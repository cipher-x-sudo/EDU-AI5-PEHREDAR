"""v3 evaluation -> results/clf_v3_metrics.json, results/clf_v3.md (every number in the .md comes from the JSON).

  python -m scripts.run_v3_evaluation          # training image, GPU; mount ./pehredar (needs pehredar.langid.detect_lang)
  python -m scripts.run_v3_evaluation --render # rebuild the .md from the JSON

1. Epoch choice: each models/clf_v3_e{N} is scored on dev_v3.jsonl; its threshold is the 2% benign-FPR point on dev
   (written to that dir's training_report.json); the best epoch has the highest dev recall at that threshold.
2. Systems: DeBERTa (0.5), v2 (models/clf_v2_e2, 0.7383), v3, routed_v2 / routed_v3 (router = langid_v1 on the
   L0-normalised text: en -> DeBERTa, else -> v2 / v3), routed_v3_oracle (dataset language label), max(DeBERTa, v3).
   Routed and max systems score = model score / its threshold (attack if >= 1).
3. Per language (en, roman_ur, ur, mixed): test (external_eval + external_translated_gemini) and overrefusal
   (xstest + or_bench + overrefusal_translated_gemini): recall, FPR, F1, AUROC, counts, Wilson 95% CIs.
   English extra sets: bipia, injecagent, llmail, benign_email_probe. Test metrics with and without label-audit flags.
4. McNemar exact test (paired correctness) routed_v3 vs DeBERTa and routed_v3 vs routed_v2.
5. Latency p50/p95 per system, batch 1, GPU and CPU."""
import csv, json, math, random, statistics, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import DEBERTA_THRESHOLD, _load_classifier
from run_v1_evaluation import fpr_threshold, scored
from run_v2_evaluation import wilson
from pehredar.dataset import load_jsonl
from pehredar.langid import detect_lang
from pehredar.normalizer import normalize_text

DATA = Path("data/processed")
EPOCHS = [f"models/clf_v3_e{n}" for n in (1, 2, 3)]
V2 = "models/clf_v2_e2"
LANGS = ("en", "roman_ur", "ur", "mixed")
SETS = {"test": ["external_eval.jsonl", "external_translated_gemini.jsonl"],
        "overrefusal": ["overrefusal_eval.jsonl", "overrefusal_translated_gemini.jsonl"]}
EXTRA = [("bipia (unseen)", "indirect_eval.jsonl", "bipia"), ("injecagent (unseen)", "indirect_eval.jsonl", "injecagent"),
         ("llmail (seen)", "indirect_eval.jsonl", "llmail"), ("benign_email_probe", "benign_email_probe.jsonl", None)]
SYSTEMS = ("deberta", "v2", "v3", "routed_v2", "routed_v3", "routed_v3_oracle", "max_deberta_v3")
OUT_JSON = Path("results/clf_v3_metrics.json")
OUT_MD = Path("results/clf_v3.md")


def risks(path, detector, directory):
    res = scored(path, detector, directory, "raw")
    return [p["risk"] for p in res["predictions"]]


def choose_epoch():
    rows = load_jsonl(DATA / "dev_v3.jsonl")
    out = {}
    for d in EPOCHS:
        if not Path(d).exists():
            continue
        res = scored(DATA / "dev_v3.jsonl", "classifier", d, "raw")
        t = fpr_threshold(res)
        preds = [(r.label, r.lang, p["risk"] >= t) for r, p in zip(rows, res["predictions"])]
        recall = sum(l == "attack" and h for l, _, h in preds) / sum(l == "attack" for l, _, _ in preds)
        per_lang = {lang: {"fp": sum(l == "benign" and h for l, g, h in preds if g == lang),
                           "benign": sum(l == "benign" for l, g, _ in preds if g == lang)} for lang in LANGS}
        for v in per_lang.values():
            v["fpr"] = round(v["fp"] / max(1, v["benign"]), 4); v["ci"] = wilson(v["fp"], v["benign"])
        card = (Path(d) / "model_card.md").read_text(encoding="utf-8")
        report = json.JSONDecoder().raw_decode(card[card.find("{"):])[0]
        report.update({"f1_threshold": report["threshold"], "threshold": t, "threshold_source": "2% benign FPR on dev_v3.jsonl"})
        (Path(d) / "training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        out[d] = {"epoch": report["epochs"], "threshold": t, "dev_recall_at_2pct_fpr": round(recall, 4),
                  "dev_attacks": sum(l == "attack" for l, _, _ in preds), "dev_per_lang_fpr": per_lang,
                  "training_seconds_cumulative": round(report["training_seconds"]), "peak_vram_gb": report.get("peak_vram_gb")}
    _load_classifier.cache_clear()
    best = max(out, key=lambda d: (out[d]["dev_recall_at_2pct_fpr"], -out[d]["epoch"]))
    return best, out


def auroc(labels, scores):
    pos = [s for l, s in zip(labels, scores) if l == "attack"]; neg = [s for l, s in zip(labels, scores) if l == "benign"]
    if not pos or not neg:
        return None
    from sklearn.metrics import roc_auc_score
    return round(float(roc_auc_score([1] * len(pos) + [0] * len(neg), pos + neg)), 4)


def metrics(rows, system):
    a = [r for r in rows if r["label"] == "attack"]; b = [r for r in rows if r["label"] == "benign"]
    tp = sum(r["pred"][system] for r in a); fp = sum(r["pred"][system] for r in b)
    return {"attacks": len(a), "benign": len(b), "tp": tp, "fp": fp,
            "recall": round(tp / len(a), 4) if a else None, "recall_ci": wilson(tp, len(a)),
            "fpr": round(fp / len(b), 4) if b else None, "fpr_ci": wilson(fp, len(b)),
            "f1": round(2 * tp / (2 * tp + fp + len(a) - tp), 4) if a else None,
            "auroc": auroc([r["label"] for r in rows], [r["score"][system] for r in rows])}


def score_rows(files, v3, t3, t2, source=None, flagged=frozenset()):
    rows = []
    for f in files:
        path = DATA / f
        recs = load_jsonl(path)
        deb, s2, s3 = risks(path, "deberta", None), risks(path, "classifier", V2), risks(path, "classifier", v3)
        for r, d, x2, x3 in zip(recs, deb, s2, s3):
            if source and r.source != source:
                continue
            routed_lang = detect_lang(normalize_text(r.input_text()))[0]
            rd, r2, r3 = d / DEBERTA_THRESHOLD, x2 / t2, x3 / t3
            score = {"deberta": d, "v2": x2, "v3": x3, "routed_v2": rd if routed_lang == "en" else r2,
                     "routed_v3": rd if routed_lang == "en" else r3, "routed_v3_oracle": rd if r.lang == "en" else r3,
                     "max_deberta_v3": max(rd, r3)}
            thresholds = {"deberta": DEBERTA_THRESHOLD, "v2": t2, "v3": t3}
            rows.append({"id": r.id, "label": r.label, "lang": r.lang, "routed_lang": routed_lang, "flagged": r.id in flagged,
                         "score": score, "pred": {s: score[s] >= thresholds.get(s, 1.0) for s in SYSTEMS}})
    return rows


def mcnemar(rows, a, b):
    from scipy.stats import binomtest
    right = lambda r, s: r["pred"][s] == (r["label"] == "attack")
    n01 = sum(right(r, a) and not right(r, b) for r in rows); n10 = sum(right(r, b) and not right(r, a) for r in rows)
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return {"a_right_b_wrong": n01, "b_right_a_wrong": n10, "p_value": round(float(p), 6), "significant_0.05": bool(p < 0.05)}


def latency(v3, n_gpu=200, n_cpu=100):
    import torch
    from pehredar.l2 import L2
    texts = [r.input_text() for f in SETS["test"] for r in load_jsonl(DATA / f)]
    random.Random(42).shuffle(texts)
    out = {}
    for device, n in (("cuda", n_gpu), ("cpu", n_cpu)):
        if device == "cuda" and not torch.cuda.is_available():
            continue
        m2, m3 = L2().load(V2, device), L2().load(v3, device)
        deb, v2fn, v3fn = m3.models["deberta"].fn, m2.models["xlmr"].fn, m3.models["xlmr"].fn
        def routed(fn):
            return lambda t: deb(t) if detect_lang(t)[0] == "en" else fn(t)
        systems = {"deberta": deb, "v2": v2fn, "v3": v3fn, "routed_v2": routed(v2fn), "routed_v3": routed(v3fn),
                   "max_deberta_v3": lambda t: max(deb(t), v3fn(t)), "router_only": detect_lang}
        res = {}
        for name, fn in systems.items():
            fn(texts[0])  # warm-up
            times = []
            for t in texts[:n]:
                t = normalize_text(t); started = time.perf_counter(); fn(t); times.append((time.perf_counter() - started) * 1000)
            times.sort()
            res[name] = {"p50_ms": round(times[len(times) // 2], 2), "p95_ms": round(times[int(.95 * len(times))], 2), "n": len(times)}
        out[device] = res
        del m2, m3
        if device == "cuda":
            torch.cuda.empty_cache()
    return out


def main():
    Path("results/cache").mkdir(parents=True, exist_ok=True)
    best, epochs = choose_epoch()
    t3 = epochs[best]["threshold"]; t2 = _load_classifier(V2)[3]
    flagged = {r["id"] for r in csv.DictReader((DATA / "label_audit.csv").open(encoding="utf-8")) if r["split"] in ("test", "overrefusal", "email_probe")}
    data = {name: score_rows(files, best, t3, t2, flagged=flagged) for name, files in SETS.items()}
    out = {"best_epoch_dir": best, "epochs": epochs, "thresholds": {"deberta": DEBERTA_THRESHOLD, "v2": t2, "v3": t3},
           "main": {}, "test_without_label_audit_flags": {}, "extra_en": {}, "significance": {}, "router": {}}
    for name, rows in data.items():
        for lang in LANGS:
            rs = [r for r in rows if r["lang"] == lang]
            out["main"][f"{name}|{lang}"] = {s: metrics(rs, s) for s in SYSTEMS}
            if name == "test":
                clean = [r for r in rs if not r["flagged"]]
                out["test_without_label_audit_flags"][lang] = {"removed_benign": len(rs) - len(clean),
                                                               **{s: metrics(clean, s) for s in ("deberta", "routed_v3", "v3")}}
            out["router"][f"{name}|{lang}"] = {"n": len(rs), "routed_as": dict(sorted({k: sum(r["routed_lang"] == k for r in rs) for k in LANGS}.items()))}
    for lang in LANGS:
        rs = [r for rows in data.values() for r in rows if r["lang"] == lang]
        out["significance"][lang] = {"routed_v3_vs_deberta": mcnemar(rs, "routed_v3", "deberta"),
                                     "routed_v3_vs_routed_v2": mcnemar(rs, "routed_v3", "routed_v2")}
    for label, f, src in EXTRA:
        rows = score_rows([f], best, t3, t2, source=src)
        out["extra_en"][label] = {s: metrics(rows, s) for s in SYSTEMS}
    out["latency"] = latency(best)
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    render(out)


def cell(m, key):
    v = m.get(key)
    if v is None:
        return "n/a"
    k, n = (m["tp"], m["attacks"]) if key == "recall" else (m["fp"], m["benign"])
    lo, hi = m[f"{key}_ci"]
    return f"{v:.3f} ({k}/{n}) [{lo:.3f}–{hi:.3f}]"


def conclusion(out):
    parts = []
    for lang in ("roman_ur", "ur", "mixed"):
        o = out["main"][f"overrefusal|{lang}"]; t = out["main"][f"test|{lang}"]; sig = out["significance"][lang]["routed_v3_vs_deberta"]
        p = "p<1e-6" if sig["p_value"] < 1e-6 else f"p={sig['p_value']:.3g}"
        parts.append(f"on {lang}, routed_v3 over-blocks {o['routed_v3']['fpr']:.1%} of benign overrefusal prompts vs DeBERTa "
                     f"{o['deberta']['fpr']:.1%} (routed_v2 {o['routed_v2']['fpr']:.1%}), with test recall {t['routed_v3']['recall']:.1%} "
                     f"vs DeBERTa {t['deberta']['recall']:.1%} at test FPR {t['routed_v3']['fpr']:.1%} vs {t['deberta']['fpr']:.1%}; "
                     f"per-row correctness differs {'significantly' if sig['significant_0.05'] else 'not significantly'} "
                     f"(McNemar {p}; routed_v3 right where DeBERTa wrong {sig['a_right_b_wrong']}, the reverse {sig['b_right_a_wrong']})")
    en = out["main"]["test|en"]; eo = out["main"]["overrefusal|en"]
    return ("In plain terms: " + "; ".join(parts) + f". On English, routed_v3 sends text to DeBERTa, so it keeps DeBERTa's behaviour "
            f"(test recall {en['routed_v3']['recall']:.1%}, overrefusal FPR {eo['routed_v3']['fpr']:.1%}); v3 alone on English has "
            f"recall {en['v3']['recall']:.1%} and overrefusal FPR {eo['v3']['fpr']:.1%}. All non-English sets are Gemini machine "
            "translations (review verdicts machine-suggested), not the human test set, so these numbers estimate rather than prove "
            "behaviour on real Roman Urdu / Urdu traffic.")


def render(out):
    ep = out["epochs"]
    lines = ["# Classifier v3 (Gemini data) evaluation", "",
             "All numbers come from `results/clf_v3_metrics.json` (generated by `scripts/run_v3_evaluation.py`). Non-English sets are "
             "Gemini machine translations, not the human test set. Thresholds: chosen on dev at 2% benign FPR; nothing tuned on test.", "",
             "## Conclusion", "", conclusion(out), "", "## v3 epochs (dev_v3)", "",
             "| Checkpoint | Epoch | Threshold (2% dev FPR) | Dev recall at threshold | Dev FPR en / roman_ur / ur / mixed | Training time (cumulative) | Peak VRAM |",
             "|---|---:|---:|---:|---|---:|---:|"]
    for d, x in ep.items():
        fpr = " / ".join(f"{x['dev_per_lang_fpr'][l]['fpr']:.3f} ({x['dev_per_lang_fpr'][l]['fp']}/{x['dev_per_lang_fpr'][l]['benign']})" for l in LANGS)
        lines.append(f"| {d}{' **(best)**' if d == out['best_epoch_dir'] else ''} | {x['epoch']} | {x['threshold']:.4f} | "
                     f"{x['dev_recall_at_2pct_fpr']:.4f} | {fpr} | {x['training_seconds_cumulative']} s | {x['peak_vram_gb']} GB |")
    lines += ["", f"Thresholds: {json.dumps(out['thresholds'])}. Routed/max systems use score / threshold ≥ 1.", "",
              "## Main table: test (external_eval + external_translated_gemini)", "",
              "| Lang | System | Recall [95% CI] | FPR [95% CI] | F1 | AUROC |", "|---|---|---|---|---:|---:|"]
    for lang in LANGS:
        for s, m in out["main"][f"test|{lang}"].items():
            lines.append(f"| {lang} | {s} | {cell(m, 'recall')} | {cell(m, 'fpr')} | {m['f1']} | {m['auroc']} |")
    lines += ["", "## Overrefusal FPR (headline): xstest + or_bench + overrefusal_translated_gemini", "",
              "| Lang | " + " | ".join(SYSTEMS) + " |", "|---|" + "---|" * len(SYSTEMS)]
    for lang in LANGS:
        o = out["main"][f"overrefusal|{lang}"]
        lines.append(f"| {lang} | " + " | ".join(cell(o[s], "fpr") for s in SYSTEMS) + " |")
    lines += ["", "## Significance (McNemar exact, paired correctness, test + overrefusal rows)", "",
              "| Lang | Comparison | A right, B wrong | B right, A wrong | p | Significant at 0.05 |", "|---|---|---:|---:|---:|---|"]
    for lang, comps in out["significance"].items():
        for name, c in comps.items():
            lines.append(f"| {lang} | {name.replace('_vs_', ' vs ')} | {c['a_right_b_wrong']} | {c['b_right_a_wrong']} | {'<1e-6' if c['p_value'] < 1e-6 else format(c['p_value'], '.3g')} | {'yes' if c['significant_0.05'] else 'no'} |")
    lines += ["", "## Router impact: routed_v3 with langid_v1 vs oracle language", "",
              "| Set | Lang | langid_v1 routed as | routed_v3 recall | routed_v3_oracle recall | routed_v3 FPR | routed_v3_oracle FPR |", "|---|---|---|---|---|---|---|"]
    for key, r in out["router"].items():
        name, lang = key.split("|"); m = out["main"][key]
        lines.append(f"| {name} | {lang} | {json.dumps(r['routed_as'])} | {cell(m['routed_v3'], 'recall')} | {cell(m['routed_v3_oracle'], 'recall')} | "
                     f"{cell(m['routed_v3'], 'fpr')} | {cell(m['routed_v3_oracle'], 'fpr')} |")
    lines += ["", "## Test without label-audit-flagged benign rows", "", "| Lang | Removed benign | System | Recall | FPR | AUROC |", "|---|---:|---|---|---|---:|"]
    for lang, x in out["test_without_label_audit_flags"].items():
        for s in ("deberta", "routed_v3", "v3"):
            lines.append(f"| {lang} | {x['removed_benign']} | {s} | {cell(x[s], 'recall')} | {cell(x[s], 'fpr')} | {x[s]['auroc']} |")
    lines += ["", "## English extra sets", "", "| Set | System | Recall [95% CI] | FPR [95% CI] |", "|---|---|---|---|"]
    for label, ms in out["extra_en"].items():
        for s, m in ms.items():
            lines.append(f"| {label} | {s} | {cell(m, 'recall')} | {cell(m, 'fpr')} |")
    lines += ["", "## Latency (batch 1, ms; routed systems include the language router)", "", "| Device | System | p50 | p95 | n |", "|---|---|---:|---:|---:|"]
    for device, res in out["latency"].items():
        for s, v in res.items():
            lines.append(f"| {device} | {s} | {v['p50_ms']} | {v['p95_ms']} | {v['n']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]), flush=True)


# ---------------------------------------------------------------- recalibration (results/clf_v3_recal.*)
V3 = "models/clf_v3_e3"
NON_EN = ("roman_ur", "ur", "mixed")
LEVELS = (0.02, 0.03, 0.05)
RULE_MAX_FPR = 0.03
RECAL_JSON = Path("results/clf_v3_recal.json")
RECAL_MD = Path("results/clf_v3_recal.md")
RECAL_SYSTEMS = ("deberta", "routed_v2", "routed_v3", "routed_v3_perlang")


def at_fpr(benign_scores, fpr):
    """Lowest threshold whose benign FPR is <= fpr (k = floor(fpr * n) benign rows at or above it)."""
    s = sorted(benign_scores)
    k = int(fpr * len(s))
    return s[-1] + 1e-9 if k == 0 else s[len(s) - k]


def dev_thresholds():
    """Non-English dev rows only (pooled, and per language) -> thresholds for v2 and v3."""
    rows = load_jsonl(DATA / "dev_v3.jsonl")
    out = {}
    for name, d in (("v2", V2), ("v3", V3)):
        sc = risks(DATA / "dev_v3.jsonl", "classifier", d)
        dev = [(r.lang, r.label, s) for r, s in zip(rows, sc) if r.lang in NON_EN]
        res = {"pooled": {}, "per_lang_2pct": {}}
        for level in LEVELS:
            t = at_fpr([s for _, l, s in dev if l == "benign"], level)
            per = {lang: {"recall": round(sum(s >= t for g, l, s in dev if g == lang and l == "attack") / sum(g == lang and l == "attack" for g, l, _ in dev), 4),
                          "fpr": round(sum(s >= t for g, l, s in dev if g == lang and l == "benign") / sum(g == lang and l == "benign" for g, l, _ in dev), 4)}
                   for lang in NON_EN}
            a = [s for _, l, s in dev if l == "attack"]; b = [s for _, l, s in dev if l == "benign"]
            res["pooled"][f"{level:.0%}"] = {"threshold": t, "dev_non_en_recall": round(sum(s >= t for s in a) / len(a), 4),
                                            "dev_non_en_fpr": round(sum(s >= t for s in b) / len(b), 4), "dev_attacks": len(a),
                                            "dev_benign": len(b), "per_lang": per}
        for lang in NON_EN:
            t = at_fpr([s for g, l, s in dev if g == lang and l == "benign"], 0.02)
            a = [s for g, l, s in dev if g == lang and l == "attack"]
            res["per_lang_2pct"][lang] = {"threshold": t, "dev_recall": round(sum(s >= t for s in a) / len(a), 4)}
        out[name] = res
    return out


def choose_point(th):
    """Dev-only rule: highest dev non-English recall among (model, level) with dev non-English FPR <= 3%;
    ties -> v3, then the lower FPR level."""
    cands = [(m, lvl, x) for m, r in th.items() for lvl, x in r["pooled"].items() if x["dev_non_en_fpr"] <= RULE_MAX_FPR]
    m, lvl, x = max(cands, key=lambda c: (c[2]["dev_non_en_recall"], c[0] == "v3", -float(c[1].rstrip("%"))))
    return {"model": m, "level": lvl, "threshold": x["threshold"], "dev_non_en_recall": x["dev_non_en_recall"],
            "dev_non_en_fpr": x["dev_non_en_fpr"],
            "rule": f"highest dev non-English recall with dev non-English FPR <= {RULE_MAX_FPR:.0%} over v2/v3 x {', '.join(f'{l:.0%}' for l in LEVELS)}"}


def recal_rows(files, t2, t3, t3_lang):
    rows = []
    for f in files:
        path = DATA / f
        recs = load_jsonl(path)
        deb, s2, s3 = risks(path, "deberta", None), risks(path, "classifier", V2), risks(path, "classifier", V3)
        for r, d, x2, x3 in zip(recs, deb, s2, s3):
            routed = detect_lang(normalize_text(r.input_text()))[0]
            en = routed == "en"
            pred = {"deberta": d >= DEBERTA_THRESHOLD,
                    "routed_v2": d >= DEBERTA_THRESHOLD if en else x2 >= t2,
                    "routed_v3": d >= DEBERTA_THRESHOLD if en else x3 >= t3,
                    "routed_v3_perlang": d >= DEBERTA_THRESHOLD if en else x3 >= t3_lang.get(routed, t3)}
            rows.append({"id": r.id, "label": r.label, "lang": r.lang, "routed": routed, "pred": pred})
    return rows


def rmetrics(rows, system):
    a = [r for r in rows if r["label"] == "attack"]; b = [r for r in rows if r["label"] == "benign"]
    tp = sum(r["pred"][system] for r in a); fp = sum(r["pred"][system] for r in b)
    return {"attacks": len(a), "benign": len(b), "tp": tp, "fp": fp,
            "recall": round(tp / len(a), 4) if a else None, "recall_ci": wilson(tp, len(a)),
            "fpr": round(fp / len(b), 4) if b else None, "fpr_ci": wilson(fp, len(b))}


def recal():
    th = dev_thresholds()
    point = choose_point(th)
    level = point["level"]
    t2, t3 = th["v2"]["pooled"][level]["threshold"], th["v3"]["pooled"][level]["threshold"]
    t3_lang = {l: x["threshold"] for l, x in th["v3"]["per_lang_2pct"].items()}
    neardup = set(json.loads((DATA / "v3_test_neardup_ids.json").read_text(encoding="utf-8")))
    data = {name: recal_rows(files, t2, t3, t3_lang) for name, files in SETS.items()}
    out = {"thresholds": th, "chosen": point, "applied": {"deberta": DEBERTA_THRESHOLD, "v2_non_en": t2, "v3_non_en": t3, "v3_per_lang_2pct": t3_lang},
           "router": "langid_v2 + Roman-Urdu override (pehredar.langid.detect_lang)", "neardup_test_rows": len(neardup),
           "test_all": {}, "test_no_neardup": {}, "overrefusal": {}, "significance_recall": {}, "significance_fpr": {}, "all_levels_routed_v3": {}}
    for lang in LANGS:
        t = [r for r in data["test"] if r["lang"] == lang]; o = [r for r in data["overrefusal"] if r["lang"] == lang]
        out["test_all"][lang] = {s: rmetrics(t, s) for s in RECAL_SYSTEMS}
        out["test_no_neardup"][lang] = {s: rmetrics([r for r in t if r["id"] not in neardup], s) for s in RECAL_SYSTEMS}
        out["test_no_neardup"][lang]["removed_rows"] = sum(r["id"] in neardup for r in t)
        out["overrefusal"][lang] = {s: rmetrics(o, s) for s in RECAL_SYSTEMS}
        attacks = [r for r in t if r["label"] == "attack"]; benign = [r for r in t + o if r["label"] == "benign"]
        out["significance_recall"][lang] = {"routed_v3_vs_deberta": mcnemar(attacks, "routed_v3", "deberta"),
                                            "routed_v3_vs_routed_v2": mcnemar(attacks, "routed_v3", "routed_v2")}
        out["significance_fpr"][lang] = {"routed_v3_vs_deberta": mcnemar(benign, "routed_v3", "deberta"),
                                         "routed_v3_vs_routed_v2": mcnemar(benign, "routed_v3", "routed_v2")}
    for lvl in th["v3"]["pooled"]:
        tl = th["v3"]["pooled"][lvl]["threshold"]
        test_rows = recal_rows(SETS["test"], t2, tl, t3_lang); over_rows = recal_rows(SETS["overrefusal"], t2, tl, t3_lang)
        out["all_levels_routed_v3"][lvl] = {lang: {"test": rmetrics([r for r in test_rows if r["lang"] == lang], "routed_v3"),
                                                   "overrefusal": rmetrics([r for r in over_rows if r["lang"] == lang], "routed_v3")} for lang in NON_EN}
    RECAL_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    render_recal(out)


def pval(c):
    return "<1e-6" if c["p_value"] < 1e-6 else format(c["p_value"], ".3g")


def render_recal(out):
    th, ch = out["thresholds"], out["chosen"]
    lines = ["# v3 recalibration: non-English thresholds, router v2", "",
             "All numbers come from `results/clf_v3_recal.json` (`python -m scripts.run_v3_evaluation --recal`). Thresholds for the "
             "non-English path are chosen on dev rows with lang in roman_ur / ur / mixed only; the English route (DeBERTa 0.5) is "
             f"unchanged. Router: {out['router']}. Non-English sets are Gemini machine translations, not the human test set.", "",
             "## Non-English dev thresholds", "", "| Model | Dev non-en FPR target | Threshold | Dev non-en recall | Dev non-en FPR | Dev FPR roman_ur / ur / mixed |",
             "|---|---|---:|---:|---:|---|"]
    for m, r in th.items():
        for lvl, x in r["pooled"].items():
            lines.append(f"| {m} | {lvl} | {x['threshold']:.4f} | {x['dev_non_en_recall']:.4f} | {x['dev_non_en_fpr']:.4f} | "
                         + " / ".join(f"{x['per_lang'][l]['fpr']:.4f}" for l in NON_EN) + " |")
    lines += ["", "Secondary: per-language thresholds (2% FPR per language on dev): " + "; ".join(
        f"{m} " + ", ".join(f"{l} {x['threshold']:.4f} (dev recall {x['dev_recall']:.4f})" for l, x in r["per_lang_2pct"].items()) for m, r in th.items()), "",
        f"**Operating point (dev-only rule: {ch['rule']}):** {ch['model']} at {ch['level']} → threshold {ch['threshold']:.4f}, dev non-en recall "
        f"{ch['dev_non_en_recall']:.4f}, dev non-en FPR {ch['dev_non_en_fpr']:.4f}. Test numbers below are reported, not used for the choice. "
        f"routed_v2 uses v2's threshold at the same level ({out['applied']['v2_non_en']:.4f}); routed_v3_perlang is the secondary per-language variant.", ""]
    for key, title in (("test_all", "Test (external_eval + external_translated_gemini), all rows"),
                       ("test_no_neardup", f"Test excluding the {out['neardup_test_rows']} near-duplicate rows (e5 > 0.95 to train)")):
        lines += [f"## {title}", "", "| Lang | System | Recall [95% CI] | FPR [95% CI] |", "|---|---|---|---|"]
        for lang, ms in out[key].items():
            for s in RECAL_SYSTEMS:
                lines.append(f"| {lang} | {s} | {cell(ms[s], 'recall')} | {cell(ms[s], 'fpr')} |")
            if "removed_rows" in ms:
                lines.append(f"| {lang} | (rows removed) | {ms['removed_rows']} | |")
        lines.append("")
    lines += ["## Overrefusal FPR (xstest + or_bench + overrefusal_translated_gemini)", "", "| Lang | " + " | ".join(RECAL_SYSTEMS) + " |",
              "|---|" + "---|" * len(RECAL_SYSTEMS)]
    for lang, ms in out["overrefusal"].items():
        lines.append(f"| {lang} | " + " | ".join(cell(ms[s], "fpr") for s in RECAL_SYSTEMS) + " |")
    for key, title in (("significance_recall", "Significance — recall (McNemar exact on test attack rows)"),
                       ("significance_fpr", "Significance — FPR (McNemar exact on test benign + overrefusal rows)")):
        lines += ["", f"## {title}", "", "| Lang | Comparison | routed_v3 right, other wrong | other right, routed_v3 wrong | p | Significant at 0.05 |",
                  "|---|---|---:|---:|---:|---|"]
        for lang, comps in out[key].items():
            for name, c in comps.items():
                lines.append(f"| {lang} | {name.replace('_vs_', ' vs ')} | {c['a_right_b_wrong']} | {c['b_right_a_wrong']} | {pval(c)} | {'yes' if c['significant_0.05'] else 'no'} |")
    lines += ["", "## routed_v3 at each dev FPR level (transparency; not used for the choice)", "",
              "| Level | Lang | Test recall [95% CI] | Test FPR [95% CI] | Overrefusal FPR [95% CI] |", "|---|---|---|---|---|"]
    for lvl, langs in out["all_levels_routed_v3"].items():
        for lang, x in langs.items():
            lines.append(f"| {lvl} | {lang} | {cell(x['test'], 'recall')} | {cell(x['test'], 'fpr')} | {cell(x['overrefusal'], 'fpr')} |")
    RECAL_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:24]), flush=True)


if __name__ == "__main__":
    if "--recal" in sys.argv:
        recal()
    elif "--render" in sys.argv:
        render(json.loads(OUT_JSON.read_text(encoding="utf-8")))
    else:
        main()
