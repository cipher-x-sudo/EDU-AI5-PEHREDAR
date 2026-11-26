"""Language detection.

detect(): rule-based labeller used by the data pipeline (scripts/unify.py).
detect_lang(): router for the gateway's L2 — char n-gram TF-IDF + logistic regression (models/langid_v1.joblib,
trained by scripts/train_langid.py). Probability < LOW_CONFIDENCE routes to "mixed" (the non-English path).
If the model file is missing, it falls back to detect() and reports probability 0.0."""
import os
import re
from functools import lru_cache
from pathlib import Path

MODEL_PATH = Path(os.getenv("PEHREDAR_LANGID_MODEL", str(Path(__file__).resolve().parent.parent / "models" / "langid_v1.joblib")))
LOW_CONFIDENCE = 0.6


def preprocess(text: str) -> str:
    """TF-IDF preprocessor of the router (module-level so the saved model can be loaded)."""
    return text[:1000].lower()


@lru_cache(maxsize=1)
def _model():
    if not MODEL_PATH.is_file():
        return None
    import joblib
    return joblib.load(MODEL_PATH)


def detect_lang(text: str) -> tuple[str, float]:
    """(lang, probability) with lang in en | roman_ur | ur | mixed; low confidence -> mixed."""
    model = _model()
    if model is None:
        lang = detect(text)
        return ("en" if lang == "other" else lang), 0.0
    proba = model.predict_proba([text])[0]
    best = int(proba.argmax())
    prob = float(proba[best])
    return ("mixed" if prob < LOW_CONFIDENCE else str(model.classes_[best])), prob

ROMAN = {"hai", "nahi", "kya", "mujhe", "aur", "karo", "bhai", "yaar"}
ENGLISH = {"the", "is", "are", "what", "how", "please", "can", "you", "to", "of"}


def detect(text: str) -> str:
    """en | ur | roman_ur | mixed | other."""
    words = re.findall(r"[a-z]+", text.casefold())
    arabic = len(re.findall(r"[؀-ۿ]", text))
    if arabic > len(text) * .2:
        return "ur" if len(words) < 3 else "mixed"
    if not words:
        return "other"
    ru_words = {w for w in words if w in ROMAN}
    ru = len(ru_words) / len(words)
    en = sum(w in ENGLISH for w in words) / len(words)
    # A few English words in names, addresses, or email text must not create a
    # mixed label; require at least two distinct Roman Urdu markers.
    if len(ru_words) >= 2 and ru > .2 and en > .2:
        return "mixed"
    return "roman_ur" if len(ru_words) >= 2 and ru > .2 else "en"
