"""roman_ur LaBSE filter: summarise v3 verdicts, refit the roman_ur threshold on all reviewed rows,
apply it (roman_ur only) when it removes clearly more bad than good, and estimate post-filter quality.

  python scripts/labse_filter.py          # fit, apply if the rule holds, report
  python scripts/labse_filter.py --dry    # fit and report only

Apply: first run backs up {name}.jsonl to {name}_pre_labse.jsonl and always reads that backup (idempotent);
removed rows -> {name}_rejected_labse.jsonl. Writes results/labse_filter_v3.md."""
import csv, json, re, shutil, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from meaning_scores import FALLBACK, FILES, MAX_GOOD_REMOVED, dist, read, threshold
from translation_checks import check, clean

ROOT = Path("data/processed")
REVIEWS = ("translation_review_v2.csv", "translation_review_v2_abliterated.csv", "translation_review_v3.csv")
LANG = "roman_ur"
CLEARLY = 3  # apply only if bad removed >= CLEARLY x good removed (and at least 5 bad)


def reviewed():
    scores = {s["id"]: s["score"] for s in read(ROOT/"meaning_scores_v3.jsonl") if s["file"] == "translated_v2"}
    rows = []
    for f in REVIEWS:
        for r in csv.DictReader((ROOT/f).open(encoding="utf-8-sig")):
            rows.append({"file": f, "id": r["id"], "lang": r["lang"], "label": r["label"], "model": r["model"],
                         "verdict": r["verdict"].strip().lower(), "meaning": "[meaning]" in r["note"].lower(), "note": r["note"],
                         "v3_caught": bool(check(clean(r["translation"]), r["original"])), "score": scores[r["id"]]})
    return rows


def verdicts(rows):
    def share(key):
        out = {}
        for r in rows: out.setdefault(r[key], Counter())[r["verdict"]] += 1
        return {k: {"good": c["good"], "bad": c["bad"], "good_share": round(c["good"] / sum(c.values()), 4)} for k, c in sorted(out.items())}
    return {"rows": len(rows), "good": sum(r["verdict"] == "good" for r in rows), "bad": sum(r["verdict"] == "bad" for r in rows),
            "by_lang": share("lang"), "by_label": share("label"),
            "by_lang_label": share("cell"),
            "bad_note_tags": dict(Counter(t for r in rows for t in re.findall(r"\[[a-z-]+\]", r["note"].lower())).most_common())}


def apply(t):
    log = {}
    for name in FILES:
        src, backup = ROOT/f"{name}.jsonl", ROOT/f"{name}_pre_labse.jsonl"
        if not backup.exists():
            shutil.copyfile(src, backup)
        scores = {s["id"]: s["score"] for s in read(ROOT/"meaning_scores_v3.jsonl") if s["file"] == name}
        rows = read(backup)
        drop = [{**r, "labse_score": scores[r["id"]], "reason": f"labse<{t}"} for r in rows if r["lang"] == LANG and scores[r["id"]] < t]
        ids = {r["id"] for r in drop}
        (ROOT/f"{name}_rejected_labse.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in drop), encoding="utf-8")
        src.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows if r["id"] not in ids), encoding="utf-8")
        log[name] = {"roman_ur_before": sum(r["lang"] == LANG for r in rows), "removed": len(drop),
                     "removed_by_label": dict(Counter(r["label"] for r in drop)), "rows_after": len(rows) - len(drop)}
    return log


def main():
    rows = reviewed()
    for r in rows: r["cell"] = f"{r['lang']}/{r['label']}"
    v3 = [r for r in rows if r["file"] == "translation_review_v3.csv"]
    ru = [r for r in rows if r["lang"] == LANG]
    fit = threshold(ru)
    t = fit["threshold_reject_below"]
    good_rm = sum(r["verdict"] == "good" and r["score"] < t for r in ru)
    bad_rm = sum(r["verdict"] == "bad" and r["score"] < t for r in ru)
    rule = bad_rm >= 5 and bad_rm >= CLEARLY * good_rm
    applied = rule and "--dry" not in sys.argv
    log = apply(t) if applied else None
    # post-filter estimate on the v3 sample: rows passing the v3 checks and (roman_ur) the threshold
    keep = [r for r in v3 if not r["v3_caught"] and not (r["lang"] == LANG and r["score"] < t)]
    est = lambda xs: {"passing": len(xs), "good": sum(r["verdict"] == "good" for r in xs),
                      "good_rate": round(sum(r["verdict"] == "good" for r in xs) / max(1, len(xs)), 4)}
    estimate = {"all": est(keep), **{l: est([r for r in keep if r["lang"] == l]) for l in ("roman_ur", "ur", "mixed")},
                **{lab: est([r for r in keep if r["label"] == lab]) for lab in ("attack", "benign")}}
    rate = estimate["all"]["good_rate"]
    gate = "continue" if rate >= .80 else "continue with stated limitation" if rate >= .75 else "stop"
    report = {"v3_verdicts": verdicts(v3),
              "roman_ur_fit": {"reviewed_rows": len(ru), "by_file": dict(Counter(r["file"] for r in ru)),
                               "good_scores": dist([r["score"] for r in ru if r["verdict"] == "good"]),
                               "bad_scores": dist([r["score"] for r in ru if r["verdict"] == "bad"]),
                               "bad_meaning_scores": dist([r["score"] for r in ru if r["verdict"] == "bad" and r["meaning"]]),
                               "max_good_removed_share": MAX_GOOD_REMOVED, **fit,
                               "apply_rule": f"bad removed >= 5 and >= {CLEARLY} x good removed", "rule_holds": rule, "applied": applied},
              "applied_log": log,
              "post_filter_estimate_v3_sample": estimate,
              "note": "v3 rows are part of the threshold fit, so the roman_ur estimate is optimistic. ur and mixed are not threshold-filtered.",
              "training_gate": {"estimate": rate, "decision": gate}}
    Path("results/labse_filter_v3.md").write_text(
        "# roman_ur LaBSE filter and v3 review\n\nGenerated by `scripts/labse_filter.py`. Threshold fitted on all reviewed "
        "roman_ur rows (v2 main, v2 abliterated, v3): largest threshold removing at most floor(5%) of good rows. Applied "
        "to roman_ur rows only.\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
