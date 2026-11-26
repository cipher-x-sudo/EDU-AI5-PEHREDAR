"""Train the language-ID router (char_wb 1-5 TF-IDF + LogisticRegression) -> models/langid_v1.joblib,
results/langid_v1.md/.json.

Train: train-split texts (English originals = en; Gemini translations = their lang). English is subsampled to
15,000 rows (seed 42); class_weight="balanced". Eval on dev (dev_public_v2 + dev_translated_v2_gemini), test
(external_eval + external_translated_gemini) and overrefusal (overrefusal_eval + overrefusal_translated_gemini):
confusion matrix, per-class F1, macro-F1, en-vs-non-en routing accuracy, for langid_v1 (argmax), langid_v1 as
routed (prob < 0.6 -> mixed) and the old 8-word detector (other -> en).

  python -m scripts.train_langid   # training image (scikit-learn version pinned in pyproject)"""
import json, random
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline

from pehredar import langid

ROOT = Path("data/processed")
LANGS = ["en", "roman_ur", "ur", "mixed"]
SETS = {"dev": ["dev_public_v2.jsonl", "dev_translated_v2_gemini.jsonl"],
        "test": ["external_eval.jsonl", "external_translated_gemini.jsonl"],
        "overrefusal": ["overrefusal_eval.jsonl", "overrefusal_translated_gemini.jsonl"]}


def read(name):
    return [json.loads(x) for x in (ROOT/name).read_text(encoding="utf-8").splitlines() if x.strip()]


def pairs(files):
    return [(r["text"], r["lang"]) for f in files for r in read(f) if r.get("text") and r["lang"] in LANGS]


def scores(y, pred):
    return {"n": len(y), "macro_f1": round(f1_score(y, pred, labels=LANGS, average="macro"), 4),
            "per_class_f1": dict(zip(LANGS, (round(x, 4) for x in f1_score(y, pred, labels=LANGS, average=None)))),
            "en_vs_non_en_accuracy": round(sum((a == "en") == (b == "en") for a, b in zip(y, pred)) / len(y), 4),
            "confusion (rows=true, cols=pred; en, roman_ur, ur, mixed)": confusion_matrix(y, pred, labels=LANGS).tolist()}


def main():
    rng = random.Random(42)
    en = [(r["text"], "en") for r in read("train_public_v2.jsonl") if r.get("text") and r["lang"] == "en"]
    train = rng.sample(en, 15000) + [(r["text"], r["lang"]) for r in read("translated_v2_gemini.jsonl")]
    model = make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 5), max_features=200000, sublinear_tf=True,
                                          preprocessor=langid.preprocess),
                          LogisticRegression(max_iter=2000, class_weight="balanced"))
    model.fit([t for t, _ in train], [l for _, l in train])
    langid.MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, langid.MODEL_PATH, compress=3)
    langid._model.cache_clear()
    out = {"train_rows": len(train), "model_path": str(langid.MODEL_PATH), "model_bytes": langid.MODEL_PATH.stat().st_size,
           "low_confidence": langid.LOW_CONFIDENCE, "sets": {}}
    for name, files in SETS.items():
        data = pairs(files)
        y = [l for _, l in data]
        proba = model.predict_proba([t for t, _ in data])
        argmax = [model.classes_[p.argmax()] for p in proba]
        routed = [("mixed" if p.max() < langid.LOW_CONFIDENCE else c) for p, c in zip(proba, argmax)]
        old = [{"other": "en"}.get(langid.detect(t), langid.detect(t)) for t, _ in data]
        out["sets"][name] = {"langid_v1": scores(y, argmax), "langid_v1_routed": scores(y, routed), "old_8_word": scores(y, old)}
    Path("results/langid_v1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# Language-ID router v1", "", f"Char n-gram (char_wb 1–5, 200k features) TF-IDF + LogisticRegression, trained on {out['train_rows']} "
             "train-split texts (15,000 English originals + Gemini roman_ur/ur/mixed translations). `langid_v1_routed` applies the "
             f"gateway rule: probability < {langid.LOW_CONFIDENCE} → mixed (v3 path). `old_8_word` is the previous rule detector "
             "(other → en). Gemini's `mixed` and `roman_ur` overlap heavily (short code-mixed lines are often labelled mixed); "
             "both route to the same model, so en-vs-non-en accuracy is the routing-relevant number.", ""]
    for name, s in out["sets"].items():
        lines += [f"## {name} (n={s['langid_v1']['n']})", "", "| Detector | Macro-F1 | F1 en | F1 roman_ur | F1 ur | F1 mixed | en vs non-en acc. | Confusion (rows true en/roman_ur/ur/mixed) |",
                  "|---|---:|---:|---:|---:|---:|---:|---|"]
        for det, m in s.items():
            f = m["per_class_f1"]
            lines.append(f"| {det} | {m['macro_f1']} | {f['en']} | {f['roman_ur']} | {f['ur']} | {f['mixed']} | {m['en_vs_non_en_accuracy']} | "
                         f"{m['confusion (rows=true, cols=pred; en, roman_ur, ur, mixed)']} |")
        lines.append("")
    Path("results/langid_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
