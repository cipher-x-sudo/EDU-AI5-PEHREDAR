"""Train the language-ID router v2 -> models/langid_v2.joblib, results/langid_v2.md/.json.

Model: char_wb 1-5 TF-IDF + LogisticRegression (class_weight balanced). Train: 15,000 English originals
(seed 42) + Gemini train translations (roman_ur / ur / mixed) + synthetic code-mixed rows labelled "mixed",
built without any API: 2,000 English train rows with their Gemini roman_ur translation are spliced
(a) clause-wise (first clauses English, rest Roman Urdu, or the reverse) and (b) word-wise (1-3 Roman Urdu
words inserted into the English sentence, English-heavy).
Report: en-vs-non-en accuracy on dev / test / overrefusal for v1, v1+override, v2, v2+override (= detect_lang),
and the rate at which ENGLISH rows are sent to the non-English (v3) path on English test sets.

  python -m scripts.train_langid   # training image (scikit-learn version pinned in pyproject)"""
import json, random, re
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline

from pehredar import langid

ROOT = Path("data/processed")
V1 = Path("models/langid_v1.joblib")
LANGS = ["en", "roman_ur", "ur", "mixed"]
SETS = {"dev": ["dev_public_v2.jsonl", "dev_translated_v2_gemini.jsonl"],
        "test": ["external_eval.jsonl", "external_translated_gemini.jsonl"],
        "overrefusal": ["overrefusal_eval.jsonl", "overrefusal_translated_gemini.jsonl"]}
ENGLISH_SETS = {"external_eval (en)": ("external_eval.jsonl", None), "overrefusal xstest+or_bench (en)": ("overrefusal_eval.jsonl", None),
                "benign_email_probe": ("benign_email_probe.jsonl", None), "bipia": ("indirect_eval.jsonl", "bipia"),
                "injecagent": ("indirect_eval.jsonl", "injecagent")}
CLAUSE = re.compile(r"(?<=[.,;:!?])\s+")


def read(name):
    return [json.loads(x) for x in (ROOT/name).read_text(encoding="utf-8").splitlines() if x.strip()]


def text(r):
    return r.get("text") or "\n".join(t["content"] if isinstance(t, dict) else str(t) for t in (r.get("turns") or []))


def synthetic_mixed(rng, n=2000):
    pairs = [(r["original"], r["text"]) for r in read("translated_v2_gemini.jsonl") if r["lang"] == "roman_ur"]
    out = []
    for en, ru in rng.sample(sorted(pairs), min(n, len(pairs))):
        ce, cr = CLAUSE.split(en.strip()), CLAUSE.split(ru.strip())
        if len(ce) >= 2 and len(cr) >= 2:
            k = rng.randint(1, min(len(ce), len(cr)) - 1)
            out.append(" ".join(ce[:k] + cr[k:]) if rng.random() < .5 else " ".join(cr[:k] + ce[k:]))
        words, ru_words = en.split(), [w for w in re.findall(r"[A-Za-z]+", ru) if len(w) > 1]
        if words and ru_words:
            for w in rng.sample(ru_words, min(len(ru_words), rng.randint(1, 3))):
                words.insert(rng.randint(0, len(words)), w)
            out.append(" ".join(words))
    return [(t, "mixed") for t in out]


def predict(model, texts, override):
    proba = model.predict_proba(texts); classes = [str(c) for c in model.classes_]; out = []
    for t, p in zip(texts, proba):
        best = int(p.argmax())
        if override and classes[best] == "en" and langid.roman_urdu_override(t):
            best = max((i for i, c in enumerate(classes) if c != "en"), key=lambda i: p[i]); out.append(classes[best])
        else:
            out.append("mixed" if p[best] < langid.LOW_CONFIDENCE else classes[best])
    return out


def scores(y, pred):
    return {"n": len(y), "macro_f1": round(f1_score(y, pred, labels=LANGS, average="macro"), 4),
            "en_vs_non_en_accuracy": round(sum((a == "en") == (b == "en") for a, b in zip(y, pred)) / len(y), 4),
            "non_en_sent_to_en": sum(a != "en" and b == "en" for a, b in zip(y, pred)),
            "en_sent_to_non_en": sum(a == "en" and b != "en" for a, b in zip(y, pred)),
            "confusion": confusion_matrix(y, pred, labels=LANGS).tolist()}


def main():
    rng = random.Random(42)
    en = [(r["text"], "en") for r in read("train_public_v2.jsonl") if r.get("text") and r["lang"] == "en"]
    synth = synthetic_mixed(rng)
    train = rng.sample(en, 15000) + [(r["text"], r["lang"]) for r in read("translated_v2_gemini.jsonl")] + synth
    model = make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 5), max_features=200000, sublinear_tf=True,
                                          preprocessor=langid.preprocess),
                          LogisticRegression(max_iter=2000, class_weight="balanced"))
    model.fit([t for t, _ in train], [l for _, l in train])
    joblib.dump(model, langid.MODEL_PATH, compress=3)
    langid._model.cache_clear()
    v1 = joblib.load(V1)
    variants = {"v1": (v1, False), "v1+override": (v1, True), "v2": (model, False), "v2+override (detect_lang)": (model, True)}
    out = {"train_rows": len(train), "synthetic_mixed_rows": len(synth), "model_path": str(langid.MODEL_PATH),
           "model_bytes": langid.MODEL_PATH.stat().st_size, "override_markers": len(langid.ROMAN_URDU_MARKERS), "sets": {}, "english_sent_to_non_en": {}}
    for name, files in SETS.items():
        data = [(text(r), r["lang"]) for f in files for r in read(f) if text(r) and r["lang"] in LANGS]
        y = [l for _, l in data]
        out["sets"][name] = {v: scores(y, predict(m, [t for t, _ in data], o)) for v, (m, o) in variants.items()}
    for name, (f, source) in ENGLISH_SETS.items():
        texts = [text(r) for r in read(f) if r["lang"] == "en" and (source is None or r["source"] == source)]
        out["english_sent_to_non_en"][name] = {v: {"n": len(texts), "sent_to_non_en": sum(p != "en" for p in predict(m, texts, o))}
                                               for v, (m, o) in variants.items()}
    Path("results/langid_v2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# Language-ID router v2", "", f"Char n-gram TF-IDF + LogisticRegression trained on {out['train_rows']} rows "
             f"(15,000 English, Gemini train translations, {out['synthetic_mixed_rows']} synthetic code-mixed rows built by clause and "
             f"word splicing of English train rows with their Gemini roman_ur translation). Roman-Urdu override: ≥ 2 of "
             f"{out['override_markers']} function-word markers, or any Urdu-script letter, never routes to en. `+override` rows are what "
             "the gateway uses (`detect_lang`).", "", "## en vs non-en accuracy (routing-relevant)", "",
             "| Set | Variant | en-vs-non-en acc. | non-en sent to en | en sent to non-en | Macro-F1 |", "|---|---|---:|---:|---:|---:|"]
    for name, vs in out["sets"].items():
        for v, m in vs.items():
            lines.append(f"| {name} (n={m['n']}) | {v} | {m['en_vs_non_en_accuracy']} | {m['non_en_sent_to_en']} | {m['en_sent_to_non_en']} | {m['macro_f1']} |")
    lines += ["", "## English rows sent to the non-English (v3) path", "", "| English set | Variant | Sent to non-en | n | Rate |", "|---|---|---:|---:|---:|"]
    for name, vs in out["english_sent_to_non_en"].items():
        for v, m in vs.items():
            lines.append(f"| {name} | {v} | {m['sent_to_non_en']} | {m['n']} | {m['sent_to_non_en'] / max(1, m['n']):.2%} |")
    Path("results/langid_v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
