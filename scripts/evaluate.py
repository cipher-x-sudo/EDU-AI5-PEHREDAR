import argparse
import hashlib
import json
import statistics
import time
from functools import lru_cache
from pathlib import Path

from pehredar.classifier import score_classifier
from pehredar.dataset import load_jsonl
from pehredar.normalizer import normalize_text
from pehredar.rules import score_rules


@lru_cache(maxsize=1)
def load_deberta():
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    name = "protectai/deberta-v3-base-prompt-injection-v2"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name)
    model.eval()
    label = next(index for index, value in model.config.id2label.items() if value.upper() == "INJECTION")
    return tokenizer, model, torch, int(label)


def score_deberta(text: str) -> float:
    tokenizer, model, torch, label = load_deberta()
    encoded = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        return torch.softmax(model(**encoded).logits, dim=-1)[0, label].item()


def evaluate(path: Path, detector: str = "rules", classifier_dir: str | None = None) -> dict:
    if detector not in {"rules", "deberta", "classifier", "combined"}:
        raise ValueError(f"Unknown detector: {detector}")
    if detector in {"classifier", "combined"} and not classifier_dir:
        raise ValueError("classifier_dir is required")
    rows = load_jsonl(path)
    predictions = []
    for row in rows:
        start = time.perf_counter()
        text = normalize_text(row.input_text())
        rules_risk, tags = score_rules(text)
        scores = {"rules": rules_risk}
        if detector == "deberta":
            scores["deberta"] = score_deberta(text)
            risk, threshold = scores["deberta"], 0.5
        elif detector == "classifier":
            scores["classifier"], threshold = score_classifier(text, classifier_dir)
            risk = scores["classifier"]
        elif detector == "combined":
            scores["classifier"], classifier_threshold = score_classifier(text, classifier_dir)
            risk = max(rules_risk, 0.75 if scores["classifier"] >= classifier_threshold else scores["classifier"])
            threshold = 0.75
        else:
            risk, threshold = rules_risk, 0.75
        predictions.append({
            "id": row.id,
            "lang": row.lang,
            "label": row.label,
            "prediction": "attack" if risk >= threshold else "benign",
            "risk": risk,
            "scores": scores,
            "tags": tags,
            "latency_ms": round((time.perf_counter() - start) * 1000, 3),
        })
    metrics = {}
    def summarize(group):
        group_latencies = sorted(p["latency_ms"] for p in group)
        tp = sum(p["label"] == "attack" and p["prediction"] == "attack" for p in group)
        fn = sum(p["label"] == "attack" and p["prediction"] == "benign" for p in group)
        fp = sum(p["label"] == "benign" and p["prediction"] == "attack" for p in group)
        tn = sum(p["label"] == "benign" and p["prediction"] == "benign" for p in group)
        return {
            "count": len(group), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": tp / (tp + fn) if tp + fn else None,
            "false_positive_rate": fp / (fp + tn) if fp + tn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
            "median_latency_ms": statistics.median(group_latencies) if group_latencies else None,
            "p95_latency_ms": group_latencies[max(0, int(len(group_latencies) * 0.95) - 1)] if group_latencies else None,
        }
    for language in ("en", "ur", "roman_ur", "mixed"):
        group = [p for p in predictions if p["lang"] == language]
        metrics[language] = summarize(group)
    by_source = {}
    for source in sorted({row.source or "unknown" for row in rows}):
        by_source[source] = summarize([p for p, row in zip(predictions, rows) if (row.source or "unknown") == source])
    latencies = sorted(p["latency_ms"] for p in predictions)
    return {
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "detector": detector,
        "classifier_dir": classifier_dir,
        "deberta_scope": "English prompt injection only" if detector == "deberta" else None,
        "metrics": metrics,
        "per_source": by_source,
        "indirect_eval_source_scope": {
            source: ("seen distribution" if source == "llmail" else "unseen")
            for source in by_source
        } if path.name == "indirect_eval.jsonl" else None,
        "median_latency_ms": statistics.median(latencies) if latencies else None,
        "p95_latency_ms": latencies[max(0, int(len(latencies) * 0.95) - 1)] if latencies else None,
        "predictions": predictions,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--detector", choices=("rules", "deberta", "classifier", "combined"), default="rules")
    parser.add_argument("--classifier-dir")
    args = parser.parse_args()
    report = evaluate(args.dataset, args.detector, args.classifier_dir)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
