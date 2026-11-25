import pytest
from scripts.train_classifier import train



def test_training_refuses_frozen_test_input(tmp_path):
    frozen = tmp_path / "frozen_test"
    frozen.mkdir()
    path = frozen / "human_v1.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="frozen"):
        train(path, tmp_path / "model", "FacebookAI/xlm-roberta-base", 1, 2, 42)


def test_eval_frozen_refuses_without_flag(monkeypatch):
    import scripts.eval_frozen as ef
    opened = []
    monkeypatch.setattr(ef, "load_jsonl", lambda *a: opened.append(a), raising=False)
    for env in ({}, {"PEHREDAR_EVAL_FROZEN": "0"}, {"PEHREDAR_EVAL_FROZEN": "1", "PEHREDAR_SKIP_FROZEN": "1"}):
        monkeypatch.delenv("PEHREDAR_EVAL_FROZEN", raising=False)
        monkeypatch.delenv("PEHREDAR_SKIP_FROZEN", raising=False)
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        with pytest.raises(SystemExit) as stop:
            ef.main()
        assert stop.value.code == 2
    assert not opened


def test_eval_frozen_cli_refuses(tmp_path):
    import os, subprocess, sys
    env = {k: v for k, v in os.environ.items() if k != "PEHREDAR_EVAL_FROZEN"}
    done = subprocess.run([sys.executable, "scripts/eval_frozen.py"], capture_output=True, text=True, env=env)
    assert done.returncode == 2 and "refuses" in done.stderr
