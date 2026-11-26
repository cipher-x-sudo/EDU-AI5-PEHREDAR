"""LaBSE meaning check (prepared, not applied).

  python scripts/meaning_scores.py            # GPU: score every translation -> data/processed/meaning_scores_v3.jsonl, then report
  python scripts/meaning_scores.py --report   # CPU: report only -> results/meaning_check_v3.md

Scores every row of the *_pre_v3 backups (all translations, before the v3 re-filter and abliterated
drop), so the reviewed rows are covered; `kept_v3` says whether the row survives in the current file.
Score = cosine(LaBSE(English original), LaBSE(cleaned translation))."""
import csv, json, sys
from pathlib import Path
from statistics import mean, median
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translation_checks import check, clean

ROOT = Path("data/processed")
OUT = ROOT/"meaning_scores_v3.jsonl"
MODEL = "sentence-transformers/LaBSE"
FILES = ("translated_v2", "dev_translated_v2", "external_translated", "overrefusal_translated")
REVIEWS = ("translation_review_v2.csv", "translation_review_v2_abliterated.csv")
LANGS = ("roman_ur", "ur", "mixed")
FALLBACK = "richardyoung/qwen3-8b-abliterated:Q4_K_M"
MAX_GOOD_REMOVED = 0.05


def read(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def score():
    rows = []
    for name in FILES:
        kept = {r["id"] for r in read(ROOT/f"{name}.jsonl")}
        rows += [(name, r, r["id"] in kept) for r in read(ROOT/f"{name}_pre_v3.jsonl")]
    sims = cosine([(r["original"], r["text"]) for _, r, _ in rows])
    with OUT.open("w", encoding="utf-8") as f:
        for (name, r, kept), sim in zip(rows, sims):
            f.write(json.dumps({"file": name, "id": r["id"], "orig_id": r["orig_id"], "lang": r["lang"], "label": r["label"],
                                "model": r["model"], "kept_v3": kept, "score": sim}) + "\n")
    print(json.dumps({"scored": len(rows), "model": MODEL}), flush=True)


def cosine(pairs):
    """LaBSE cosine(original, clean(translation)) for (original, translation) pairs, rounded to 4 places."""
    import torch
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL, device="cuda" if torch.cuda.is_available() else "cpu")
    originals = sorted({o for o, _ in pairs})
    enc = dict(zip(originals, model.encode(originals, batch_size=128, normalize_embeddings=True, show_progress_bar=True)))
    trans = model.encode([clean(t) for _, t in pairs], batch_size=128, normalize_embeddings=True, show_progress_bar=True)
    return [round(float(enc[o] @ t), 4) for (o, _), t in zip(pairs, trans)]


def dist(xs):
    if not xs:
        return {"n": 0}
    s = sorted(xs); q = lambda p: s[min(len(s) - 1, int(p * len(s)))]
    return {"n": len(s), "mean": round(mean(s), 4), "min": s[0], "p10": q(.1), "p25": q(.25), "median": round(median(s), 4),
            "p75": q(.75), "max": s[-1]}


def threshold(rows):
    """Largest t with (good rows scoring < t) <= floor(5% of good); bad removed is maximal at that t."""
    good = sorted(r["score"] for r in rows if r["verdict"] == "good")
    k = int(MAX_GOOD_REMOVED * len(good))
    t = good[k]
    removed = [r for r in rows if r["score"] < t]
    bad = [r for r in rows if r["verdict"] == "bad"]
    new = [r for r in bad if not r["v3_caught"] and r["model"] != FALLBACK]
    return {"threshold_reject_below": t, "good_removed": f"{sum(r['verdict'] == 'good' for r in removed)}/{len(good)}",
            "bad_removed": f"{sum(r['verdict'] == 'bad' for r in removed)}/{len(bad)}",
            "meaning_bad_removed": f"{sum(r['meaning'] for r in removed if r['verdict'] == 'bad')}/{sum(r['meaning'] for r in bad)}",
            "bad_missed_by_v3_and_not_abliterated_removed": f"{sum(r in removed for r in new)}/{len(new)}"}


def report():
    scores = read(OUT)
    by_id = {s["id"]: s for s in scores if s["file"] == "translated_v2"}
    reviewed = []
    for f in REVIEWS:
        for r in csv.DictReader((ROOT/f).open(encoding="utf-8-sig")):
            reviewed.append({"file": f, "lang": r["lang"], "label": r["label"], "model": r["model"],
                             "verdict": r["verdict"].strip().lower(), "meaning": "[meaning]" in r["note"].lower(),
                             "v3_caught": bool(check(clean(r["translation"]), r["original"])), "score": by_id[r["id"]]["score"]})
    groups = lambda rows: {"good": dist([r["score"] for r in rows if r["verdict"] == "good"]),
                           "bad": dist([r["score"] for r in rows if r["verdict"] == "bad"]),
                           "bad_meaning_tagged": dist([r["score"] for r in rows if r["verdict"] == "bad" and r["meaning"]]),
                           "bad_other": dist([r["score"] for r in rows if r["verdict"] == "bad" and not r["meaning"]])}
    thresholds = {"all": threshold(reviewed), **{l: threshold([r for r in reviewed if r["lang"] == l]) for l in LANGS}}
    impact = {}
    for name in FILES:
        kept = [s for s in scores if s["file"] == name and s["kept_v3"]]
        impact[name] = {l: {"kept_rows": sum(s["lang"] == l for s in kept),
                            "would_remove": sum(s["lang"] == l and s["score"] < thresholds[l]["threshold_reject_below"] for s in kept)}
                        for l in LANGS}
    report = {"model": MODEL, "scored_rows": len(scores),
              "reviewed_rows": {"total": len(reviewed), "good": sum(r["verdict"] == "good" for r in reviewed),
                                "bad": sum(r["verdict"] == "bad" for r in reviewed),
                                "bad_meaning_tagged": sum(r["verdict"] == "bad" and r["meaning"] for r in reviewed)},
              "distribution_both_csvs": groups(reviewed),
              "distribution_per_csv": {f: groups([r for r in reviewed if r["file"] == f]) for f in REVIEWS},
              "distribution_per_lang": {l: groups([r for r in reviewed if r["lang"] == l]) for l in LANGS},
              "threshold_at_most_5pct_good_removed": thresholds,
              "per_lang_threshold_impact_on_current_kept_rows (not applied)": impact,
              "all_scores_kept_rows_per_file_lang": {name: {l: dist([s["score"] for s in scores if s["file"] == name and s["kept_v3"] and s["lang"] == l])
                                                            for l in LANGS} for name in FILES}}
    Path("results/meaning_check_v3.md").write_text(
        "# Meaning check v3 (LaBSE) — prepared, NOT applied\n\nGenerated by `scripts/meaning_scores.py`. Score = cosine "
        "similarity between LaBSE embeddings of the English original and the cleaned translation (rows scoring below the "
        "threshold would be rejected). Thresholds are fitted on the 130 reviewed rows (both CSVs combined): the largest "
        "threshold that removes at most floor(5% of good rows). Per-language groups are small (21–34 good rows), so "
        "the 5% limit allows one good row per language. Nothing was filtered.\n\n```json\n"
        + json.dumps(report, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(report["threshold_at_most_5pct_good_removed"]), flush=True)


if __name__ == "__main__":
    if "--report" not in sys.argv:
        score()
    report()
