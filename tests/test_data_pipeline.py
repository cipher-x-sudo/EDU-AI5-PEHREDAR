import json
from collections import Counter
from pathlib import Path

from scripts.unify import norm


PROCESSED = Path("data/processed")
REQUIRED = {"id", "text", "lang", "label", "type", "source", "split_group",
            "usage", "redistributable", "license", "turns", "orig_label"}


def records(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def test_processed_schema_and_unique_ids():
    if not PROCESSED.exists():
        return
    ids = set()
    for path in PROCESSED.glob("*.jsonl"):
        if path.name.startswith("unclear_"):
            continue
        for row in records(path):
            assert REQUIRED <= row.keys(), (path, row.get("id"))
            assert isinstance(row["text"], str) and 3 <= len(row["text"]) <= 4000
            assert row["label"] in {"attack", "benign"}
            assert row["lang"] in {"en", "ur", "roman_ur", "mixed", "other"}
            assert row["usage"] in {"train", "secondary_eval", "eval_only"}
            assert isinstance(row["redistributable"], bool)
            assert row["id"] not in ids
            ids.add(row["id"])
            if row["turns"] is not None:
                assert all(turn["role"] in {"user", "assistant", "system"} and
                           isinstance(turn["content"], str) for turn in row["turns"])


def test_training_excludes_frozen_exact_and_normalized_text():
    frozen = Path("data/frozen_test/human_v1.jsonl")
    if not frozen.exists() or not PROCESSED.exists():
        return
    held_out = {row["text"] for row in records(frozen)}
    normalized = {norm(text) for text in held_out}
    for path in PROCESSED.glob("*.jsonl"):
        for row in records(path):
            if row.get("usage") == "train":
                assert row["text"] not in held_out, (path, row["id"])
                assert norm(row["text"]) not in normalized, (path, row["id"])


def test_injection_pool_balance_and_source_cap():
    path = PROCESSED / "injection_train.jsonl"
    if not path.exists():
        return
    rows = list(records(path))
    labels = Counter(row["label"] for row in rows)
    assert labels["attack"] == labels["benign"]
    attacks = Counter(row["source"] for row in rows if row["label"] == "attack")
    assert all(count <= labels["attack"] * .35 for count in attacks.values())
