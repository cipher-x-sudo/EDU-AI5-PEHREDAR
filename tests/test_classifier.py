import importlib

import pytest
from fastapi import HTTPException
from scripts.train_classifier import train

gateway = importlib.import_module("pehredar.app")


def test_optional_classifier_blocks_at_saved_threshold(monkeypatch, tmp_path):
    monkeypatch.setattr(gateway, "DB_PATH", tmp_path / "events.db")
    monkeypatch.setattr(gateway, "CLASSIFIER_DIR", "models/clf_v1")
    monkeypatch.setattr(gateway, "score_rules", lambda text: (0.0, []))
    monkeypatch.setattr(gateway, "score_classifier", lambda text, directory: (0.67, 0.65))
    decision = gateway.inspect_text("Previously unseen example", record=False)
    assert decision.action == "block"
    assert "classifier_attack" in decision.tags


def test_configured_classifier_fails_closed(monkeypatch):
    monkeypatch.setattr(gateway, "CLASSIFIER_DIR", "models/missing")
    def unavailable(text, directory):
        raise FileNotFoundError(directory)
    monkeypatch.setattr(gateway, "score_classifier", unavailable)
    with pytest.raises(HTTPException) as error:
        gateway.inspect_text("hello", record=False)
    assert error.value.status_code == 503


def test_training_refuses_frozen_test_input(tmp_path):
    frozen = tmp_path / "frozen_test"
    frozen.mkdir()
    path = frozen / "human_v1.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="frozen"):
        train(path, tmp_path / "model", "FacebookAI/xlm-roberta-base", 1, 2, 42)
