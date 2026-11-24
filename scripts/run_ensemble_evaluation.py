"""Evaluate DeBERTa, v1b and the language-routed ensembles -> results/ensemble_v1.md."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import DEBERTA_THRESHOLD, _load_classifier
from run_v1_evaluation import DATA, metric, scored, summary
from pehredar.dataset import load_jsonl

CLF = "models/clf_v1b"
MODELS = {"deberta": "deberta", "v1b_e1": "classifier", "ensemble": "ensemble", "ensemble_max": "ensemble_max"}
SETS = {"external_eval": "external_eval.jsonl", "indirect_eval": "indirect_eval.jsonl",
        "overrefusal_eval": "overrefusal_eval.jsonl", "benign_email_probe": "benign_email_probe.jsonl"}
ROWS = [("external_eval", None), ("indirect_eval", "bipia"), ("indirect_eval", "injecagent"),
        ("indirect_eval", "llmail"), ("overrefusal_eval", "xstest"), ("overrefusal_eval", "or_bench"),
        ("benign_email_probe", None), ("translated_dev", None)]
TRANSLATED_DEV = "translated_v2_dev_eval.jsonl"


def translated_dev_rows():
    """Passed translations whose original is in the dev split (never train)."""
    src = DATA / "translated_v2.jsonl"
    if not src.exists():
        return 0
    dev_ids = {json.loads(x)["id"] for x in (DATA / "dev_public_v2.jsonl").open(encoding="utf-8") if x.strip()}
    rows = [r for r in map(json.loads, src.read_text(encoding="utf-8").splitlines())
            if r and (r.get("orig_split") == "dev" or r["orig_id"] in dev_ids)]
    if rows:
        (DATA / TRANSLATED_DEV).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return len(rows)


def main():
    Path("results/cache").mkdir(parents=True, exist_ok=True)
    sets = dict(SETS)
    n_dev = translated_dev_rows()
    if n_dev:
        sets["translated_dev"] = TRANSLATED_DEV
    clf_threshold = _load_classifier(CLF)[3]
    thresholds = {"deberta": DEBERTA_THRESHOLD, "v1b_e1": clf_threshold, "ensemble": 1.0, "ensemble_max": 1.0}
    out = {}
    for model, detector in MODELS.items():
        directory = None if detector == "deberta" else CLF
        out[model] = {"threshold": thresholds[model], "sets": {}}
        for set_name, filename in sets.items():
            path = DATA / filename
            result = scored(path, detector, directory, thresholds[model])
            preds = []
            for row, pred in zip(load_jsonl(path), result["predictions"]):
                assert row.id == pred["id"], (path, row.id, pred["id"])
                preds.append({"label": row.label, "source": row.source, "lang": row.lang,
                              "prediction": "attack" if pred["risk"] >= thresholds[model] else "benign"})
            out[model]["sets"][set_name] = {
                "overall": summary(preds),
                "per_source": {s: summary([p for p in preds if p["source"] == s]) for s in sorted({p["source"] for p in preds})},
                "per_language": {l: summary([p for p in preds if p["lang"] == l]) for l in sorted({p["lang"] for p in preds})}}
    Path("results/ensemble_v1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    render(out, n_dev, clf_threshold)


def render(out, n_dev, clf_threshold):
    def f(v):
        return "n/a" if v is None else f"{v:.4f}"
    def label(set_name, source):
        if source is None:
            return set_name
        return {"llmail": "llmail (seen)", "bipia": "bipia (unseen)", "injecagent": "injecagent (unseen)"}.get(source, f"{source} FPR")
    lines = ["# Ensemble evaluation v1", "",
             f"- `ensemble`: language-routed. `en` -> DeBERTa (threshold {DEBERTA_THRESHOLD}); "
             f"`ur` / `roman_ur` / `mixed` -> v1b (saved threshold {clf_threshold:.4f}).",
             "- `ensemble_max`: attack if either model is over its own threshold.",
             "- Language comes from each row's `lang` label.",
             ("- Translated dev rows: " + (f"{n_dev} machine-translated rows from DEV-split originals. "
              "Machine-made, not the human test set." if n_dev else
              "none. `translated_v2.jsonl` holds only translations of TRAIN-split rows, so no translated "
              "dev rows exist.")),
             "- Non-`en` rows per eval set (routed to v1b by `ensemble`): " + "; ".join(
                 f"{name} {sum(m['count'] for l, m in item['per_language'].items() if l != 'en')}"
                 for name, item in out["deberta"]["sets"].items()) + ". On `en` rows `ensemble` equals DeBERTa.", "",
             "| Model | Eval row | Recall | FPR | F1 |", "|---|---|---:|---:|---:|"]
    for model in out:
        for set_name, source in ROWS:
            m = metric(out, model, set_name, source)
            if m:
                lines.append(f"| {model} | {label(set_name, source)} | {f(m['recall'])} | {f(m['fpr'])} | {f(m['f1'])} |")
    lines += ["", "## Numbers-only comparison (generated)", ""]
    for set_name, source in ROWS:
        key = "fpr" if source in {"xstest", "or_bench"} or set_name == "benign_email_probe" else "recall"
        vals = [(m, metric(out, m, set_name, source)) for m in out]
        if not any(v for _, v in vals):
            continue
        name = label(set_name, source)
        lines.append(f"- {name}{'' if name.endswith('FPR') else ' ' + key}: " + " vs ".join(f"{f((v or {}).get(key))} ({m})" for m, v in vals))
    lines += ["", "## Limitations", "",
              "- v1b is the interim multilingual classifier; v2 is not trained yet (waits for translation review).",
              "- `llmail` is seen distribution for v1b; `bipia` and `injecagent` are unseen.",
              "- No model was promoted to the gateway."]
    Path("results/ensemble_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
