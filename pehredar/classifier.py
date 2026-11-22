import json
from functools import lru_cache
from pathlib import Path

from .normalizer import VERSION


@lru_cache(maxsize=1)
def _load(directory: str):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    path = Path(directory)
    report = json.loads((path / "training_report.json").read_text(encoding="utf-8"))
    if report["preprocessing_version"] != VERSION:
        raise ValueError("Classifier preprocessing version does not match gateway")
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True)
    model.eval()
    return tokenizer, model, torch, float(report["threshold"])


def score_classifier(normalized_text: str, directory: str) -> tuple[float, float]:
    tokenizer, model, torch, threshold = _load(directory)
    encoded = tokenizer(normalized_text, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        risk = torch.softmax(model(**encoded).logits, dim=-1)[0, 1].item()
    return risk, threshold
