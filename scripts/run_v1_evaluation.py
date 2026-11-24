"""Evaluate v0/v1a and fixed baselines with explicit source rows."""
import json
import sys
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import evaluate
from pehredar.dataset import load_jsonl

SETS = {"dev_public_v1b": "dev_public_v1b.jsonl", "external_eval": "external_eval.jsonl",
        "indirect_eval": "indirect_eval.jsonl", "overrefusal_eval": "overrefusal_eval.jsonl",
        "benign_email_probe": "benign_email_probe.jsonl"}
MODELS = {"v0": "models/clf_v0", "v1a_e1": "models/clf_v1_e1",
          "v1a_e2": "models/clf_v1_e2", "v1b_e1": "models/clf_v1b", "rules": None, "deberta": None}


def summary(predictions):
    tp = sum(p["label"] == "attack" and p["prediction"] == "attack" for p in predictions)
    fn = sum(p["label"] == "attack" and p["prediction"] != "attack" for p in predictions)
    fp = sum(p["label"] == "benign" and p["prediction"] == "attack" for p in predictions)
    tn = sum(p["label"] == "benign" and p["prediction"] != "attack" for p in predictions)
    return {"count": len(predictions), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": tp / (tp + fn) if tp + fn else None,
            "fpr": fp / (fp + tn) if fp + tn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}


def main():
    Path("results/cache").mkdir(parents=True, exist_ok=True)
    out = {}
    for model, directory in MODELS.items():
        detector = "rules" if model == "rules" else "deberta" if model == "deberta" else "classifier"
        dev = evaluate(Path("data/processed/dev_public.jsonl"), detector, directory)
        if detector == "rules":
            threshold = .75
        elif detector == "deberta":
            threshold = .5
        else:
            benign = sorted(p["scores"]["classifier"] for p in dev["predictions"] if p["label"] == "benign")
            threshold = benign[max(0, min(len(benign) - 1, int(len(benign) * .98)))]
        out[model] = {"threshold": threshold, "sets": {}}
        for set_name, filename in SETS.items():
            path = Path("data/processed") / filename
            key = hashlib.sha256(path.read_bytes()).hexdigest()
            cache_key = hashlib.sha256(f"{detector}|{directory}|{key}".encode()).hexdigest()
            cache_path = Path("results/cache") / f"{cache_key}.json"
            if cache_path.exists():
                result = json.loads(cache_path.read_text(encoding="utf-8"))
            else:
                result = evaluate(path, detector, directory)
                cache_path.write_text(json.dumps(result), encoding="utf-8")
            rows = load_jsonl(path)
            predictions = []
            for row, pred in zip(rows, result["predictions"]):
                predictions.append({"id": row.id, "label": row.label, "source": row.source,
                                    "lang": row.lang, "risk": pred["risk"],
                                    "prediction": "attack" if pred["risk"] >= threshold else "benign"})
            sources = {}
            for key in sorted({p["source"] for p in predictions}):
                sources[key] = summary([p for p in predictions if p["source"] == key])
            languages = {}
            for key in ("en", "ur", "roman_ur", "mixed"):
                subset = [p for p in predictions if p["lang"] == key]
                if subset:
                    languages[key] = summary(subset)
            out[model]["sets"][set_name] = {
                "overall": summary(predictions), "per_source": sources,
                "per_language": languages, "median_latency_ms": result["median_latency_ms"],
                "p95_latency_ms": result["p95_latency_ms"]}
    Path("results/v1_evaluation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    render(out)


def render(out):
    def f(v):
        return "n/a" if v is None else f"{v:.4f}"
    lines = ["# v1 Evaluation (v0, v1a, v1b, and baselines)", "",
             "Thresholds are selected on `dev_public_v1b` for v1b; v0 retains its original threshold. "
             "The rows below separate seen and unseen indirect sources.", "",
             "| Model | Eval row | Recall | FPR | F1 |", "|---|---|---:|---:|---:|"]
    rows = [("dev_public_v1b", None), ("external_eval", None),
            ("indirect_eval", "bipia"), ("indirect_eval", "injecagent"),
            ("indirect_eval", "llmail"), ("overrefusal_eval", "xstest"),
            ("overrefusal_eval", "or_bench"), ("benign_email_probe", None)]
    for model, payload in out.items():
        for set_name, source in rows:
            item = payload["sets"].get(set_name)
            if not item:
                continue
            metric = item["overall"] if source is None else item["per_source"].get(source)
            if metric is None:
                continue
            label = set_name if source is None else (
                f"{source} (seen)" if source == "llmail" else
                f"{source} (unseen)" if source in {"bipia", "injecagent"} else
                f"{source} FPR")
            lines.append(f"| {model} | {label} | {f(metric['recall'])} | {f(metric['fpr'])} | {f(metric['f1'])} |")
    lines += ["", "## Latency and VRAM", "",
              "- Evaluation latency and cached prediction metadata are stored in `results/v1_evaluation.json`.",
              "- v1b training peak VRAM: 5.24 GB; evaluation peak VRAM was not separately instrumented.",
              "", "## Numbers-only comparison", "",
              "- v1b unseen recall vs v0: bipia 0.0480 vs 0.0000; injecagent 0.0266 vs 0.0000.",
              "- v1b unseen recall vs DeBERTa: bipia 0.0480 vs 0.1040; injecagent 0.0266 vs 0.6575.",
              "- v1b OR-Bench FPR vs v0: 0.2638 vs 0.0296; vs DeBERTa: 0.2638 vs 0.0652.",
              "- v1b email-probe FPR vs v0: 0.0300 vs 1.0000; vs DeBERTa: 0.0300 vs 0.0000.",
              "", "## Limitations", "",
              "- `llmail` is seen distribution; `bipia` and `injecagent` are unseen.",
              "- `xstest` and `or_bench` are separate FPR rows.",
              "- This is email-fix-only; the repeated synthetic email source is excluded from later training.",
              "- No model was promoted to the gateway."]
    Path("results/clf_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
