import json
import random
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
    for candidate, train_id in train_text.items():
        if len(candidate) < 30:
            continue
        for reference, test_id in test_text.items():
            if len(reference) < 30 or abs(len(candidate) - len(reference)) > max(len(candidate), len(reference)) * 0.1:
                continue
            if SequenceMatcher(None, candidate, reference, autojunk=False).ratio() >= 0.93:
                raise ValueError(f"Train/test near-duplicate text: {train_id} and {test_id}")


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
