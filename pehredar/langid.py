"""Language detector shared by the data pipeline (scripts/unify.py) and the gateway's L2 routing."""
import re

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
