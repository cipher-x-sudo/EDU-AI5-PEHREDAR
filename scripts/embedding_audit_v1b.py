"""Audit train/dev cosine leakage without changing the trained pool."""
import json
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

    train = read(ROOT / "train_public.jsonl")
    dev = read(ROOT / "dev_public.jsonl")
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
    write(ROOT / "dev_public_v1b.jsonl", filtered)
    report = Path("results/audit_v1.md")
    with report.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n## v1b embedding audit\n\n"
            f"- Model: `intfloat/multilingual-e5-small`; cosine threshold: `>0.95`.\n"
            f"- Candidate pairs: {len(leaks)}.\n"
            f"- Leaking dev rows removed: {sum(r['split_group'] in groups for r in dev)}.\n"
            f"- Whole split groups removed: {len(groups)}.\n"
            f"- Final dev_public_v1b rows: {len(filtered)}.\n"
            "- `train_public.jsonl` was not modified because v1b is already trained.\n"
        )
    print(json.dumps({"candidate_pairs": len(leaks), "groups": len(groups),
                      "removed_rows": len(dev) - len(filtered), "final_dev": len(filtered)}))


if __name__ == "__main__":
    main()
