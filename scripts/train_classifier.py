import argparse
import hashlib
import json
import random
from pathlib import Path

from pehredar.dataset import assert_disjoint, grouped_split, load_jsonl
from pehredar.normalizer import VERSION, normalize_text


def train(dataset: Path, destination: Path, base_model: str, epochs: int, batch_size: int, seed: int) -> dict:
    if "frozen_test" in dataset.resolve().parts:
        raise ValueError("The frozen test set cannot be used for training")
    if destination.exists():
        raise FileExistsError(f"Model directory already exists: {destination}")
    if epochs < 1 or batch_size < 1:
        raise ValueError("epochs and batch_size must be positive")

    records = load_jsonl(dataset)
    frozen_path = dataset.parent.parent / "frozen_test" / "human_v1.jsonl"
    if frozen_path.exists():
        assert_disjoint(records, load_jsonl(frozen_path))
    training, development = grouped_split(records, seed=seed)
    for name, split in (("training", training), ("development", development)):
        if {record.label for record in split} != {"attack", "benign"}:
            raise ValueError(f"{name} split needs attack and benign examples")

    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    random.seed(seed)
    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model, num_labels=2, id2label={0: "benign", 1: "attack"},
        label2id={"benign": 0, "attack": 1},
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    class Examples(Dataset):
        def __init__(self, rows):
            self.rows = rows

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, index):
            row = self.rows[index]
            encoded = tokenizer(
                normalize_text(row.input_text()), truncation=True, max_length=256,
            )
            return {**encoded, "labels": 1 if row.label == "attack" else 0}

    def collate(items):
        labels = torch.tensor([item.pop("labels") for item in items])
        return {**tokenizer.pad(items, padding=True, return_tensors="pt"), "labels": labels}

    train_loader = DataLoader(Examples(training), batch_size=batch_size, shuffle=True, collate_fn=collate)
    dev_loader = DataLoader(Examples(development), batch_size=batch_size, collate_fn=collate)
    counts = [sum(row.label == label for row in training) for label in ("benign", "attack")]
    weights = torch.tensor([len(training) / (2 * count) for count in counts], device=device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    for _ in range(epochs):
        model.train()
        for batch in train_loader:
            batch = {key: value.to(device) for key, value in batch.items()}
            optimizer.zero_grad()
            logits = model(**{key: value for key, value in batch.items() if key != "labels"}).logits
            loss = torch.nn.functional.cross_entropy(logits, batch["labels"], weight=weights)
            loss.backward()
            optimizer.step()

    model.eval()
    scores = []
    with torch.no_grad():
        for batch in dev_loader:
            labels = batch.pop("labels").tolist()
            logits = model(**{key: value.to(device) for key, value in batch.items()}).logits
            risks = torch.softmax(logits, dim=-1)[:, 1].cpu().tolist()
            scores.extend(zip(labels, risks))

    # Threshold selection uses development examples only.
    candidates = sorted({0.0, 0.5, 1.0, *(risk for _, risk in scores)})
    def f1(threshold):
        tp = sum(label == 1 and risk >= threshold for label, risk in scores)
        fp = sum(label == 0 and risk >= threshold for label, risk in scores)
        fn = sum(label == 1 and risk < threshold for label, risk in scores)
        return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0

    threshold = max(candidates, key=lambda value: (f1(value), value))
    report = {
        "base_model": base_model,
        "base_revision": getattr(model.config, "_commit_hash", None),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "preprocessing_version": VERSION,
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "training_count": len(training),
        "development_count": len(development),
        "threshold": threshold,
        "development_f1": f1(threshold),
        "device": str(device),
        "labels": {"benign": 0, "attack": 1},
    }
    destination.mkdir(parents=True)
    model.save_pretrained(destination)
    tokenizer.save_pretrained(destination)
    (destination / "training_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune a local multilingual attack classifier")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--base-model", default="FacebookAI/xlm-roberta-base")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(train(args.dataset, args.destination, args.base_model, args.epochs, args.batch_size, args.seed), indent=2))
