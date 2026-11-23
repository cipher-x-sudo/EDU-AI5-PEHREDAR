"""Audit and repair public train/dev leakage with multilingual-e5-small."""
import json
from pathlib import Path
import numpy as np

ROOT = Path("data/processed")

def read(path):
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]

def write(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")

def main():
    from sentence_transformers import SentenceTransformer
    import faiss
    train_path, dev_path = ROOT / "train_public.jsonl", ROOT / "dev_public.jsonl"
    train, dev = read(train_path), read(dev_path)
    model = SentenceTransformer("intfloat/multilingual-e5-small", device="cuda" if __import__("torch").cuda.is_available() else "cpu")
    tr = model.encode(["passage: " + r["text"] for r in train], normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    dv = model.encode(["query: " + r["text"] for r in dev], normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    index = faiss.IndexFlatIP(tr.shape[1]); index.add(np.asarray(tr, dtype="float32"))
    scores, ids = index.search(np.asarray(dv, dtype="float32"), 1)
    leaks = [(dev[i], train[int(ids[i, 0])], float(scores[i, 0])) for i in range(len(dev)) if scores[i, 0] > .95]
    leak_groups = {row["split_group"] for d, t, _ in leaks for row in (d, t)}
    if leak_groups:
        dev = [r for r in dev if r["split_group"] not in leak_groups]
        train = train + [r for r in read(dev_path) if r["split_group"] in leak_groups]
        write(train_path, train); write(dev_path, dev)
    report = Path("results/audit_v1.md")
    text = report.read_text(encoding="utf-8") if report.exists() else "# Public classifier audit v1\n"
    text = text.replace("Embedding cosine results are recorded separately when multilingual-e5-small is available.",
        f"Embedding model: `intfloat/multilingual-e5-small`; cosine threshold: 0.95. "
        f"Candidate train/dev near-duplicates: {len(leaks)}; whole split_groups moved: {len(leak_groups)}.")
    report.write_text(text, encoding="utf-8")
    print(json.dumps({"train": len(train), "dev": len(dev), "leaks": len(leaks), "groups_moved": len(leak_groups)}))

if __name__ == "__main__":
    main()
