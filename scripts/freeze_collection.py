import argparse
import csv
import hashlib
import json
from pathlib import Path

from pehredar.dataset import Record
from pehredar.normalizer import normalize_text
from pehredar.output_guard import PII_PATTERNS


def freeze(source: Path, destination: Path) -> str:
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"id", "text", "lang", "label", "type", "source", "split_group",
                    "consent", "consent_reference", "author_code", "reviewer", "attack_family"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing collection columns: {sorted(required - set(reader.fieldnames or []))}")
        rows = list(reader)
    if not rows:
        raise ValueError("Collection is empty")
    records = []
    ids = set()
    texts = set()
    counts = {"attack": 0, "benign": 0}
    for line_number, row in enumerate(rows, 2):
        if row.get("consent", "").strip().lower() != "yes":
            raise ValueError(f"Row {line_number}: consent must be yes")
        if row.get("source", "").strip().lower() != "human":
            raise ValueError(f"Row {line_number}: source must be human")
        for field in ("author_code", "consent_reference", "reviewer"):
            if not row.get(field, "").strip():
                raise ValueError(f"Row {line_number}: {field} is required")
        if row.get("label", "").strip() == "attack" and not row.get("attack_family", "").strip():
            raise ValueError(f"Row {line_number}: attack_family is required for attacks")
        text = row.get("text", "").strip()
        if any(pattern.search(text) for pattern in PII_PATTERNS):
            raise ValueError(f"Row {line_number}: possible personal data")
        record = Record.model_validate({
            key: row.get(key, "").strip()
            for key in ("id", "text", "lang", "label", "type", "source", "split_group")
        })
        if record.lang != "roman_ur":
            raise ValueError(f"Row {line_number}: initial frozen set must be Roman Urdu")
        normalized = normalize_text(text).casefold()
        if record.id in ids or normalized in texts:
            raise ValueError(f"Row {line_number}: duplicate ID or text")
        ids.add(record.id)
        texts.add(normalized)
        counts[record.label] += 1
        records.append(record)
    if counts["attack"] < 50 or counts["benign"] < 50:
        raise ValueError(f"Need at least 50 attack and 50 benign records; got {counts}")
    content = "".join(json.dumps(record.model_dump(exclude_none=True), ensure_ascii=False) + "\n" for record in records)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    hash_path = destination.with_suffix(destination.suffix + ".sha256")
    if destination.exists() or hash_path.exists():
        raise FileExistsError(f"Frozen file already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    try:
        with hash_path.open("x", encoding="ascii", newline="\n") as stream:
            stream.write(f"{digest}  {destination.name}\n")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(freeze(args.source, args.destination))
