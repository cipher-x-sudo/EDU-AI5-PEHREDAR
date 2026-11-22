import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

from pehredar.dataset import load_jsonl
from pehredar.normalizer import normalize_text
from pehredar.rules import score_rules


def evaluate(path: Path) -> dict:
    rows = load_jsonl(path)
    predictions = []
    for row in rows:
        start = time.perf_counter()
        risk, tags = score_rules(normalize_text(row.input_text()))
        predictions.append({
            "id": row.id,
            "lang": row.lang,
            "label": row.label,
            "prediction": "attack" if risk >= 0.75 else "benign",
            "risk": risk,
            "tags": tags,
            "latency_ms": round((time.perf_counter() - start) * 1000, 3),
        })
    metrics = {}
    for language in ("en", "ur", "roman_ur", "mixed"):
        group = [p for p in predictions if p["lang"] == language]
        tp = sum(p["label"] == "attack" and p["prediction"] == "attack" for p in group)
        fn = sum(p["label"] == "attack" and p["prediction"] == "benign" for p in group)
        fp = sum(p["label"] == "benign" and p["prediction"] == "attack" for p in group)
        tn = sum(p["label"] == "benign" and p["prediction"] == "benign" for p in group)
        metrics[language] = {
            "count": len(group), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": tp / (tp + fn) if tp + fn else None,
            "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        }
    latencies = sorted(p["latency_ms"] for p in predictions)
    return {
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "detector": "rules-v1",
        "threshold": 0.75,
        "metrics": metrics,
        "median_latency_ms": statistics.median(latencies) if latencies else None,
        "p95_latency_ms": latencies[max(0, int(len(latencies) * 0.95) - 1)] if latencies else None,
        "predictions": predictions,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.dataset)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
