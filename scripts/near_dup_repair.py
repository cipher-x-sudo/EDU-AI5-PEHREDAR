"""Remove dev groups that are string near-duplicates of train rows (check_split criteria).

Usage: python -m scripts.near_dup_repair v2   (rewrites data/processed/dev_public_v2.jsonl)
"""
import json
import sys
from pathlib import Path

from pehredar.dataset import load_jsonl, near_duplicate_pairs
from pehredar.normalizer import normalize_text

ROOT = Path("data/processed")


def main(tag):
    train_path, dev_path = ROOT / f"train_public_{tag}.jsonl", ROOT / f"dev_public_{tag}.jsonl"
    key = lambda r: normalize_text(r.input_text()).casefold()
    train = {key(r): r.id for r in load_jsonl(train_path)}
    dev_records = load_jsonl(dev_path)
    pairs = near_duplicate_pairs(train, {key(r): r.id for r in dev_records})
    leak_ids = {test_id for _, test_id in pairs}
    groups = {r.split_group for r in dev_records if r.id in leak_ids}
    raw = [json.loads(x) for x in dev_path.open(encoding="utf-8") if x.strip()]
    kept = [r for r in raw if r["split_group"] not in groups]
    with dev_path.open("w", encoding="utf-8") as stream:
        for row in kept:
            stream.write(json.dumps(row, ensure_ascii=True) + "\n")
    with Path("results/audit_v1.md").open("a", encoding="utf-8") as stream:
        stream.write(f"\n## {tag} string near-duplicate repair\n\n"
                     f"- Criteria: `pehredar.dataset.near_duplicate_pairs` (same as `check_split`: ratio >= 0.93).\n"
                     f"- Train/dev pairs: {len(pairs)}; dev groups removed: {len(groups)}; "
                     f"dev rows removed: {len(raw) - len(kept)}.\n"
                     f"- Final dev_public_{tag} rows: {len(kept)}.\n")
    print(json.dumps({"pairs": len(pairs), "dev_groups_removed": len(groups),
                      "removed_rows": len(raw) - len(kept), "final_dev": len(kept)}))


if __name__ == "__main__":
    main(sys.argv[1])
