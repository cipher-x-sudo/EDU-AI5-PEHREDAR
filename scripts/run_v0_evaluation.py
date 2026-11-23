"""Evaluate v0 and fixed baselines on public evaluation files."""
import json
from pathlib import Path
from evaluate import evaluate

SETS = {
    "dev_public": "dev_public.jsonl",
    "indirect_eval": "indirect_eval.jsonl",
    "external_eval": "external_eval.jsonl",
    "overrefusal_eval": "overrefusal_eval.jsonl",
    "benign_email_probe": "benign_email_probe.jsonl",
}
MODELS = ("classifier", "rules", "deberta")

def main():
    output = {}
    for name, filename in SETS.items():
        path = Path("data/processed") / filename
        output[name] = {}
        for detector in MODELS:
            try:
                output[name][detector] = evaluate(
                    path, detector,
                    "models/clf_v0" if detector == "classifier" else None,
                )
            except Exception as exc:
                output[name][detector] = {"error": f"{type(exc).__name__}: {exc}"}
    Path("results/v0_evaluation.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("wrote results/v0_evaluation.json")

if __name__ == "__main__":
    main()
