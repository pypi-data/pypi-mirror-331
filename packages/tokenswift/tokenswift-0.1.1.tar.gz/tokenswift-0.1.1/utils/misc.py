import os

from typing import List
from termcolor import colored
from transformers import PreTrainedTokenizer


def rank0_print(*args, **kwargs):
    if int(os.environ.get("LOCAL_RANK", "0")) == 0:
        print(*args, **kwargs)


def spec_stream(pred_token_idx: List[int], tokenizer: PreTrainedTokenizer, color: str = "blue"):
    decoded_token = tokenizer.decode(
        pred_token_idx,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
        # spaces_between_special_tokens=False,
    )

    decoded_token = decoded_token.replace("<0x0A>", "\n")

    rank0_print(colored(decoded_token, color), flush=True, end=" ")


def log_csv(file_path, header, entry):
    try:
        with open(file_path, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = ""

    if not contents:
        with open(file_path, "a") as f:
            f.write(header)
            f.flush()

    with open(file_path, "a") as f:
        f.write(entry)
        f.flush()


def print_config(target, prefill_len, gen_len, gamma, file_path, method, sample_args=None, spec_args=None):
    rank0_print(
        colored("####################################### Config #######################################", "blue"),
        flush=True,
    )
    rank0_print(colored(f"Method: {method}", "red"), flush=True)
    rank0_print(colored(f"Spec Args: {spec_args}", "blue"), flush=True)
    rank0_print(colored(f"Target: {target.config._name_or_path}", "blue"), flush=True)
    rank0_print(colored(f"Prefill Length: {prefill_len}", "blue"), flush=True)
    rank0_print(colored(f"Generation Length: {gen_len}", "blue"), flush=True)
    rank0_print(colored(f"Gamma: {gamma}", "blue"), flush=True)
    rank0_print(colored(f"Sampling Args: {sample_args}", "blue"), flush=True)
    rank0_print(colored(f"Log CSV: {file_path}", "blue"), flush=True)
    rank0_print(
        colored("######################################################################################\n", "blue"),
        flush=True,
    )
