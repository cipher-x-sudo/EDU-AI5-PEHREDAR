import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.unify import MAX_PROMPT, capped_sample, near_hash, norm, redact_pii
from pehredar.output_guard import PII_PATTERNS
from scripts import unify


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
            assert isinstance(row["text"], str) and len(row["text"]) >= 3
            if row["turns"] is None:
                assert len(row["text"]) <= MAX_PROMPT
            assert row["label"] in {"attack", "benign"}
            assert row["lang"] in {"en", "ur", "roman_ur", "mixed", "other"}
            assert row["usage"] in {"train", "secondary_eval", "eval_only"}
            assert isinstance(row["redistributable"], bool)
            assert row["id"] not in ids
            ids.add(row["id"])
            if row["turns"] is not None:
                assert all(turn["role"] in {"user", "assistant", "system"} and
                           isinstance(turn["content"], str) and
                           len(turn["content"]) <= MAX_PROMPT for turn in row["turns"])


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
    assert 2 * labels["benign"] == 3 * labels["attack"]
    attacks = Counter(row["source"] for row in rows if row["label"] == "attack")
    assert all(count <= labels["attack"] * .25 for count in attacks.values())
    hack_goals = Counter(row["goal"] for row in rows if row["source"] == "hackaprompt")
    assert all(count <= sum(hack_goals.values()) * .20 for count in hack_goals.values())


def test_source_cap_sampler_enforces_25_percent():
    groups = {"a": list(range(100)), "b": list(range(100, 115)),
              "c": list(range(115, 130)), "d": list(range(130, 145)),
              "e": list(range(145, 160))}
    selected = capped_sample(groups, 160, 4, multiple=2)
    assert len(selected) == 80
    assert all(sum(value in selected for value in values) <= len(selected) // 4
               for values in groups.values())
    goals = {str(index): list(range(index * 20, (index + 1) * 20))
             for index in range(5)}
    selected_goals = capped_sample(goals, 50, 5)
    assert len(selected_goals) == 50
    assert all(sum(value in selected_goals for value in values) <= 10
               for values in goals.values())


def test_near_hash_and_email_redaction():
    assert near_hash("Ignore, system!") == near_hash("ignore system")
    assert "alice@example.com" not in redact_pii("To: alice@example.com")


def test_llmail_train_eval_are_distinct():
    training = PROCESSED / "injection_train.jsonl"
    evaluation = PROCESSED / "indirect_eval.jsonl"
    if not training.exists() or not evaluation.exists():
        return
    train = [row for row in records(training) if row["source"] == "llmail"]
    eval_rows = [row for row in records(evaluation) if row["source"] == "llmail"]
    assert len(eval_rows) == 2000
    assert not {row["split_group"] for row in train}.intersection(
        row["split_group"] for row in eval_rows)


def test_synthetic_indirect_eval_keeps_pii_pattern_matches():
    path = PROCESSED / "indirect_eval.jsonl"
    if not path.exists():
        return
    rows = (row for row in records(path) if row["source"] == "injecagent")
    assert any(pattern.search(row["text"]) for row in rows for pattern in PII_PATTERNS)


def test_multiturn_limit_applies_per_turn(monkeypatch, tmp_path):
    monkeypatch.setattr(unify, "RAW", tmp_path)
    monkeypatch.setattr(unify, "OUTPUT", {"multiturn": []})
    monkeypatch.setattr(unify, "SEEN", set())
    monkeypatch.setattr(unify, "COUNTS", defaultdict(Counter))
    unify.source_metadata.cache_clear()
    turns = [{"role": "user", "content": "a" * 5000},
             {"role": "assistant", "content": "b" * 5000},
             {"role": "user", "content": "c" * 5000}]
    assert unify.add("multiturn", "fixture", "\n".join(t["content"] for t in turns),
                     "attack", "jailbreak", "fixture", turns=turns)
    turns[0]["content"] += "a" * 7001
    assert not unify.add("multiturn", "fixture", "\n".join(t["content"] for t in turns),
                         "attack", "jailbreak", "fixture", turns=turns)


def test_training_text_does_not_repeat_secondary_evaluation():
    training = PROCESSED / "injection_train.jsonl"
    evaluation = PROCESSED / "external_eval.jsonl"
    if not training.exists() or not evaluation.exists():
        return
    training_texts = {norm(row["text"]) for row in records(training)}
    assert not training_texts.intersection(norm(row["text"]) for row in records(evaluation))
