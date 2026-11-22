import sqlite3

import pytest

from pehredar.state import update_escalation


def test_session_history_is_bounded_and_hashed(tmp_path):
    path = tmp_path / "state.db"
    for score in [0, 0, 0.5, 0.5, 1, 1]:
        result = update_escalation(path, "session-one", score)
    assert 0 < result <= 1
    with sqlite3.connect(path) as db:
        key, scores = db.execute("SELECT session_hash, scores FROM sessions").fetchone()
    assert "session-one" not in key
    assert len(__import__("json").loads(scores)) == 5
    assert update_escalation(path, "session-two", 0) == 0


def test_invalid_session_id_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        update_escalation(tmp_path / "state.db", "../escape", 0.2)
