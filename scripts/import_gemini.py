"""Import Gemini translations and run the filter chain (qwen files are not touched).

  python -m scripts.import_gemini    # in the training image (LaBSE on GPU)

1. data/processed/translated_full_dedup.jsonl (one row per (orig_id, lang), asserted) is split by `set` into
   {translated_v2,dev_translated_v2,external_translated,overrefusal_translated}_gemini_pre.jsonl in the qwen schema
   (metadata copied from the qwen records of the same original; id = <orig_id>-<lang>-gemini).
2. Review summary of translation_review_gemini.csv -> results/translation_gemini_review.md.
3. LaBSE thresholds per language (labse_filter.fit_balanced: qwen review rows + Gemini review rows, balanced
   accuracy, capped at 2% of the language's Gemini rows).
4. Filter chain, in order: original validator (validate_basic; every qwen output passed it) -> v3 checks
   (clean + check) -> script check -> LaBSE (per-language threshold). Kept -> {name}_gemini.jsonl;
   removed -> {name}_gemini_rejected.jsonl (stage, reasons).
5. Pass rates per set x lang x label next to qwen, LaBSE drops old vs new, missing pairs -> results/translation_gemini_v2.md.
The review sample translation_review_gemini.csv is drawn once and never overwritten."""
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
SCORES = ROOT/"meaning_scores_gemini.jsonl"
OLD_THRESHOLD = {"roman_ur": 0.5168}  # fitted on qwen reviews only (translation_gemini_v1)
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
    out, missing = {}, {}
    for setname, name in SETS.items():
        attempted = qwen_attempted(name)
        meta = {r["orig_id"]: r for r in attempted}
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
        have = {(r["orig_id"], r["lang"]) for r in part}
        missing[setname] = sorted(f"{o}-{l}" for o, l in {(r["orig_id"], r["lang"]) for r in attempted} - have)
        out[name] = part
    return out, missing


def labse_scores(parts):
    """LaBSE cosine for every Gemini row (all languages); cached by id in meaning_scores_gemini.jsonl."""
    scores = {s["id"]: s["score"] for s in read(SCORES)}
    todo = [r for part in parts.values() for r in part if r["id"] not in scores]
    if todo:
        from meaning_scores import cosine
        scores.update(zip((r["id"] for r in todo), cosine([(r["original"], r["text"]) for r in todo])))
        write(SCORES, [{"id": k, "score": v} for k, v in scores.items()])
    return scores


def review_summary():
    rows = list(csv.DictReader(REVIEW.open(encoding="utf-8-sig")))
    v = lambda r: r["verdict"].strip().lower()
    cell = {}
    for r in rows: cell.setdefault(f"{r['lang']}/{r['label']}", Counter())[v(r)] += 1
    out = {"rows": len(rows), "verdicts": dict(Counter(v(r) for r in rows)), "reviewers": dict(Counter(r["reviewer"] for r in rows)),
           "good_rate_per_lang_label": {k: {"good": c["good"], "n": sum(c.values()), "rate": round(c["good"] / sum(c.values()), 4)}
                                        for k, c in sorted(cell.items())},
           "notes_flagging_labels": [{"id": r["id"], "note": r["note"]} for r in rows if "label" in r["note"].lower()]}
    lines = ["# Gemini translation review", "", f"Source: `{REVIEW.as_posix()}` ({out['rows']} rows). Reviewer field: "
             f"{json.dumps(out['reviewers'])} — machine-suggested verdicts unless a human edited them.", "",
             "| Lang/label | Good | n | Good rate |", "|---|---:|---:|---:|"]
    for k, x in out["good_rate_per_lang_label"].items():
        lines.append(f"| {k} | {x['good']} | {x['n']} | {x['rate']:.1%} |")
    lines += ["", f"Overall: {json.dumps(out['verdicts'])}", "",
              "Rows whose note questions the source label: " + json.dumps(out["notes_flagging_labels"], ensure_ascii=False), ""]
    Path("results/translation_gemini_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def chain(rows, scores, thresholds):
    kept, rejected = [], []
    for r in rows:
        text = clean(r["text"]); r = {**r, "text": text}
        t = thresholds.get(r["lang"])
        for stage, reasons in (("validator", lambda: validate_basic(text, r["lang"], r["original"])),
                               ("v3_checks", lambda: check(text, r["original"])),
                               ("script_check", lambda: foreign_scripts(text, r["original"])),
                               ("labse", lambda: [f"labse<{t}"] if t is not None and scores[r["id"]] < t else [])):
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
    parts, missing = import_rows()
    scores = labse_scores(parts)
    review = review_summary()
    fits = {lang: labse_filter.fit_balanced(lang, scores) for lang in LANGS}
    thresholds = {lang: f["threshold"] for lang, f in fits.items()}
    table, stages, labse_drops, kept_train = {}, {}, {}, None
    for setname, name in SETS.items():
        kept, rejected = chain(parts[name], scores, thresholds)
        write(ROOT/f"{name}_gemini.jsonl", kept); write(ROOT/f"{name}_gemini_rejected.jsonl", rejected)
        if setname == "train":
            kept_train = kept
        reach = kept + [r for r in rejected if r["stage"] == "labse"]  # rows that reached the LaBSE stage
        labse_drops[setname] = {l: {"old": sum(r["lang"] == l and l in OLD_THRESHOLD and scores[r["id"]] < OLD_THRESHOLD[l] for r in reach),
                                    "new": sum(r["lang"] == l and scores[r["id"]] < thresholds[l] for r in reach),
                                    "reached_labse": sum(r["lang"] == l for r in reach)} for l in LANGS}
        attempted = Counter((r["lang"], r["label"]) for r in qwen_attempted(name))
        q_kept = Counter((r["lang"], r["label"]) for r in read(ROOT/f"{name}.jsonl"))
        g_in = Counter((r["lang"], r["label"]) for r in parts[name]); g_kept = Counter((r["lang"], r["label"]) for r in kept)
        table[setname] = {f"{l}/{lab}": {"attempted_pairs": attempted[(l, lab)], "gemini_returned": g_in[(l, lab)],
                                         "qwen_kept": q_kept[(l, lab)], "qwen_rate": round(q_kept[(l, lab)] / max(1, attempted[(l, lab)]), 4),
                                         "gemini_kept": g_kept[(l, lab)], "gemini_rate": round(g_kept[(l, lab)] / max(1, attempted[(l, lab)]), 4)}
                          for l in LANGS for lab in LABELS if attempted[(l, lab)]}
        stages[setname] = {st: {**{l: sum(r["lang"] == l for r in rejected if r["stage"] == st) for l in LANGS},
                                "reasons": dict(Counter(x for r in rejected if r["stage"] == st for x in r["reasons"]).most_common(8))}
                           for st in ("validator", "v3_checks", "script_check", "labse")}
    sample = review_sample(kept_train)
    totals = {k: sum(v[k] for s in table.values() for v in s.values()) for k in ("attempted_pairs", "gemini_returned", "qwen_kept", "gemini_kept")}
    out = {"source": str(SRC), "review": review, "labse_fits": fits, "labse_old": OLD_THRESHOLD, "labse_drops_old_vs_new": labse_drops,
           "totals": totals, "per_set_lang_label": table, "gemini_removed_per_stage": stages, "missing_pairs": missing,
           "review_sample": {"path": REVIEW.as_posix(), "cells": sample}}
    Path("results/translation_gemini_v2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# Gemini translations: refitted LaBSE, filter chain, qwen comparison (v2)", "",
             "Generated by `scripts/import_gemini.py`. Chain: original validator → v3 checks → script check → LaBSE with a "
             "per-language threshold. LaBSE fit (`labse_filter.fit_balanced`): qwen review rows (good + bad) + Gemini review rows "
             "(all good, claude-suggested), threshold maximising balanced accuracy, capped so it removes at most 2% of that "
             "language's Gemini rows. Gemini rows replace qwen rows for v3; qwen files are untouched and appear only for comparison.", "",
             "## LaBSE thresholds", "", "| Lang | Old | Balanced-accuracy t | 2% cap | Cap applied | New t | BA at new t | Fit rows (qwen good / qwen bad / gemini good) |",
             "|---|---:|---:|---:|---|---:|---:|---|"]
    for lang, f in fits.items():
        fr = f["fit_rows"]
        lines.append(f"| {lang} | {OLD_THRESHOLD.get(lang, 'none')} | {f['balanced_accuracy_threshold']} | {f['cap_2pct_of_gemini_rows']} | "
                     f"{'yes' if f['cap_applied'] else 'no'} | {f['threshold']} | {f['balanced_accuracy_at_threshold']} | "
                     f"{fr['qwen_good']} / {fr['qwen_bad']} / {fr['gemini_good']} |")
    lines += ["", "## LaBSE drops per split (rows reaching the LaBSE stage; old threshold vs new)", "",
              "| Split | Lang | Reached LaBSE | Dropped (old) | Dropped (new) |", "|---|---|---:|---:|---:|"]
    for setname, d in labse_drops.items():
        for l, x in d.items():
            lines.append(f"| {setname} | {l} | {x['reached_labse']} | {x['old'] if l in OLD_THRESHOLD else 'n/a'} | {x['new']} |")
    lines += ["", f"Totals: attempted {totals['attempted_pairs']}, Gemini returned {totals['gemini_returned']}, "
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
    lines += ["", f"## Missing Gemini pairs ({sum(len(v) for v in missing.values())}, skipped)", ""]
    lines += [f"- {s}: {', '.join(v) if v else 'none'}" for s, v in missing.items()]
    lines += ["", f"Review sample: `{REVIEW.as_posix()}` — {json.dumps(sample)}", ""]
    Path("results/translation_gemini_v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:30]), flush=True)


if __name__ == "__main__":
    main()
