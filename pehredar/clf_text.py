"""Classifier text preprocessing shared by train_v0.py and evaluate.py."""

# Bump when encode() or the text fed to it changes; part of the evaluation cache key.
PREPROCESSING_VERSION = "raw-512-headtail-v1"
MAX_LENGTH = 512


def encode(tokenizer, value: str) -> dict:
    """Raw text -> token ids, keeping the head and tail of long inputs."""
    ids = tokenizer(value, add_special_tokens=True, truncation=False)["input_ids"]
    if len(ids) > MAX_LENGTH:
        keep = MAX_LENGTH - 2
        head, tail = keep // 2, keep - keep // 2
        # Byte-for-byte what v0/v1a/v1b were trained on: ids[-tail:] already ends in
        # </s>, so long inputs end in "</s></s>". Changing this needs retraining.
        ids = [ids[0]] + ids[1:1 + head] + ids[-tail:] + [ids[-1]]
    return {"input_ids": ids, "attention_mask": [1] * len(ids)}
