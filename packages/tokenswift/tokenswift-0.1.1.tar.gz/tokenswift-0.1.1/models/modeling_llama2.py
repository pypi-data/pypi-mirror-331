from typing import Optional

import math
import torch
from torch import nn

from transformers.activations import ACT2FN
from transformers.models.llama.modeling_llama import PreTrainedModel, ACT2FN

from models.llama_config import LlamaConfig
from models.cache import Cache, FlashSimpleCache, RetrievalCache


def _make_causal_mask(
    input_ids_shape: torch.Size, dtype: torch.dtype, device: torch.device, past_key_values_length: int = 0
):
    bsz, tgt_len = input_ids_shape
    mask = torch.tril(torch.ones((tgt_len, tgt_len), device=device, dtype=dtype))

    if past_key_values_length > 0:
        mask = torch.cat([torch.ones(tgt_len, past_key_values_length, dtype=dtype, device=device), mask], dim=-1)
    return mask[None, None, :, :].expand(bsz, 1, tgt_len, tgt_len + past_key_values_length)


class LlamaRMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)


class LlamaMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size
        self.gate_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=False)
        self.act_fn = ACT2FN[config.hidden_act]

    def forward(self, x):
        down_proj = self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))

        return down_proj


class LlamaRotaryEmbedding(nn.Module):
    def __init__(self, dim, max_position_embeddings=2048, base=10000, device=None):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float().to(device) / self.dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)

        self._set_cos_sin_cache(
            seq_len=max_position_embeddings, device=self.inv_freq.device, dtype=torch.get_default_dtype()
        )

    def _set_cos_sin_cache(self, seq_len, device, dtype):
        self.max_seq_len_cached = seq_len
        t = torch.arange(self.max_seq_len_cached, device=device, dtype=self.inv_freq.dtype)

        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos().to(dtype), persistent=False)
        self.register_buffer("sin_cached", emb.sin().to(dtype), persistent=False)

    def forward(self, x, seq_len=None):
        return (
            self.cos_cached.to(dtype=x.dtype),
            self.sin_cached.to(dtype=x.dtype),
        )


def _yarn_get_mscale(scale=1):
    if scale <= 1:
        return 1.0
    return 0.1 * math.log(scale) + 1.0


def _yarn_find_correction_dim(num_rotations, dim, base=10000, max_position_embeddings=2048):
    return (dim * math.log(max_position_embeddings / (num_rotations * 2 * math.pi))) / (2 * math.log(base))


def _yarn_find_correction_range(low_rot, high_rot, dim, base=10000, max_position_embeddings=2048):
    low = math.floor(_yarn_find_correction_dim(low_rot, dim, base, max_position_embeddings))
    high = math.ceil(_yarn_find_correction_dim(high_rot, dim, base, max_position_embeddings))
    return max(low, 0), min(high, dim - 1)  # Clamp values just in case


def _yarn_linear_ramp_mask(min, max, dim):
    if min == max:
        max += 0.001  # Prevent singularity

    linear_func = (torch.arange(dim, dtype=torch.float32) - min) / (max - min)
    ramp_func = torch.clamp(linear_func, 0, 1)
    return ramp_func


class LlamaYaRNRotaryEmbedding(nn.Module):
    def __init__(
        self,
        dim=128,
        max_position_embeddings=131072,
        base=10000,
        scaling_factor=32.0,
        pos_idx_in_fp32=True,
        original_max_position_embeddings=4096,
        extrapolation_factor=1,
        attn_factor=1,
        beta_fast=32,
        beta_slow=1,
        device=None,
    ):
        super().__init__()

        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        self.device = device
        self.scaling_factor = scaling_factor
        self.pos_idx_in_fp32 = pos_idx_in_fp32
        self.original_max_position_embeddings = (
            original_max_position_embeddings if original_max_position_embeddings else max_position_embeddings
        )
        self.extrapolation_factor = extrapolation_factor
        self.attn_factor = attn_factor
        self.beta_fast = beta_fast
        self.beta_slow = beta_slow
        self.mscale = float(_yarn_get_mscale(self.scaling_factor) * attn_factor)
        # compute inverse frequency
        self._compute_inv_freq(self.scaling_factor, device)

    def _compute_inv_freq(self, scaling_factor, device=None):
        pos_freqs = self.base ** (torch.arange(0, self.dim, 2).float().to(device) / self.dim)
        inv_freq_extrapolation = 1.0 / pos_freqs
        inv_freq_interpolation = 1.0 / (scaling_factor * pos_freqs)

        low, high = _yarn_find_correction_range(
            self.beta_fast, self.beta_slow, self.dim, self.base, self.original_max_position_embeddings
        )
        inv_freq_mask = (
            1 - _yarn_linear_ramp_mask(low, high, self.dim // 2).float().to(device)
        ) * self.extrapolation_factor  # Get n-d rotational scaling corrected for extrapolation
        inv_freq = inv_freq_interpolation * (1 - inv_freq_mask) + inv_freq_extrapolation * inv_freq_mask
        self.register_buffer("inv_freq", inv_freq, persistent=False)

        # Build here to make `torch.jit.trace` work.
        self._set_cos_sin_cache(seq_len=self.max_position_embeddings, device=self.inv_freq.device)

    def _set_cos_sin_cache(self, seq_len, device):
        self.max_seq_len_cached = seq_len
        if self.pos_idx_in_fp32:
            dtype = torch.float32
        else:
            dtype = torch.float16
        t = torch.arange(self.max_seq_len_cached, device=device, dtype=dtype)
        if self.inv_freq.dtype != dtype:
            self.inv_freq = self.inv_freq.to(dtype)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", (emb.cos() * self.mscale).to(torch.float16), persistent=False)
        self.register_buffer("sin_cached", (emb.sin() * self.mscale).to(torch.float16), persistent=False)

    def forward(self, x, seq_len=None):
        return (
            self.cos_cached.to(dtype=x.dtype),
            self.sin_cached.to(dtype=x.dtype),
        )


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Rotates half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    """Applies Rotary Position Embedding to the query and key tensors.

    Args:
        q (`torch.Tensor`): The query tensor.
        k (`torch.Tensor`): The key tensor.
        cos (`torch.Tensor`): The cosine part of the rotary embedding.
        sin (`torch.Tensor`): The sine part of the rotary embedding.
        position_ids (`torch.Tensor`, *optional*):
            Deprecated and unused.
        unsqueeze_dim (`int`, *optional*, defaults to 1):
            The 'unsqueeze_dim' argument specifies the dimension along which to unsqueeze cos[position_ids] and
            sin[position_ids] so that they can be properly broadcasted to the dimensions of q and k. For example, note
            that cos[position_ids] and sin[position_ids] have the shape [batch_size, seq_len, head_dim]. Then, if q and
            k have the shape [batch_size, heads, seq_len, head_dim], then setting unsqueeze_dim=1 makes
            cos[position_ids] and sin[position_ids] broadcastable to the shapes of q and k. Similarly, if q and k have
            the shape [batch_size, seq_len, heads, head_dim], then set unsqueeze_dim=2.
    Returns:
        `tuple(torch.Tensor)` comprising of the query and key tensors rotated using the Rotary Position Embedding.
    """
    cos = cos[position_ids].unsqueeze(unsqueeze_dim)
    sin = sin[position_ids].unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


class LlamaAttention(nn.Module):
    def __init__(self, config: LlamaConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.hidden_size // self.num_heads
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings = config.max_position_embeddings
        self.rope_theta = config.rope_theta
        self.attention_dropout = config.attention_dropout

        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=config.attention_bias)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=config.attention_bias)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=config.attention_bias)

        self._init_rope()

    def _init_rope(self):
        if self.config.rope_scaling is None:
            self.rotary_emb = LlamaRotaryEmbedding(
                self.head_dim,
                max_position_embeddings=self.max_position_embeddings,
                base=self.rope_theta,
            )
        else:
            scaling_type = self.config.rope_scaling["type"]
            scaling_factor = self.config.rope_scaling["factor"]
            if scaling_type == "yarn":
                original_max_position_embeddings = self.config.rope_scaling["original_max_position_embeddings"]
                self.rotary_emb = LlamaYaRNRotaryEmbedding(
                    self.head_dim,
                    base=10000,
                    scaling_factor=scaling_factor,
                    max_position_embeddings=self.max_position_embeddings,
                    original_max_position_embeddings=original_max_position_embeddings,
                )
            else:
                raise ValueError(f"Unknown RoPE scaling type {scaling_type}")

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        kv_cache: Optional[FlashSimpleCache] = None,
        retri_cache: Optional[RetrievalCache] = None,
        spec: bool = False,
    ) -> torch.Tensor:
        bsz, q_len, _ = hidden_states.size()

        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)

        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)

        cos, sin = self.rotary_emb(value_states, position_ids)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, position_ids)

        if spec:
            if kv_cache is not None:
                key_states, value_states = kv_cache.get_full_kv(
                    key_states=key_states, value_states=value_states, layer_idx=self.layer_idx
                )
            elif retri_cache is not None:
                key_states, value_states = retri_cache.spec_update(
                    new_k_cache=key_states, new_v_cache=value_states, layer_idx=self.layer_idx
                )
            else:
                raise NotImplementedError("kv cache and retri cache is all None")

        else:
            # update kv cache
            key_states, value_states = kv_cache.update(key_states, value_states, layer_idx=self.layer_idx)

            if (retri_cache is not None) and (retri_cache.update_prefill):
                retri_cache.init_retri_cache(kv_cache, query_states, self.layer_idx)

                if self.layer_idx == self.config.num_hidden_layers - 1:
                    retri_cache.update_prefill = False
                    print(f"\nretri_cache update_prefill, kv_cache len is {kv_cache.seq_len}\n")

        attn_output = torch.nn.functional.scaled_dot_product_attention(
            query=query_states, key=key_states, value=value_states, attn_mask=attention_mask
        )
        attn_output = attn_output.transpose(1, 2)

        attn_output = attn_output.reshape(bsz, q_len, self.hidden_size).contiguous()
        attn_output = self.o_proj(attn_output)

        return attn_output


class LlamaDecoderLayer(nn.Module):
    def __init__(self, config: LlamaConfig, layer_idx: int):
        super().__init__()
        self.hidden_size = config.hidden_size

        self.self_attn = LlamaAttention(config=config, layer_idx=layer_idx)

        self.mlp = LlamaMLP(config)
        self.input_layernorm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        kv_cache: Optional[Cache] = None,
        retri_cache: Optional[Cache] = None,
        spec: bool = False,
    ):

        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)

        # Self Attention
        hidden_states = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            position_ids=position_ids,
            kv_cache=kv_cache,
            retri_cache=retri_cache,
            spec=spec,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        return hidden_states


class LlamaPreTrainedModel(PreTrainedModel):
    config_class = LlamaConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["LlamaDecoderLayer"]
    _skip_keys_device_placement = ["past_key_values"]
    _supports_flash_attn_2 = True
    _supports_sdpa = True
    _supports_cache_class = True

    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()


class MedusaModel(nn.Module):
    def __init__(self, config: LlamaConfig):
        super().__init__()
        self.linear = nn.Linear(config.hidden_size, config.hidden_size, bias=False)
        self.input_layernorm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_layernorm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def forward(
        self,
        hidden_states: torch.Tensor,
    ):

        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states = self.linear(hidden_states)
        hidden_states = residual + hidden_states

        norm_hidden_states = self.post_layernorm(hidden_states)

        return hidden_states, norm_hidden_states


class LlamaModel(LlamaPreTrainedModel):
    def __init__(self, config: LlamaConfig):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size

        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size, self.padding_idx)
        self.layers = nn.ModuleList(
            [LlamaDecoderLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)]
        )
        self.norm = LlamaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

        self.medusa_layers = nn.ModuleList([MedusaModel(config) for _ in range(config.medusa_heads)])

        self.gradient_checkpointing = False
        self.post_init()

    def forward(
        self,
        input_ids: torch.LongTensor,
        inputs_embeds: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        kv_cache: Optional[Cache] = None,
        retri_cache: Optional[Cache] = None,
        spec: bool = False,
        past_kv_len: int = -1,
        medusa_mask: Optional[torch.Tensor] = None,
    ):
        batch_size, seq_length = input_ids.shape[:2]

        if (position_ids is None) and ((kv_cache is not None) or (past_kv_len != -1)):
            # for verification
            device = input_ids.device if input_ids is not None else inputs_embeds.device
            past_kv_len = kv_cache.seq_len if kv_cache is not None else past_kv_len
            position_ids = torch.arange(past_kv_len, past_kv_len + seq_length, dtype=torch.long, device=device)
            position_ids = position_ids.unsqueeze(0)

        inputs_embeds = self.embed_tokens(input_ids)
        hidden_states = inputs_embeds

        if (attention_mask is None) and (kv_cache is not None):
            attention_mask = self._prepare_decoder_attention_mask(
                input_shape=input_ids.shape,
                inputs_embeds=hidden_states,
                past_key_values_length=kv_cache.seq_len,
                medusa_mask=medusa_mask,
            )

        for decoder_layer in self.layers:
            layer_outputs = decoder_layer(
                hidden_states,
                attention_mask=attention_mask,
                position_ids=position_ids,
                kv_cache=kv_cache,
                retri_cache=retri_cache,
                spec=spec,
            )

            hidden_states = layer_outputs

        ori_hidden_states = self.norm(hidden_states)
        if not spec:
            return ori_hidden_states

        hidden_states_list = []
        hidden_states_list.append(ori_hidden_states)

        for m_layer in self.medusa_layers:
            hidden_states, norm_hidden_states = m_layer(hidden_states)
            hidden_states_list.append(norm_hidden_states)

        return hidden_states_list

    def _prepare_decoder_attention_mask(self, input_shape, inputs_embeds, past_key_values_length, medusa_mask):
        # create causal mask
        # [bsz, seq_len] -> [bsz, 1, tgt_seq_len, src_seq_len]
        combined_attention_mask = None
        if input_shape[-1] > 1:
            combined_attention_mask = _make_causal_mask(
                input_shape,
                inputs_embeds.dtype,
                device=inputs_embeds.device,
                past_key_values_length=past_key_values_length,
            )
        else:
            bsz, tgt_len = input_shape
            return torch.ones(
                [bsz, 1, tgt_len, tgt_len + past_key_values_length],
                dtype=inputs_embeds.dtype,
                device=inputs_embeds.device,
            )

        # [MODIFIED] add medusa mask
        if medusa_mask is not None:
            medusa_len = medusa_mask.size(-1)
            combined_attention_mask[:, :, -medusa_len:, -medusa_len:][medusa_mask == 0] = 0
            if hasattr(self, "medusa_mode"):
                # debug mode
                if self.medusa_mode == "debug":
                    torch.save(combined_attention_mask, "medusa_mask.pt")

        combined_attention_mask = combined_attention_mask.to(torch.bool)

        return combined_attention_mask


class LlamaForCausalLM(LlamaPreTrainedModel):
    _tied_weights_keys = ["lm_head.weight"]

    def __init__(self, config: LlamaConfig):
        super().__init__(config)
        self.model = LlamaModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.post_init()

    def forward(
        self,
        input_ids: torch.LongTensor,
        inputs_embeds: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        kv_cache: Optional[Cache] = None,
        retri_cache: Optional[Cache] = None,
        spec: bool = False,
        past_kv_len: int = -1,
        medusa_mask: torch.Tensor = None,
    ):

        outputs = self.model(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            position_ids=position_ids,
            kv_cache=kv_cache,
            retri_cache=retri_cache,
            spec=spec,
            past_kv_len=past_kv_len,
            medusa_mask=medusa_mask,
        )

        hidden_states = outputs
        logits = self.lm_head(hidden_states)
        logits = logits.float()

        return logits
