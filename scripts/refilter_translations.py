"""Re-filter existing translations with the v3 checks (no re-translation).

- Drops every abliterated-model row (review: 11/30 good).
- Cleans /no_think and think tags, rejects rows failing scripts/translation_checks.check.
- First run backs up {name}.jsonl to {name}_pre_v3.jsonl; every run reads the backup, so it is idempotent.
  Kept -> {name}.jsonl, removed -> {name}_rejected_v3.jsonl (with v3_reasons).
- Then, in this order on the rows that survive: the roman_ur LaBSE threshold (labse_filter.fit, from the review
  CSVs and meaning_scores_v3.jsonl) -> {name}_rejected_labse.jsonl, and the script check (letters outside
  Latin/Arabic, unless the original has that script) -> {name}_rejected_script.jsonl.
  Always rebuilt from the _pre_v3 backup, so this is the one entry point for the whole filter chain.
- Summarises review verdicts, measures catch rate on reviewed rows, draws translation_review_v3.csv
  (only if it does not exist yet: it holds reviewer verdicts).
Writes results/translation_refilter_v3.md and (via labse_filter.report) results/labse_filter_v3.md."""
import csv, json, random, re, shutil, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translation_checks import check, clean, foreign_scripts

ROOT = Path("data/processed")
FALLBACK = "richardyoung/qwen3-8b-abliterated:Q4_K_M"
FILES = ("translated_v2", "dev_translated_v2", "external_translated", "overrefusal_translated")
REVIEWS = ("translation_review_v2.csv", "translation_review_v2_abliterated.csv")
COLS = ["id", "orig_id", "source", "label", "lang", "model", "original", "translation", "reviewer", "verdict", "note"]
TAGS = ("truncated", "repetition", "answered", "wrong-script", "untranslated", "meaning")
LANGS = ("roman_ur", "ur", "mixed")


def read(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def refilter(name, t):
    src, backup = ROOT/f"{name}.jsonl", ROOT/f"{name}_pre_v3.jsonl"
    if not backup.exists():
        shutil.copyfile(src, backup)
    rows = read(backup)
    kept, rejected, stats = [], [], {"input": Counter(), "abliterated": Counter(), "cleaned": Counter(),
                                     "removed_by_checks": Counter(), "kept": Counter()}
    per_check = {}
    for r in rows:
        lang = r["lang"]; stats["input"][lang] += 1
        if r["model"] == FALLBACK:
            stats["abliterated"][lang] += 1; rejected.append({**r, "v3_reasons": ["abliterated"]}); continue
        text = clean(r["text"])
        if text != r["text"]:
            stats["cleaned"][lang] += 1
        reasons = check(text, r["original"])
        for c in reasons:
            per_check.setdefault(c, Counter())[lang] += 1
        if reasons:
            stats["removed_by_checks"][lang] += 1; rejected.append({**r, "text": text, "v3_reasons": reasons})
        else:
            stats["kept"][lang] += 1; kept.append({**r, "text": text})
    write(ROOT/f"{name}_rejected_v3.jsonl", rejected)
    # stage 2: roman_ur LaBSE threshold (fitted by labse_filter.fit on the review CSVs)
    scores = {s["id"]: s["score"] for s in read(ROOT/"meaning_scores_v3.jsonl") if s["file"] == name}
    labse = [{**r, "labse_score": scores[r["id"]], "reason": f"labse<{t}"} for r in kept
             if t is not None and r["lang"] == "roman_ur" and scores[r["id"]] < t]
    drop = {r["id"] for r in labse}; kept = [r for r in kept if r["id"] not in drop]
    write(ROOT/f"{name}_rejected_labse.jsonl", labse)
    # stage 3: letters outside Latin/Arabic script (unless the original has that script)
    script = [{**r, "foreign_scripts": fs} for r in kept for fs in [foreign_scripts(r["text"], r["original"])] if fs]
    drop = {r["id"] for r in script}; kept = [r for r in kept if r["id"] not in drop]
    write(ROOT/f"{name}_rejected_script.jsonl", script)
    write(src, kept)
    by = lambda rs: {**{l: sum(r["lang"] == l for r in rs) for l in LANGS}, "total": len(rs)}
    out = {k: {**{l: v[l] for l in LANGS}, "total": sum(v.values())} for k, v in stats.items()}
    out["kept_after_v3_checks"] = out.pop("kept")
    out["failing_each_check_(overlapping)"] = {c: {**{l: v[l] for l in LANGS}, "total": sum(v.values())}
                                              for c, v in sorted(per_check.items())}
    out["removed_by_labse_roman_ur"] = {**by(labse), "threshold": t}
    out["removed_by_script_check"] = {**by(script), "scripts": dict(Counter(s for r in script for s in r["foreign_scripts"]))}
    out["kept_final"] = by(kept)
    return out, kept


def review_summary():
    summary, catch = {}, {}
    for f in REVIEWS:
        rows = list(csv.DictReader((ROOT/f).open(encoding="utf-8-sig")))
        v = lambda r: r["verdict"].strip().lower()
        def good(key):
            groups = {}
            for r in rows: groups.setdefault(r[key], Counter())[v(r)] += 1
            return {k: {"good": c["good"], "bad": c["bad"], "good_share": round(c["good"] / sum(c.values()), 4)}
                    for k, c in sorted(groups.items())}
        tags = Counter(t for r in rows for t in TAGS if f"[{t}]" in r["note"].lower())
        summary[f] = {"rows": len(rows), "good": sum(v(r) == "good" for r in rows), "bad": sum(v(r) == "bad" for r in rows),
                      "by_lang": good("lang"), "by_label": good("label"), "by_model": good("model"),
                      "bad_note_tags": {t: tags[t] for t in TAGS}}
        hits = [(v(r), check(clean(r["translation"]), r["original"])) for r in rows]
        bad_tagged = [r for r in rows if v(r) == "bad" and any(f"[{t}]" in r["note"].lower() for t in TAGS[:5])]
        catch[f] = {"bad_rows": sum(x == "bad" for x, _ in hits),
                    "bad_caught_by_new_checks": sum(x == "bad" and bool(h) for x, h in hits),
                    "bad_with_machine_detectable_tag": len(bad_tagged),
                    "of_those_caught": sum(bool(check(clean(r["translation"]), r["original"])) for r in bad_tagged),
                    "good_rows": sum(x == "good" for x, _ in hits),
                    "good_wrongly_rejected": sum(x == "good" and bool(h) for x, h in hits),
                    "caught_by_check": dict(Counter(c for x, h in hits if x == "bad" for c in h))}
    return summary, catch


def sample_v3(kept):
    path = ROOT/"translation_review_v3.csv"
    if path.exists():  # never overwrite reviewer verdicts
        return {"kept_existing_file": True, **Counter(f"{r['lang']}/{r['label']}" for r in csv.DictReader(path.open(encoding="utf-8-sig")))}
    reviewed = {r["id"] for f in REVIEWS for r in csv.DictReader((ROOT/f).open(encoding="utf-8-sig"))}
    pool = [r for r in kept if r["model"] != FALLBACK and r["id"] not in reviewed]
    rng = random.Random(47); sample = []
    cells = [(l, lab) for l in LANGS for lab in ("attack", "benign")]
    for j, (l, lab) in enumerate(cells):
        cell = sorted((r for r in pool if r["lang"] == l and r["label"] == lab), key=lambda r: r["id"])
        sample += rng.sample(cell, 100 // len(cells) + (j < 100 % len(cells)))
    with (ROOT/"translation_review_v3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(COLS)
        for r in sample:
            w.writerow([r["id"], r["orig_id"], r["source"], r["label"], r["lang"], r["model"], r["original"], r["text"], "", "", ""])
    return dict(Counter(f"{r['lang']}/{r['label']}" for r in sample))


def main():
    import labse_filter
    summary, catch = review_summary()
    t = labse_filter.fit()["threshold"]
    files = {}
    for name in FILES:
        files[name], kept = refilter(name, t)
        if name == "translated_v2":
            sample = sample_v3(kept)
    passed_v2 = Counter(f"{r['lang']}/{r['label']}" for r in read(ROOT/"translated_v2.jsonl"))
    report = {"review_verdicts": summary, "new_checks_on_reviewed_rows": catch, "refilter_per_file": files,
              "translated_v2_kept_by_lang_label": dict(sorted(passed_v2.items())),
              "review_v3_sample": {"path": (ROOT/"translation_review_v3.csv").as_posix(), "cells": sample}}
    Path("results/translation_refilter_v3.md").write_text(
        "# Translation re-filter v3\n\nGenerated by `scripts/refilter_translations.py`. No re-translation: existing "
        "outputs re-checked with `scripts/translation_checks.py` (truncation, repetition, Devanagari, untranslated, "
        "answered; /no_think and think tags stripped), then the roman_ur LaBSE threshold, then the script check "
        "(letters outside Latin/Arabic). All abliterated-model rows dropped. Truncation uses the heuristic "
        "(Ollama done_reason was not stored).\n\n```json\n" + json.dumps(report, indent=2, ensure_ascii=False) + "\n```\n",
        encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    labse_filter.report()


if __name__ == "__main__":
    main()
