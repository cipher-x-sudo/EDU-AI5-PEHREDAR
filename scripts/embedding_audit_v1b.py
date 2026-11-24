"""Audit train/dev cosine leakage without changing the trained pool.

No argument: v1b (train_public + dev_public -> dev_public_v1b).
`v2`: train_public_v2 + dev_public_v2_unaudited -> dev_public_v2.
"""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path("data/processed")


def read(path):
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def write(path, rows):
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=True) + "\n")


def main():
    from sentence_transformers import SentenceTransformer
    import faiss
    import torch

    tag = sys.argv[1] if len(sys.argv) > 1 else "v1b"
    if tag == "v1b":
        train_name, dev_name = "train_public.jsonl", "dev_public.jsonl"
    else:
        train_name, dev_name = f"train_public_{tag}.jsonl", f"dev_public_{tag}_unaudited.jsonl"
    train = read(ROOT / train_name)
    dev = read(ROOT / dev_name)
    model = SentenceTransformer(
        "intfloat/multilingual-e5-small",
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
    tr = model.encode(
        ["passage: " + r["text"] for r in train],
        normalize_embeddings=True, batch_size=64, show_progress_bar=True,
    )
    dv = model.encode(
        ["query: " + r["text"] for r in dev],
        normalize_embeddings=True, batch_size=64, show_progress_bar=True,
    )
    index = faiss.IndexFlatIP(tr.shape[1])
    index.add(np.asarray(tr, dtype="float32"))
    scores, ids = index.search(np.asarray(dv, dtype="float32"), 1)
    leaks = [
        (dev[i], train[int(ids[i, 0])], float(scores[i, 0]))
        for i in range(len(dev)) if scores[i, 0] > 0.95
    ]
    groups = {row["split_group"] for d, t, _ in leaks for row in (d, t)}
    filtered = [r for r in dev if r["split_group"] not in groups]
    write(ROOT / f"dev_public_{tag}.jsonl", filtered)
    removed_rows = len(dev) - len(filtered)
    dev_groups_removed = len({r["split_group"] for r in dev if r["split_group"] in groups})
    report = Path("results/audit_v1.md")
    with report.open("a", encoding="utf-8") as stream:
        stream.write(
            f"\n## {tag} embedding audit\n\n"
            f"- Model: `intfloat/multilingual-e5-small`; cosine threshold: `>0.95`.\n"
            f"- Train rows: {len(train)}; dev rows before audit: {len(dev)}.\n"
            f"- Candidate pairs: {len(leaks)}.\n"
            f"- Leaking dev rows removed: {removed_rows}.\n"
            f"- Whole split groups involved: {len(groups)}; dev groups removed: {dev_groups_removed}.\n"
            f"- Final dev_public_{tag} rows: {len(filtered)}.\n"
            f"- `{train_name}` was not modified; leaking groups are removed from dev only.\n"
        )
    print(json.dumps({"tag": tag, "train": len(train), "candidate_pairs": len(leaks),
                      "groups": len(groups), "dev_groups_removed": dev_groups_removed,
                      "removed_rows": removed_rows, "final_dev": len(filtered)}))


if __name__ == "__main__":
    main()
