"""Post-hoc translation checks (review v2 findings). No network imports, so tests can use them."""
import re
from collections import Counter
from difflib import SequenceMatcher

TERMINAL = tuple('.!?۔؟:;"\')]}`*…>')
OPENERS = ("sure", "here is", "here's", "here are", "certainly", "of course", "beshak", "bilkul", "zaroor",
           "یہاں", "یقیناً", "بالکل", "ضرور", "بے شک", "بیشک")
EN_OPENERS = ("sure", "here", "certainly", "of course", "absolutely", "yes", "ok", "okay")


def clean(value: str) -> str:
    """Strip /no_think and leftover think tags (clean, never reject)."""
    value = re.sub(r"<think>.*?</think>", "", value, flags=re.S | re.I)
    value = re.sub(r"</?think>|/no_think|/think\b", "", value, flags=re.I)
    return value.strip()


def _repetitive(text: str) -> bool:
    words = text.split()
    grams = [tuple(words[i:i + 4]) for i in range(len(words) - 3)]
    if not grams:
        return False
    return max(Counter(grams).values()) >= 3 or len(set(grams)) / len(grams) < 0.5


def check(value: str, original: str, done_reason: str | None = None) -> list[str]:
    """Failure reasons from the v3 checks (empty list = keep). `value` should already be clean()ed."""
    reasons = []
    o = original.strip()
    if done_reason == "length" or (
            done_reason is None and (
                (o.endswith(TERMINAL) and not value.rstrip().endswith(TERMINAL))
                or (len(o) > 300 and len(value) / len(o) < 0.6))):
        reasons.append("truncated")
    if _repetitive(value) and not _repetitive(original):  # a faithfully repeated original is fine
        reasons.append("repetition")
    if re.search("[ऀ-ॿ]", value):  # Devanagari
        reasons.append("wrong_script")
    v, oc = value.casefold(), original.casefold()
    if SequenceMatcher(None, v, oc).ratio() > 0.85 or (len(v) >= 20 and v in oc):  # copied (part of) the original
        reasons.append("untranslated")
    if value.lstrip().casefold().startswith(OPENERS) and not o.casefold().startswith(EN_OPENERS):
        reasons.append("answered")
    return reasons
