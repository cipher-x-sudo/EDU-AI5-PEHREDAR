"""Phase C threshold/selection + Phase D evaluation for the v2 classifier -> results/clf_v2.md, results/clf_v2.json.

1. Each candidate (models/clf_v2_e1, models/clf_v2_e2): threshold at 2% benign FPR on dev_v2_threshold.jsonl
   (dev_public_v2 + dev_translated_v2 roman_ur/mixed), written into the model dir's training_report.json
   (the original F1 threshold is kept as f1_threshold). Per-language FPR at that threshold.
2. Pick the candidate with lower or_bench FPR among those whose unseen recall (bipia + injecagent) is equal
   (95% Wilson CIs overlap) or better.
3. Evaluate DeBERTa, v1b, v2, ensemble_routed (en -> DeBERTa, else v2), ensemble_max on English and
   translated (roman_ur, mixed) sets; ur only in an appendix. Every recall/FPR has counts and a Wilson 95% CI.
All non-English sets are machine-translated, not the human test set."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import DEBERTA_THRESHOLD, _load_classifier
from run_v1_evaluation import DATA, fpr_threshold, scored
from pehredar.dataset import load_jsonl

CANDIDATES = {"v2_e1": "models/clf_v2_e1", "v2_e2": "models/clf_v2_e2"}
V1B = "models/clf_v1b"
DEV = DATA / "dev_v2_threshold.jsonl"
MAIN_LANGS = ("roman_ur", "mixed")
EN_ROWS = [("external_eval", "external_eval.jsonl", None), ("bipia (unseen)", "indirect_eval.jsonl", "bipia"),
           ("injecagent (unseen)", "indirect_eval.jsonl", "injecagent"), ("llmail (seen)", "indirect_eval.jsonl", "llmail"),
           ("xstest FPR", "overrefusal_eval.jsonl", "xstest"), ("or_bench FPR", "overrefusal_eval.jsonl", "or_bench"),
           ("benign_email_probe FPR", "benign_email_probe.jsonl", None)]
TR_FILES = [("external_translated", "external_translated.jsonl"), ("overrefusal_translated FPR", "overrefusal_translated.jsonl"),
            ("dev_translated_v2 (threshold set)", "dev_translated_v2.jsonl")]
QUALITY = Path("results/labse_filter_v3.md")


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def metrics(preds):
    tp = sum(p["label"] == "attack" and p["pred"] for p in preds); a = sum(p["label"] == "attack" for p in preds)
    fp = sum(p["label"] == "benign" and p["pred"] for p in preds); b = sum(p["label"] == "benign" for p in preds)
    return {"attacks": a, "benign": b, "tp": tp, "fp": fp,
            "recall": round(tp / a, 4) if a else None, "recall_ci": wilson(tp, a),
            "fpr": round(fp / b, 4) if b else None, "fpr_ci": wilson(fp, b)}


def predictions(filename, detector, directory, threshold, source=None, lang=None):
    path = DATA / filename
    res = scored(path, detector, directory, threshold)
    out = []
    for row, p in zip(load_jsonl(path), res["predictions"]):
        assert row.id == p["id"]
        if (source is None or row.source == source) and (lang is None or row.lang == lang):
            out.append({"label": row.label, "lang": row.lang, "pred": p["risk"] >= threshold})
    return out


def set_threshold(directory):
    """2% benign FPR on the combined dev set -> training_report.json in the model dir."""
    res = scored(DEV, "classifier", directory, "dev_fpr_2pct_v2")
    t = fpr_threshold(res)
    card = (Path(directory) / "model_card.md").read_text(encoding="utf-8")
    report = json.JSONDecoder().raw_decode(card[card.find("{"):])[0]
    report.update({"f1_threshold": report["threshold"], "threshold": t,
                   "threshold_source": "2% benign FPR on dev_v2_threshold.jsonl (dev_public_v2 + dev_translated_v2 roman_ur/mixed)"})
    (Path(directory) / "training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _load_classifier.cache_clear()
    rows = load_jsonl(DEV)
    per_lang = {}
    for lang in ("en", *MAIN_LANGS):
        preds = [{"label": r.label, "pred": p["risk"] >= t} for r, p in zip(rows, res["predictions"]) if r.lang == lang]
        per_lang[lang] = metrics(preds)
    return t, report, {"overall": metrics([{"label": r.label, "pred": p["risk"] >= t} for r, p in zip(rows, res["predictions"])]),
                       "per_lang": per_lang}


def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def main():
    Path("results/cache").mkdir(parents=True, exist_ok=True)
    cands = {}
    for name, d in CANDIDATES.items():
        t, rep, dev = set_threshold(d)
        unseen = predictions("indirect_eval.jsonl", "classifier", d, t, "bipia") + predictions("indirect_eval.jsonl", "classifier", d, t, "injecagent")
        orb = predictions("overrefusal_eval.jsonl", "classifier", d, t, "or_bench")
        cands[name] = {"dir": d, "threshold": t, "f1_threshold": rep["f1_threshold"], "epochs": rep["epochs"],
                       "training_seconds": round(rep["training_seconds"]), "peak_vram_gb": rep.get("peak_vram_gb"),
                       "train_count": rep["train_count"], "encoder_version": rep["encoder_version"],
                       "dev_at_threshold": dev, "unseen": metrics(unseen), "or_bench": metrics(orb)}
    names = list(cands)
    ok = [n for n in names if all(cands[n]["unseen"]["recall"] >= cands[m]["unseen"]["recall"]
                                  or overlap(cands[n]["unseen"]["recall_ci"], cands[m]["unseen"]["recall_ci"]) for m in names)]
    chosen = min(ok or names, key=lambda n: (cands[n]["or_bench"]["fpr"], -cands[n]["unseen"]["recall"]))
    why = (f"{chosen}: or_bench FPR {cands[chosen]['or_bench']['fpr']} vs " +
           ", ".join(f"{n} {cands[n]['or_bench']['fpr']}" for n in names if n != chosen) +
           f"; unseen recall {cands[chosen]['unseen']['recall']} {cands[chosen]['unseen']['recall_ci']} vs " +
           ", ".join(f"{n} {cands[n]['unseen']['recall']} {cands[n]['unseen']['recall_ci']}" for n in names if n != chosen) +
           (" (equal or better: CIs overlap or higher)" if chosen in ok else " (no candidate met the recall condition; lowest or_bench FPR taken)"))
    v2 = cands[chosen]["dir"]; t2 = cands[chosen]["threshold"]
    v1b_t = _load_classifier(V1B)[3]
    models = {"deberta": ("deberta", None, DEBERTA_THRESHOLD), "v1b": ("classifier", V1B, v1b_t), "v2": ("classifier", v2, t2),
              "ensemble_routed": ("ensemble", v2, 1.0), "ensemble_max": ("ensemble_max", v2, 1.0)}
    main_rows, lang_rows, appendix = {}, {}, {}
    for m, (det, d, t) in models.items():
        main_rows[m] = {label: metrics(predictions(f, det, d, t, src)) for label, f, src in EN_ROWS}
        for label, f in TR_FILES:
            main_rows[m][f"{label} (roman_ur+mixed)"] = metrics([p for lang in MAIN_LANGS for p in predictions(f, det, d, t, lang=lang)])
            for lang in MAIN_LANGS:
                lang_rows.setdefault(lang, {}).setdefault(m, {})[label] = metrics(predictions(f, det, d, t, lang=lang))
            appendix.setdefault(m, {})[label] = metrics(predictions(f, det, d, t, lang="ur"))
    out = {"candidates": cands, "chosen": chosen, "why": why, "models": {m: {"detector": a, "dir": b, "threshold": c} for m, (a, b, c) in models.items()},
           "main": main_rows, "per_language": lang_rows, "appendix_ur": appendix}
    Path("results/clf_v2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    render(out)


def cell(m, key):
    v = m[key]
    if v is None:
        return "n/a"
    k, n = (m["tp"], m["attacks"]) if key == "recall" else (m["fp"], m["benign"])
    ci = m[f"{key}_ci"]
    return f"{v:.3f} ({k}/{n}) [{ci[0]:.3f}–{ci[1]:.3f}]"


def table(rows_by_model, title):
    lines = [f"### {title}", "", "| Eval row | Model | Recall (tp/attacks) [95% CI] | FPR (fp/benign) [95% CI] |", "|---|---|---|---|"]
    labels = list(next(iter(rows_by_model.values())))
    for label in labels:
        for m, rows in rows_by_model.items():
            lines.append(f"| {label} | {m} | {cell(rows[label], 'recall')} | {cell(rows[label], 'fpr')} |")
    return lines + [""]


def compare(out):
    """Numbers-only: on roman_ur / mixed, does v2 or an ensemble beat DeBERTa in recall at comparable FPR?"""
    lines = ["## Generated comparison: roman_ur / mixed vs DeBERTa", "",
             "Rule: a model beats DeBERTa if its recall is higher with non-overlapping 95% CIs and its FPR on the same set "
             "and on overrefusal_translated is at most DeBERTa's + 0.02. Higher recall with overlapping CIs is reported as "
             "\"higher, not significant\". ur is in the appendix only.", ""]
    for lang in MAIN_LANGS:
        rows = out["per_language"][lang]
        for label in ("external_translated", "dev_translated_v2 (threshold set)"):
            d = rows["deberta"][label]; dor = rows["deberta"]["overrefusal_translated FPR"]
            for m in ("v2", "ensemble_routed", "ensemble_max"):
                x = rows[m][label]; xor = rows[m]["overrefusal_translated FPR"]
                if x["recall"] is None or d["recall"] is None:
                    continue
                fpr_ok = all(a["fpr"] is None or b["fpr"] is None or a["fpr"] <= b["fpr"] + 0.02 for a, b in ((x, d), (xor, dor)))
                if x["recall"] > d["recall"] and not overlap(x["recall_ci"], d["recall_ci"]):
                    verdict = "beats DeBERTa" if fpr_ok else "higher recall, but FPR not comparable"
                elif x["recall"] > d["recall"]:
                    verdict = "higher, not significant" + ("" if fpr_ok else "; FPR not comparable")
                else:
                    verdict = "does not beat DeBERTa"
                lines.append(f"- {lang} / {label} / {m}: recall {cell(x, 'recall')} vs DeBERTa {cell(d, 'recall')}; "
                             f"FPR same set {cell(x, 'fpr')} vs {cell(d, 'fpr')}; overrefusal_translated FPR {cell(xor, 'fpr')} "
                             f"vs {cell(dor, 'fpr')} → {verdict}")
    return lines + [""]


def render(out):
    q = json.loads(QUALITY.read_text(encoding="utf-8").split("```json")[1].split("```")[0])["post_filter_estimate_v3_sample"]
    est = lambda l: f"{q[l]['good']}/{q[l]['passing']} = {q[l]['good_rate']:.1%}"
    c = out["candidates"]
    lines = ["# Classifier v2 (XLM-R base) evaluation", "",
             "## Limitations (read first)", "",
             "- **All non-English eval sets are machine-translated** (qwen3:8b, filtered), not the human test set.",
             f"- Estimated translation quality after all filters (human review of the v3 sample, `results/labse_filter_v3.md`): "
             f"roman_ur {est('roman_ur')} (**optimistic**: the roman_ur LaBSE threshold was fitted on the same review rows), "
             f"mixed {est('mixed')}, ur {est('ur')} (ur reviewed 55.9% good before the script check; excluded from training "
             "and from the main results).",
             "- `dev_translated_v2` is part of the threshold set, so v2 numbers on it are in-sample for the threshold.",
             "- Translated attack counts per language are small; see the CIs.",
             "- No model was promoted to the gateway.", "",
             "## Candidates (Phase C)", "",
             "| Candidate | Epochs | Threshold (2% dev FPR) | F1 threshold | Train rows | Training time | Peak VRAM | Dev FPR en / roman_ur / mixed | Unseen recall | or_bench FPR |",
             "|---|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for n, x in c.items():
        pl = x["dev_at_threshold"]["per_lang"]
        lines.append(f"| {n} | {x['epochs']} | {x['threshold']:.4f} | {x['f1_threshold']:.4f} | {x['train_count']} | "
                     f"{x['training_seconds']} s | {x['peak_vram_gb']} GB | " + " / ".join(cell(pl[l], 'fpr') for l in ("en", *MAIN_LANGS)) +
                     f" | {cell(x['unseen'], 'recall')} | {cell(x['or_bench'], 'fpr')} |")
    lines += ["", f"Chosen: **{out['chosen']}** — {out['why']}", "",
              "Models: " + "; ".join(f"`{m}` {v['detector']} {v['dir'] or ''} threshold {v['threshold']:.4f}" for m, v in out["models"].items()) +
              ". `ensemble_routed`: en → DeBERTa, roman_ur/mixed/ur → v2; `ensemble_max`: attack if either is over its own threshold "
              "(risk = score / threshold, so ensemble threshold 1.0).", "", "## Main results", ""]
    lines += table(out["main"], "English sets and translated sets (roman_ur + mixed combined)")
    lines += ["## Per-language results (translated sets)", ""]
    for lang in MAIN_LANGS:
        lines += table(out["per_language"][lang], lang)
    lines += compare(out)
    lines += ["## Appendix: ur — low translation quality (55.9% good)", ""]
    lines += table(out["appendix_ur"], "ur (not used for training; machine-translated, low quality)")
    Path("results/clf_v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]), flush=True)


if __name__ == "__main__":
    main()
