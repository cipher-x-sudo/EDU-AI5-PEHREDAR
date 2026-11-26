"""Import Gemini translations and run the filter chain (qwen files are not touched).

  python -m scripts.import_gemini    # in the training image (LaBSE on GPU)

1. data/processed/translated_full_dedup.jsonl (one row per (orig_id, lang), asserted) is split by `set` into
   {translated_v2,dev_translated_v2,external_translated,overrefusal_translated}_gemini_pre.jsonl in the qwen schema
   (metadata copied from the qwen records of the same original; id = <orig_id>-<lang>-gemini).
2. Filter chain, in order: original validator (validate_basic; every qwen output passed it) -> v3 checks
   (clean + check) -> script check -> roman_ur LaBSE (threshold fitted on the reviewed qwen rows,
   labse_filter.fit). Kept -> {name}_gemini.jsonl; removed -> {name}_gemini_rejected.jsonl (stage, reasons).
3. Pass rates per set x lang x label side by side with qwen (same source pairs) -> results/translation_gemini_v1.md.
4. translation_review_gemini.csv: 100 passed train rows, balanced lang x label (17/17/17/17/16/16), empty verdicts;
   never overwritten once it exists."""
import csv, json, random, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translate_ru import validate_basic
from translation_checks import check, clean, foreign_scripts

ROOT = Path("data/processed")
SRC = ROOT/"translated_full_dedup.jsonl"
SETS = {"train": "translated_v2", "dev": "dev_translated_v2", "external": "external_translated", "overrefusal": "overrefusal_translated"}
LANGS = ("roman_ur", "ur", "mixed")
LABELS = ("attack", "benign")
META = ("type", "orig_split", "usage", "redistributable", "license", "orig_label")
REVIEW = ROOT/"translation_review_gemini.csv"
COLS = ["id", "orig_id", "source", "label", "lang", "model", "original", "translation", "reviewer", "verdict", "note"]


def read(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def write(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def qwen_attempted(name):
    return read(ROOT/f"{name}_pre_v3.jsonl") + read(ROOT/f"{name}_failures.jsonl")


def import_rows():
    rows = read(SRC)
    pairs = Counter((r["orig_id"], r["lang"]) for r in rows)
    assert max(pairs.values()) == 1, f"duplicate (orig_id, lang): {[k for k, v in pairs.items() if v > 1][:5]}"
    out = {}
    for setname, name in SETS.items():
        meta = {r["orig_id"]: r for r in qwen_attempted(name)}
        part = []
        for r in rows:
            if r["set"] != setname:
                continue
            m = meta[r["orig_id"]]
            assert (m["label"], m["source"], m["split_group"]) == (r["label"], r["source"], r["split_group"]), r["id"]
            part.append({"id": f"{r['orig_id']}-{r['lang']}-gemini", "text": r["translation"], "orig_id": r["orig_id"],
                         "lang": r["lang"], "label": r["label"], "source": r["source"], "split_group": r["split_group"],
                         "turns": None, **{k: m.get(k) for k in META}, "original": r["original"],
                         "model": r["model"], "provider": r["provider"], "seconds": None})
        write(ROOT/f"{name}_gemini_pre.jsonl", part)
        out[name] = part
    return out


def labse_scores(parts):
    from meaning_scores import cosine
    rows = [r for part in parts.values() for r in part if r["lang"] == "roman_ur"]
    scores = dict(zip((r["id"] for r in rows), cosine([(r["original"], r["text"]) for r in rows])))
    write(ROOT/"meaning_scores_gemini.jsonl", [{"id": k, "score": v} for k, v in scores.items()])
    return scores


def chain(rows, scores, t):
    kept, rejected = [], []
    for r in rows:
        text = clean(r["text"]); r = {**r, "text": text}
        for stage, reasons in (("validator", lambda: validate_basic(text, r["lang"], r["original"])),
                               ("v3_checks", lambda: check(text, r["original"])),
                               ("script_check", lambda: foreign_scripts(text, r["original"])),
                               ("labse_roman_ur", lambda: [f"labse<{t}"] if r["lang"] == "roman_ur" and scores[r["id"]] < t else [])):
            why = reasons()
            if why:
                rejected.append({**r, "stage": stage, "reasons": why}); break
        else:
            kept.append(r)
    return kept, rejected


def review_sample(kept):
    if REVIEW.exists():  # holds reviewer verdicts once filled in
        return {"kept_existing_file": True}
    rng = random.Random(48); sample = []
    cells = [(l, lab) for l in LANGS for lab in LABELS]
    for j, (l, lab) in enumerate(cells):
        cell = sorted((r for r in kept if r["lang"] == l and r["label"] == lab), key=lambda r: r["id"])
        sample += rng.sample(cell, 100 // len(cells) + (j < 100 % len(cells)))
    with REVIEW.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(COLS)
        for r in sample:
            w.writerow([r["id"], r["orig_id"], r["source"], r["label"], r["lang"], r["model"], r["original"], r["text"], "", "", ""])
    return dict(Counter(f"{r['lang']}/{r['label']}" for r in sample))


def main():
    import labse_filter
    parts = import_rows()
    scores = labse_scores(parts)
    t = labse_filter.fit()["threshold"]
    table, stages, kept_train = {}, {}, None
    for setname, name in SETS.items():
        kept, rejected = chain(parts[name], scores, t)
        write(ROOT/f"{name}_gemini.jsonl", kept); write(ROOT/f"{name}_gemini_rejected.jsonl", rejected)
        if setname == "train":
            kept_train = kept
        attempted = Counter((r["lang"], r["label"]) for r in qwen_attempted(name))
        q_kept = Counter((r["lang"], r["label"]) for r in read(ROOT/f"{name}.jsonl"))
        g_in = Counter((r["lang"], r["label"]) for r in parts[name]); g_kept = Counter((r["lang"], r["label"]) for r in kept)
        table[setname] = {f"{l}/{lab}": {"attempted_pairs": attempted[(l, lab)], "gemini_returned": g_in[(l, lab)],
                                         "qwen_kept": q_kept[(l, lab)], "qwen_rate": round(q_kept[(l, lab)] / max(1, attempted[(l, lab)]), 4),
                                         "gemini_kept": g_kept[(l, lab)], "gemini_rate": round(g_kept[(l, lab)] / max(1, attempted[(l, lab)]), 4)}
                          for l in LANGS for lab in LABELS if attempted[(l, lab)]}
        stages[setname] = {st: {**{l: sum(r["lang"] == l for r in rejected if r["stage"] == st) for l in LANGS},
                                "reasons": dict(Counter(x for r in rejected if r["stage"] == st for x in r["reasons"]).most_common(8))}
                           for st in ("validator", "v3_checks", "script_check", "labse_roman_ur")}
    sample = review_sample(kept_train)
    totals = {k: sum(v[k] for s in table.values() for v in s.values()) for k in ("attempted_pairs", "gemini_returned", "qwen_kept", "gemini_kept")}
    out = {"source": str(SRC), "labse_roman_ur_threshold": t, "totals": totals, "per_set_lang_label": table,
           "gemini_removed_per_stage": stages, "review_sample": {"path": REVIEW.as_posix(), "cells": sample}}
    Path("results/translation_gemini_v1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# Gemini translations vs qwen: filter chain pass rates", "",
             f"Generated by `scripts/import_gemini.py`. Gemini (`gemini-4-hydrogen-xhigh`) translated the same (original, language) "
             f"pairs qwen attempted; {totals['attempted_pairs'] - totals['gemini_returned']} pairs are missing from the Gemini file "
             "(counted as not passed). Rate = rows kept after the full chain / attempted pairs. Gemini chain: original validator → "
             f"v3 checks → script check → roman_ur LaBSE (threshold {t}, fitted on reviewed qwen rows). Qwen kept = current qwen "
             "files (qwen3:8b only; abliterated rows dropped; same checks, LaBSE before the script check). Machine-filtered only; "
             "no Gemini row has been human-reviewed yet.", "",
             f"Totals: attempted {totals['attempted_pairs']}, Gemini returned {totals['gemini_returned']}, "
             f"qwen kept {totals['qwen_kept']} ({totals['qwen_kept'] / totals['attempted_pairs']:.1%}), "
             f"Gemini kept {totals['gemini_kept']} ({totals['gemini_kept'] / totals['attempted_pairs']:.1%}).", "",
             "| Set | Lang/label | Attempted | Qwen kept | Qwen rate | Gemini kept | Gemini rate |", "|---|---|---:|---:|---:|---:|---:|"]
    for setname, cells in table.items():
        for c, v in cells.items():
            lines.append(f"| {setname} | {c} | {v['attempted_pairs']} | {v['qwen_kept']} | {v['qwen_rate']:.1%} | {v['gemini_kept']} | {v['gemini_rate']:.1%} |")
    lines += ["", "## Gemini rows removed per stage (roman_ur / ur / mixed; top reasons)", "",
              "| Set | Stage | roman_ur | ur | mixed | Reasons |", "|---|---|---:|---:|---:|---|"]
    for setname, st in stages.items():
        for stage, v in st.items():
            lines.append(f"| {setname} | {stage} | {v['roman_ur']} | {v['ur']} | {v['mixed']} | {json.dumps(v['reasons'], ensure_ascii=False)} |")
    lines += ["", f"Review sample: `{REVIEW.as_posix()}` — {json.dumps(sample)}", ""]
    Path("results/translation_gemini_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]), flush=True)


if __name__ == "__main__":
    main()
