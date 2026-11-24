"""Classifier text preprocessing shared by train_v0.py and evaluate.py.

Encoder versions (stored as "encoder_version" in each model's training report;
reports without the key are version 1):
  1 = v0/v1a/v1b behavior: long inputs end in a doubled </s>. Kept for compatibility.
  2 = correct head+tail: exactly one </s>. Used from v2 on.
"""

MAX_LENGTH = 512
CURRENT_VERSION = 2


def preprocessing_id(version: int) -> str:
    """Part of the evaluation cache key; changes whenever encode() output changes."""
    return f"raw-512-headtail-v{version}"


def encode(tokenizer, value: str, version: int = CURRENT_VERSION) -> dict:
    """Raw text -> token ids, keeping the head and tail of long inputs."""
    if version not in (1, 2):
        raise ValueError(f"Unknown encoder version: {version}")
    ids = tokenizer(value, add_special_tokens=True, truncation=False)["input_ids"]
    if len(ids) > MAX_LENGTH:
        keep = MAX_LENGTH - 2
        head, tail = keep // 2, keep - keep // 2
        # v1: ids[-tail:] already ends in </s>, so </s> is doubled (what v0/v1a/v1b saw).
        tail_ids = ids[-tail:] if version == 1 else ids[-1 - tail:-1]
        ids = [ids[0]] + ids[1:1 + head] + tail_ids + [ids[-1]]
    return {"input_ids": ids, "attention_mask": [1] * len(ids)}
