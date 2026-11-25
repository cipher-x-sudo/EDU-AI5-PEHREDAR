import pytest
from scripts.train_classifier import train



def test_training_refuses_frozen_test_input(tmp_path):
    frozen = tmp_path / "frozen_test"
    frozen.mkdir()
    path = frozen / "human_v1.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="frozen"):
        train(path, tmp_path / "model", "FacebookAI/xlm-roberta-base", 1, 2, 42)
