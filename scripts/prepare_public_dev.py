"""Repair SPML representation and make a group-disjoint public dev split.

This script never opens data/frozen_test or any human development set.
"""
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("data/processed")


def read(path):
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def write(path, rows):
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=True) + "\n")


def prepare(seed=42):
    source = ROOT / "injection_train.jsonl"
    rows = read(source)
    for row in rows:
        if row["source"] != "spml" or "system_prompt" in row:
            continue
        system, marker, prompt = row["text"].partition("\nUser: ")
        if not marker or not system.startswith("System: "):
            raise ValueError(f"Unexpected SPML representation: {row['id']}")
        row["system_prompt"] = system.removeprefix("System: ")
        row["text"] = prompt
        normalized = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", prompt).casefold()).strip()
        row["split_group"] = hashlib.sha256(normalized.encode()).hexdigest()[:20]
    # Keep all normalized exact twins in the same group, even across sources.
    canonical = {}
    for row in rows:
        key = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", row["text"]).casefold()).strip()
        canonical.setdefault(key, row["split_group"])
        row["split_group"] = canonical[key]

    # Assign whole groups globally. Source/label strata define dev targets.
    strata = Counter((r["source"], r["label"]) for r in rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["split_group"]].append(row)
    candidates = list(grouped)
    random.Random(seed).shuffle(candidates)
    targets = {key: round(count * .10) for key, count in strata.items()}
    selected = set()
    progress = Counter()
    for key in candidates:
        contribution = Counter((r["source"], r["label"]) for r in grouped[key])
        if any(progress[k] + n <= targets[k] for k, n in contribution.items()):
            selected.add(key)
            progress.update(contribution)
    train = [r for r in rows if r["split_group"] not in selected]
    dev = [r for r in rows if r["split_group"] in selected]
    assert {r["split_group"] for r in train}.isdisjoint(r["split_group"] for r in dev)
    write(ROOT / "train_public.jsonl", train)
    write(ROOT / "dev_public.jsonl", dev)
    return {"pool": len(rows), "train": len(train), "dev": len(dev),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "strata": {f"{s}/{label}": {"pool": count, "dev": progress[s, label]}
                       for (s, label), count in sorted(strata.items())}}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
