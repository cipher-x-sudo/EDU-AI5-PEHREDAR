"""Audit public classifier rows without opening sealed human datasets."""
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("data/processed")


def rows(name):
    with (ROOT / name).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def normalized(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def audit():
    pool = rows("injection_train.jsonl")
    train = rows("train_public.jsonl")
    dev = rows("dev_public.jsonl")
    assert {r["id"] for r in pool} == {r["id"] for r in train + dev}
    assert not ({r["split_group"] for r in train} & {r["split_group"] for r in dev})
    train_by_hash = defaultdict(list)
    for row in train:
        train_by_hash[normalized(row["text"])].append(row["id"])
    exact = [(row["id"], train_by_hash[normalized(row["text"])])
             for row in dev if normalized(row["text"]) in train_by_hash]
    strata = Counter((r["source"], r["label"], r["type"], r["lang"]) for r in pool)
    by_source_label = defaultdict(list)
    for row in pool:
        by_source_label[row["source"], row["label"]].append(row)
    rng = random.Random(42)
    sample = [r for key in sorted(by_source_label)
              for r in rng.sample(by_source_label[key], min(30, len(by_source_label[key])))]
    suspicious = []
    for row in sample:
        reason = None
        if row["source"] == "jailbreak_llms":
            text = normalized(row["text"])
            if row["label"] == "benign" and any(x in text for x in
                    ("ignore previous instructions", "ignore all previous instructions",
                     "jailbreak", "bypass safety")):
                reason = "Benign row contains an explicit jailbreak cue; review source label"
        if row["source"] == "spml" and not row.get("system_prompt"):
            reason = "Missing paired system prompt"
        if reason:
            suspicious.append((row["id"], reason))
    out = Path("results")
    out.mkdir(exist_ok=True)
    lines = [
        "# Public classifier audit v1", "",
        "The sealed human frozen set and any human dev set were not opened or evaluated.",
        "Scope: public classifier pool before the public 10% dev split.", "",
        "## Counts by source × label × type × lang", "",
        "Source | Label | Type | Lang | Rows", "---|---|---|---|---:",
    ]
    lines += [f"{' | '.join(k)} | {v}" for k, v in sorted(strata.items())]
    lines += ["", "## Label review", "",
              f"Deterministic random sample: {len(sample)} rows, up to 30 per source and label (seed 42).",
              "The sample IDs are listed below for manual review. Automated cue checks are triage, not label adjudication.",
              "",
              "Source | Label | Sample IDs", "---|---|---"]
    for key in sorted(by_source_label):
        sampled = [r["id"] for r in sample if (r["source"], r["label"]) == key]
        lines.append(f"{key[0]} | {key[1]} | {', '.join(sampled)}")
    lines += ["", "Potential label issues requiring human review:", ""]
    lines += [f"- `{ident}`: {reason}." for ident, reason in suspicious] or ["- No automatic cue flags in this sample. Human semantic review remains required."]
    spml = [r for r in pool if r["source"] == "spml"]
    lines += ["", "## SPML", "",
              f"{len(spml)} selected rows use `text` = User Prompt as classifier input; "
              "`system_prompt` stores the paired System Prompt. "
              "`orig_label` 1 maps to attack and 0 to benign.",
              "The source label is context dependent, so prompt-only training can introduce label noise.",
              "", "## Leakage", "",
              f"Shared split groups across public train/dev: 0. Normalized exact text overlaps: {len(exact)}.",
              "Embedding cosine results are recorded separately when multilingual-e5-small is available.",
              "The pipeline did not open sealed human data. Its contents therefore cannot be compared in this task.",
              ""]
    (out / "audit_v1.md").write_text("\n".join(lines), encoding="utf-8")
    return len(pool), len(train), len(dev), len(sample), len(suspicious), len(exact)


if __name__ == "__main__":
    print(audit())
