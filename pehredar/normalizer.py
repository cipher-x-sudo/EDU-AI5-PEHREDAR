import base64
import re
import unicodedata

INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
ENCODED = re.compile(r"\b(base64|hex):([A-Za-z0-9+/=]+)(?![A-Za-z0-9+/=])", re.I)
VERSION = "l0-1"


def normalize_text(text: str) -> str:
    if len(text) > 32768:
        raise ValueError("Text exceeds 32768 characters")
    text = unicodedata.normalize("NFKC", text).translate(INVISIBLE)

    def decode(match: re.Match[str]) -> str:
        kind, data = match.groups()
        try:
            raw = base64.b64decode(data, validate=True) if kind.lower() == "base64" else bytes.fromhex(data)
            if len(raw) > 8192:
                return match.group()
            decoded = raw.decode("utf-8")
            return decoded if decoded.isprintable() else match.group()
        except (ValueError, UnicodeDecodeError):
            return match.group()

    for _ in range(2):
        updated = ENCODED.sub(decode, text)
        if updated == text:
            break
        text = updated
    return re.sub(r"\s+", " ", text).strip()
