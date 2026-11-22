import re

PII_PATTERNS = [
    re.compile(r"\b\d{5}-\d{7}-\d\b"),
    re.compile(r"(?<!\w)(?:\+92|0)3\d{2}-?\d{7}\b"),
    re.compile(r"\bPK\d{2}[A-Z]{4}\d{16}\b", re.I),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
]
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
CODE_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+/(?:\s|$)"),
    re.compile(r"\bcurl\b[^\n|]{0,200}\|\s*(?:ba)?sh\b", re.I),
]


def check_output(text: str, canary: str) -> tuple[str, str, list[str]]:
    if canary and canary in text:
        return "block", "", ["canary_leak"]
    if any(p.search(text) for p in SECRET_PATTERNS):
        return "block", "", ["secret_leak"]
    if any(p.search(text) for p in CODE_PATTERNS):
        return "block", "", ["unsafe_code"]
    redacted = text
    for pattern in PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return ("redact", redacted, ["pii"]) if redacted != text else ("allow", text, [])
