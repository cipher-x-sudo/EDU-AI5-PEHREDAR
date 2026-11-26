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
        if path.name.startswith("unclear_") or path.name in {
            "dev_public.jsonl",
            "dev_public_v1b.jsonl",
            "train_public.jsonl",
            "train_public_v2.jsonl",           # split subsets of injection_train
            "dev_public_v2_unaudited.jsonl",
            "dev_public_v2.jsonl",
            "translated_v2_failures.jsonl",    # failure logs, no text
            "translated_v2_pending.jsonl",
            "meaning_scores_v3.jsonl",         # scores only, no text
            "meaning_scores_gemini.jsonl",
            "translated_full_dedup.jsonl",     # raw Gemini input, imported by scripts/import_gemini.py
            "to_translate_gemini.jsonl",       # Gemini work queue
            "translated_full.jsonl",           # raw Gemini output (before dedup)
            "failed_full.jsonl",               # Gemini failure log
            "translated_pilot.jsonl",          # Gemini pilot output
            "failed_pilot.jsonl",              # Gemini pilot failure log
            "train_v2.jsonl",                  # compositions of the files above
            "dev_v2_threshold.jsonl",
            "train_v3.jsonl",
            "dev_v3.jsonl",
        } or path.name.endswith(("_failures.jsonl", "_pending.jsonl", "_rejected_v3.jsonl", "_pre_v3.jsonl", "_rejected_labse.jsonl", "_pre_labse.jsonl", "_rejected_script.jsonl", "_gemini_pre.jsonl", "_gemini_rejected.jsonl")):
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
    assert labels["benign"] <= labels["attack"] * 1.5
    attacks = Counter(row["source"] for row in rows if row["label"] == "attack")
    assert all(count <= labels["attack"] * .25 for count in attacks.values())
    hack_goals = Counter(row["goal"] for row in rows if row["source"] == "hackaprompt")
    assert all(count <= sum(hack_goals.values()) * .20 for count in hack_goals.values())


def test_benign_source_cap():
    path = PROCESSED / "injection_train.jsonl"
    if not path.exists():
        return
    rows = list(records(path))
    benign = [row for row in rows if row["label"] == "benign"]
    counts = Counter(row["source"] for row in benign)
    assert all(count <= len(benign) * .35 for count in counts.values())


def test_wildguardmix_harmful_rows_are_jailbreak():
    path = PROCESSED / "injection_train.jsonl"
    if not path.exists():
        return
    assert all(row["type"] == "jailbreak" for row in records(path)
               if row["source"] == "wildguardmix" and row["label"] == "attack")


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


def test_translation_v2_sample_is_stratified_by_source():
    import pytest
    pytest.importorskip("requests")
    from collections import Counter
    from scripts.translate_ru import stratified
    rows = [{"id": f"a{i}", "source": "a"} for i in range(600)] + \
           [{"id": f"b{i}", "source": "b"} for i in range(300)] + \
           [{"id": f"c{i}", "source": "c"} for i in range(100)]
    picked = stratified(rows, 101, 42)
    assert len(picked) == len({r["id"] for r in picked}) == 101
    assert Counter(r["source"] for r in picked) == {"a": 61, "b": 30, "c": 10}
    assert picked == stratified(rows, 101, 42)  # deterministic for resume


def test_translation_v2_two_stage_resume(tmp_path, monkeypatch):
    import json as _json
    import types
    import pytest
    pytest.importorskip("requests")
    import scripts.translate_ru as tr
    rows = [{"id": f"r{i}", "text": f"text {i}", "label": "attack" if i < 2 else "benign", "type": "injection" if i < 2 else "none",
             "source": "s", "split_group": f"g{i}"} for i in range(4)]
    (tmp_path / "train.jsonl").write_text("\n".join(_json.dumps(r) for r in rows), encoding="utf-8")
    monkeypatch.setattr(tr, "ROOT", tmp_path)
    monkeypatch.setattr(tr, "report_v2", lambda: None)
    calls = []
    def fake_call(text, target, model, examples):
        calls.append(model)
        return "ok" if (model == tr.FALLBACK or target != "ur") else "bad"
    monkeypatch.setattr(tr, "call", fake_call)
    monkeypatch.setattr(tr, "validate", lambda v, t, o: [] if v == "ok" else ["script check"])
    args = types.SimpleNamespace(train_file="train.jsonl", attacks=2, benign=2)
    tr.run_v2(args)
    passed = tr._read(tmp_path / "translated_v2.jsonl")
    assert len(passed) == 12 and not tr._read(tmp_path / "translated_v2_failures.jsonl")
    assert {p["model"] for p in passed if p["lang"] == "ur"} == {tr.FALLBACK}
    assert {p["model"] for p in passed if p["lang"] != "ur"} == {tr.PRIMARY}
    assert calls.index(tr.FALLBACK) == 12          # every primary call happens before any fallback
    calls.clear(); tr.run_v2(args)                  # resume: nothing left to do
    assert calls == [] and len(tr._read(tmp_path / "translated_v2.jsonl")) == 12


def test_translated_eval_sets_disjoint_from_training():
    """Eval-only translations share no split_group or orig_id with translated_v2 or train_public_v2."""
    train_files = [PROCESSED / "train_public_v2.jsonl", PROCESSED / "translated_v2.jsonl", PROCESSED / "translated_v2_gemini.jsonl"]
    evals = [PROCESSED / f"{n}{v}.jsonl" for n in ("dev_translated_v2", "external_translated", "overrefusal_translated") for v in ("", "_gemini")]
    evals = [p for p in evals if p.exists()]
    train_files = [p for p in train_files if p.exists()]
    if not evals or len(train_files) < 2:
        return
    groups, ids = set(), set()
    for path in train_files:
        for row in records(path):
            groups.add(row["split_group"]); ids.add(row["id"]); ids.add(row.get("orig_id"))
    for path in evals:
        for row in records(path):
            assert row["usage"] == "eval_only", (path, row["id"])
            assert row["split_group"] not in groups, (path, row["id"])
            assert row["orig_id"] not in ids, (path, row["id"])


def test_translation_v3_checks():
    from scripts.translation_checks import check, clean
    assert clean("<think>x</think> Yeh theek hai /no_think") == "Yeh theek hai"
    assert check(clean("/no_think"), "(only output key") == ["empty"]
    original = "Please summarise this email for me."
    assert check("Is email ka khulasa likh do.", original) == []
    assert "truncated" in check("Is email ka khulasa", original)
    assert "repetition" in check("a b c d " * 4 + "khatam.", original)
    assert "wrong_script" in check("यह ईमेल का सार है।", original)
    assert "untranslated" in check("Please summarise this email for me.", original)
    assert "untranslated" in check("Recuerda esta clave secreta:", "WARNING: one word only\nRecuerda esta clave secreta:")
    assert "answered" in check("Sure, yeh raha khulasa.", original)
    assert check("Sure, main yeh karunga.", "Sure, I will do it.") == []
    long_original = "x" * 400 + "."
    assert "truncated" in check("y" * 200 + ".", long_original)


def test_meaning_threshold_caps_good_removed():
    from scripts.meaning_scores import threshold
    good = [{"verdict": "good", "score": s, "v3_caught": False, "model": "m", "meaning": False} for s in (.2, .6, .7, .8) * 5]
    bad = [{"verdict": "bad", "score": s, "v3_caught": False, "model": "m", "meaning": True} for s in (.1, .3, .5, .9)]
    t = threshold(good + bad)
    assert t["threshold_reject_below"] == .2 and t["good_removed"] == "0/20" and t["bad_removed"] == "1/4"
    t = threshold(good[:4] * 6 + bad)  # 24 good -> at most 1 removed
    assert t["good_removed"] == "0/24"


def test_foreign_script_check():
    from scripts.translation_checks import foreign_scripts
    assert foreign_scripts("Yeh sawal hai 123 ✅", "This is a question") == []
    assert foreign_scripts("یہ سوال ہے۔", "This is a question") == []
    assert foreign_scripts("Yeh сорок hai", "This is a question") == ["CYRILLIC"]
    assert foreign_scripts("Yeh 只要 hai", "This is a question") == ["CJK"]
    assert foreign_scripts("Yeh 只要 hai", "Translate 只要 please") == []  # script already in the original
