import csv
import hashlib

import pytest

from pehredar.dataset import load_jsonl
from scripts.freeze_collection import freeze


FIELDS = (
    "id", "text", "lang", "label", "type", "source", "split_group",
    "consent", "consent_reference", "author_code", "reviewer", "attack_family",
)


def write_review_csv(path, change=None):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for index in range(100):
            attack = index < 50
            row = {
                "id": f"ru-{index:03}",
                "text": f"Review fixture {index}",
                "lang": "roman_ur",
                "label": "attack" if attack else "benign",
                "type": "injection" if attack else "none",
                "source": "human",
                "split_group": f"group-{index}",
                "consent": "yes",
                "consent_reference": "fixture-consent",
                "author_code": "fixture-author",
                "reviewer": "fixture-reviewer",
                "attack_family": "instruction_override" if attack else "",
            }
            if change and index == 0:
                row.update(change)
            writer.writerow(row)


def test_freeze_seals_reviewed_csv_without_private_metadata(tmp_path):
    source = tmp_path / "review.csv"
    output = tmp_path / "human_v1.jsonl"
    write_review_csv(source)
    digest = freeze(source, output)
    assert digest == hashlib.sha256(output.read_bytes()).hexdigest()
    assert len(load_jsonl(output)) == 100
    assert "fixture-consent" not in output.read_text(encoding="utf-8")
    assert output.with_suffix(".jsonl.sha256").read_text().startswith(digest)
    with pytest.raises(FileExistsError):
        freeze(source, output)


@pytest.mark.parametrize("change, message", [
    ({"consent": "no"}, "consent"),
    ({"reviewer": ""}, "reviewer"),
    ({"attack_family": ""}, "attack_family"),
    ({"type": "none"}, "attack type"),
    ({"text": "email me at user@example.com"}, "personal data"),
])
def test_freeze_rejects_unreviewed_or_invalid_rows(tmp_path, change, message):
    source = tmp_path / "review.csv"
    output = tmp_path / "human_v1.jsonl"
    write_review_csv(source, change)
    with pytest.raises(ValueError, match=message):
        freeze(source, output)
    assert not output.exists()
