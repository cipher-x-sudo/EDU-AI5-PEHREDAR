"""Evaluate DeBERTa, v2 and ensemble_routed on the frozen HUMAN test set -> results/frozen_v1.md.

Refuses to run unless PEHREDAR_EVAL_FROZEN=1 (and PEHREDAR_SKIP_FROZEN is not 1). The frozen set may be
evaluated ONCE per final model: thresholds are fixed (DeBERTa 0.5, v2 from its training_report.json, chosen on
dev data), nothing is tuned here. Every run is appended to results/frozen_runs.log with timestamp and commit.
ensemble_routed routes by the gateway's language detector (pehredar/langid.py), as deployed; metrics are
reported per dataset language label.

  PEHREDAR_EVAL_FROZEN=1 PEHREDAR_SKIP_FROZEN=0 python scripts/eval_frozen.py   (gateway-gpu image, GPU)"""
import json, math, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

FROZEN = Path("data/frozen_test/human_v1.jsonl")
V2_DIR = os.getenv("PEHREDAR_L2_XLMR_DIR", "models/clf_v3_e3")
LOG = Path("results/frozen_runs.log")
OUT = Path("results/frozen_v1.md")
WARNING = ("WARNING: data/frozen_test is the human test set. It may only be evaluated ONCE per final model. "
           "Do not tune thresholds, prompts or data on these results.")


def refuse_unless_allowed():
    if os.getenv("PEHREDAR_EVAL_FROZEN") != "1" or os.getenv("PEHREDAR_SKIP_FROZEN") == "1":
        print("eval_frozen refuses to run: set PEHREDAR_EVAL_FROZEN=1 (and not PEHREDAR_SKIP_FROZEN=1) "
              "to evaluate the frozen human test set.", file=sys.stderr)
        raise SystemExit(2)


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def cell(k, n):
    if not n:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k / n:.3f} ({k}/{n}) [{lo:.3f}–{hi:.3f}]"


def commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return os.getenv("PEHREDAR_COMMIT")


def main():
    refuse_unless_allowed()
    print(WARNING, file=sys.stderr, flush=True)
    from pehredar.dataset import load_jsonl
    from pehredar.l2 import L2
    from pehredar.langid import detect
    from pehredar.normalizer import normalize_text
    run = {"timestamp": datetime.now(timezone.utc).isoformat(), "commit": commit() or os.getenv("PEHREDAR_COMMIT"),
           "file": str(FROZEN), "v2_dir": V2_DIR}
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**run, "event": "start"}) + "\n")
    rows = load_jsonl(FROZEN)
    l2 = L2().load(V2_DIR)
    if l2.errors:
        raise SystemExit(f"model load failed: {l2.errors}")
    preds = []
    for r in rows:
        text = normalize_text(r.input_text())
        d = l2.models["deberta"].fn(text); v = l2.models["xlmr"].fn(text)
        hit_d, hit_v = d >= l2.models["deberta"].threshold, v >= l2.models["xlmr"].threshold
        preds.append({"lang": r.lang, "label": r.label, "deberta": hit_d, "v2": hit_v,
                      "ensemble_routed": hit_d if detect(text) == "en" else hit_v})
    models = ("deberta", "v2", "ensemble_routed")
    langs = ["all", *sorted({p["lang"] for p in preds})]
    table = {}
    for lang in langs:
        ps = [p for p in preds if lang == "all" or p["lang"] == lang]
        a = [p for p in ps if p["label"] == "attack"]; b = [p for p in ps if p["label"] == "benign"]
        table[lang] = {m: {"tp": sum(p[m] for p in a), "attacks": len(a), "fp": sum(p[m] for p in b), "benign": len(b)} for m in models}
    lines = ["# Frozen human test set v1", "", f"> {WARNING}", "",
             f"- Run: {run['timestamp']}, commit {run['commit']}, rows {len(rows)}",
             f"- Fixed thresholds: DeBERTa {l2.models['deberta'].threshold}, v2 {l2.models['v2'].threshold:.4f} ({V2_DIR}); "
             "ensemble_routed: detected en → DeBERTa, else v2.", "",
             "| Language | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |", "|---|---|---|---|"]
    for lang, ms in table.items():
        for m, x in ms.items():
            lines.append(f"| {lang} | {m} | {cell(x['tp'], x['attacks'])} | {cell(x['fp'], x['benign'])} |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**run, "event": "done", "rows": len(rows), "result": str(OUT)}) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
