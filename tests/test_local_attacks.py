import pytest

from scripts.run_local_attacks import run


def test_attack_runner_rejects_nonlocal_targets(tmp_path):
    with pytest.raises(ValueError, match="local"):
        run(tmp_path / "attacks.jsonl", tmp_path / "report.json", "https://example.org", "model")
