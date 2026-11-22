import re

PATTERNS = {
    "prompt_injection": [
        re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.I),
        re.compile(r"(?:reveal|show|print|disclose).{0,40}(?:system\s+prompt|hidden\s+instructions)", re.I),
        re.compile(r"forget\s+(?:your|all)\s+(?:rules|instructions)", re.I),
        re.compile(r"(?:apni|pichli)\s+(?:saari\s+)?hidayaat\s+bhool", re.I),
        re.compile(r"(?:rules|instructions|hidayaat)\s+(?:bhool|nazr\s+andaz)\s+(?:karo|do)", re.I),
        re.compile(r"(?:اپنی|پچھلی)\s+(?:تمام\s+)?ہدایات\s+(?:بھول|نظر\s+انداز)", re.I),
    ],
}


def score_rules(text: str) -> tuple[float, list[str]]:
    tags = [tag for tag, patterns in PATTERNS.items() if any(p.search(text) for p in patterns)]
    return (0.95 if tags else 0.0), tags
