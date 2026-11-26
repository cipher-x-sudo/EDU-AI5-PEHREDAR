"""roman_ur LaBSE filter: fit + report. Applying happens in scripts/refilter_translations.py (the one entry
point for the filter chain: v3 checks -> this threshold -> script check), so

  python scripts/labse_filter.py      # same as running refilter_translations.py

Fit: largest threshold on all reviewed roman_ur rows (v2 main, v2 abliterated, v3) that removes at most
floor(5%) of good rows; used only if bad removed >= 5 and >= 3x good removed.
Report: v3 verdicts, fit, rows removed per file, post-filter quality on the v3 sample, training gate.
Writes results/labse_filter_v3.md."""
import csv, json, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from meaning_scores import FILES, MAX_GOOD_REMOVED, dist, read, threshold
from translation_checks import check, clean, foreign_scripts

ROOT = Path("data/processed")
REVIEWS = ("translation_review_v2.csv", "translation_review_v2_abliterated.csv", "translation_review_v3.csv")
LANG = "roman_ur"
CLEARLY = 3


def reviewed():
    scores = {s["id"]: s["score"] for s in read(ROOT/"meaning_scores_v3.jsonl") if s["file"] == "translated_v2"}
    rows = []
    for f in REVIEWS:
        for r in csv.DictReader((ROOT/f).open(encoding="utf-8-sig")):
            text = clean(r["translation"])
            rows.append({"file": f, "id": r["id"], "lang": r["lang"], "label": r["label"], "model": r["model"],
                         "cell": f"{r['lang']}/{r['label']}", "verdict": r["verdict"].strip().lower(),
                         "meaning": "[meaning]" in r["note"].lower(), "note": r["note"],
                         "v3_caught": bool(check(text, r["original"])), "script_caught": bool(foreign_scripts(text, r["original"])),
                         "score": scores[r["id"]]})
    return rows


def fit():
    ru = [r for r in reviewed() if r["lang"] == LANG]
    res = threshold(ru)
    t = res["threshold_reject_below"]
    good_rm = sum(r["verdict"] == "good" and r["score"] < t for r in ru)
    bad_rm = sum(r["verdict"] == "bad" and r["score"] < t for r in ru)
    rule = bad_rm >= 5 and bad_rm >= CLEARLY * good_rm
    return {**res, "reviewed_rows": len(ru), "by_file": dict(Counter(r["file"] for r in ru)),
            "good_scores": dist([r["score"] for r in ru if r["verdict"] == "good"]),
            "bad_scores": dist([r["score"] for r in ru if r["verdict"] == "bad"]),
            "bad_meaning_scores": dist([r["score"] for r in ru if r["verdict"] == "bad" and r["meaning"]]),
            "max_good_removed_share": MAX_GOOD_REMOVED, "apply_rule": f"bad removed >= 5 and >= {CLEARLY} x good removed",
            "rule_holds": rule, "threshold": t if rule else None}


GEMINI_REVIEW = ROOT/"translation_review_gemini.csv"


def gemini_lang(row_id):
    return row_id.rsplit("-", 2)[1]  # <orig_id>-<lang>-gemini


def fit_balanced(lang, gemini_scores, cap_share=0.02):
    """Threshold (reject score < t) for one language, fitted on qwen review rows (good + bad) plus Gemini
    review rows (all good so far): the t maximising balanced accuracy, then capped so that at most
    cap_share of all Gemini rows of that language score below it."""
    rows = [r for r in reviewed() if r["lang"] == lang]
    rows += [{"verdict": r["verdict"].strip().lower(), "score": gemini_scores[r["id"]], "file": GEMINI_REVIEW.name}
             for r in csv.DictReader(GEMINI_REVIEW.open(encoding="utf-8-sig")) if r["lang"] == lang]
    bad = [r["score"] for r in rows if r["verdict"] == "bad"]
    good = [r["score"] for r in rows if r["verdict"] == "good"]
    ba = lambda t: (sum(s < t for s in bad) / len(bad) + sum(s >= t for s in good) / len(good)) / 2
    best = max(sorted({r["score"] for r in rows}), key=lambda t: (round(ba(t), 6), -t))
    pool = sorted(v for k, v in gemini_scores.items() if gemini_lang(k) == lang)
    cap = pool[int(cap_share * len(pool))]  # rejecting s < cap removes at most cap_share of the pool
    t = min(best, cap)
    return {"lang": lang, "fit_rows": {"qwen_good": sum(r["verdict"] == "good" and r["file"] != GEMINI_REVIEW.name for r in rows),
                                       "qwen_bad": len(bad), "gemini_good": sum(r["file"] == GEMINI_REVIEW.name and r["verdict"] == "good" for r in rows)},
            "balanced_accuracy_threshold": best, "balanced_accuracy": round(ba(best), 4),
            "cap_2pct_of_gemini_rows": cap, "gemini_rows_scored": len(pool), "cap_applied": best > cap, "threshold": t,
            "balanced_accuracy_at_threshold": round(ba(t), 4)}


def verdicts(rows):
    def share(key):
        out = {}
        for r in rows: out.setdefault(r[key], Counter())[r["verdict"]] += 1
        return {k: {"good": c["good"], "bad": c["bad"], "good_share": round(c["good"] / sum(c.values()), 4)} for k, c in sorted(out.items())}
    return {"rows": len(rows), "good": sum(r["verdict"] == "good" for r in rows), "bad": sum(r["verdict"] == "bad" for r in rows),
            "by_lang": share("lang"), "by_label": share("label"), "by_lang_label": share("cell"),
            "bad_note_tags": dict(Counter(t for r in rows for t in re.findall(r"\[[a-z-]+\]", r["note"].lower())).most_common())}


def report():
    rows = reviewed(); f = fit(); t = f["threshold"]
    v3 = [r for r in rows if r["file"] == "translation_review_v3.csv"]
    keep = [r for r in v3 if not r["v3_caught"] and not (t is not None and r["lang"] == LANG and r["score"] < t)
            and not r["script_caught"]]
    est = lambda xs: {"passing": len(xs), "good": sum(r["verdict"] == "good" for r in xs),
                      "good_rate": round(sum(r["verdict"] == "good" for r in xs) / max(1, len(xs)), 4)}
    estimate = {"all": est(keep), "roman_ur+mixed": est([r for r in keep if r["lang"] != "ur"]),
                **{l: est([r for r in keep if r["lang"] == l]) for l in ("roman_ur", "ur", "mixed")},
                **{lab: est([r for r in keep if r["label"] == lab]) for lab in ("attack", "benign")}}
    removed = {}
    for name in FILES:
        lab = read(ROOT/f"{name}_rejected_labse.jsonl"); scr = read(ROOT/f"{name}_rejected_script.jsonl")
        removed[name] = {"labse_roman_ur": {"total": len(lab), **Counter(r["label"] for r in lab)},
                         "script_check": {"total": len(scr), **{l: sum(r["lang"] == l for r in scr) for l in ("roman_ur", "ur", "mixed")},
                                          "scripts": dict(Counter(s for r in scr for s in r["foreign_scripts"]))},
                         "rows_after": len(read(ROOT/f"{name}.jsonl"))}
    rate = estimate["roman_ur+mixed"]["good_rate"]
    report = {"v3_verdicts": verdicts(v3), "roman_ur_fit": f, "removed_per_file": removed,
              "post_filter_estimate_v3_sample": estimate,
              "note": "Estimate = good share of v3 sample rows that pass the v3 checks, the roman_ur threshold and the "
                      "script check. v3 rows are part of the threshold fit, so the roman_ur estimate is optimistic. "
                      "ur and mixed are not threshold-filtered.",
              "training_gate": {"scope": "roman_ur + mixed (team decision 2026-11-26: no ur in training)", "estimate": rate,
                                "decision": "continue" if rate >= .80 else "continue with stated limitation" if rate >= .75 else "stop"}}
    Path("results/labse_filter_v3.md").write_text(
        "# roman_ur LaBSE filter, script check and v3 review\n\nGenerated by `scripts/labse_filter.py` / "
        "`scripts/refilter_translations.py`.\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(report["post_filter_estimate_v3_sample"]), json.dumps(report["training_gate"]), flush=True)
    return report


if __name__ == "__main__":
    import refilter_translations
    refilter_translations.main()
