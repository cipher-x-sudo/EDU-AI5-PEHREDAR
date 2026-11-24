import json
import random
from bisect import bisect_left, bisect_right
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from .normalizer import normalize_text


class Record(BaseModel):
    id: str = Field(min_length=1)
    text: str | None = None
    turns: list[str] | None = None
    lang: Literal["en", "ur", "roman_ur", "mixed"]
    label: Literal["attack", "benign"]
    type: Literal["injection", "jailbreak", "extraction", "obfuscation", "harm", "none"]
    source: str = Field(min_length=1)
    split_group: str = Field(min_length=1)

    @model_validator(mode="after")
    def text_or_turns(self):
        if bool(self.text) == bool(self.turns):
            raise ValueError("Exactly one of text or turns is required")
        if self.label == "benign" and self.type != "none":
            raise ValueError("Benign records must have type=none")
        if self.label == "attack" and self.type == "none":
            raise ValueError("Attack records must have an attack type")
        return self

    def input_text(self) -> str:
        return self.text if self.text is not None else "\n".join(self.turns or [])


def load_jsonl(path: Path) -> list[Record]:
    records = []
    ids = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = Record.model_validate(json.loads(line))
        except Exception as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        if record.id in ids:
            raise ValueError(f"Duplicate record ID: {record.id}")
        ids.add(record.id)
        records.append(record)
    return records


def assert_disjoint(train: list[Record], test: list[Record]) -> None:
    groups = {record.split_group for record in train}
    overlap = groups & {record.split_group for record in test}
    if overlap:
        raise ValueError(f"Train/test split_group overlap: {sorted(overlap)[:5]}")
    train_text = {normalize_text(record.input_text()).casefold(): record.id for record in train}
    test_text = {normalize_text(record.input_text()).casefold(): record.id for record in test}
    shared = train_text.keys() & test_text.keys()
    if shared:
        example = next(iter(shared))
        raise ValueError(f"Train/test duplicate text: {train_text[example]} and {test_text[example]}")
    for train_id, test_id in near_duplicate_pairs(train_text, test_text, first_only=True):
        raise ValueError(f"Train/test near-duplicate text: {train_id} and {test_id}")


def near_duplicate_pairs(train_text: dict[str, str], test_text: dict[str, str], first_only: bool = False):
    """(train_id, test_id) pairs with SequenceMatcher ratio >= 0.93 among texts >= 30 chars whose
    lengths differ by <= 10%. Same result as comparing every pair; the length window (bisect) and
    real_quick_ratio/quick_ratio (upper bounds of ratio) only skip pairs that cannot match."""
    refs = sorted((len(t), t, i) for t, i in test_text.items() if len(t) >= 30)
    lengths = [r[0] for r in refs]
    pairs = []
    for candidate, train_id in train_text.items():
        n = len(candidate)
        if n < 30:
            continue
        lo, hi = bisect_left(lengths, int(n * 0.9)), bisect_right(lengths, int(n / 0.9) + 1)
        for m, reference, test_id in refs[lo:hi]:
            if abs(n - m) > max(n, m) * 0.1:
                continue
            matcher = SequenceMatcher(None, candidate, reference, autojunk=False)
            if matcher.real_quick_ratio() >= 0.93 and matcher.quick_ratio() >= 0.93 and matcher.ratio() >= 0.93:
                pairs.append((train_id, test_id))
                if first_only:
                    return pairs
    return pairs


def grouped_split(records: list[Record], dev_fraction: float = 0.2, seed: int = 42) -> tuple[list[Record], list[Record]]:
    if not 0 < dev_fraction < 1:
        raise ValueError("dev_fraction must be between 0 and 1")
    groups: dict[str, list[Record]] = {}
    for record in records:
        groups.setdefault(record.split_group, []).append(record)
    if len(groups) < 2:
        raise ValueError("At least two split groups are required")
    keys = sorted(groups)
    random.Random(seed).shuffle(keys)
    dev_keys = set(keys[:max(1, min(len(keys) - 1, round(len(keys) * dev_fraction)))])
    train = [record for record in records if record.split_group not in dev_keys]
    dev = [record for record in records if record.split_group in dev_keys]
    assert_disjoint(train, dev)
    return train, dev
