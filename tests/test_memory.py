import sqlite3

from pehredar.memory import MAX_PER_SOURCE_DAY, is_known_attack, learn_canary_miss


def test_only_confirmed_canary_miss_is_remembered(tmp_path):
    db_path = tmp_path / "memory.db"
    assert not is_known_attack(db_path, "new prompt")
    assert not learn_canary_miss(db_path, "new prompt", None)
    assert learn_canary_miss(db_path, "new prompt", "session-1")
    assert is_known_attack(db_path, "new prompt")
    with sqlite3.connect(db_path) as db:
        assert "new prompt" not in str(db.execute("SELECT * FROM confirmed_attacks").fetchall())


def test_source_cap(tmp_path):
    db_path = tmp_path / "memory.db"
    for index in range(MAX_PER_SOURCE_DAY):
        assert learn_canary_miss(db_path, f"attack-{index}", "session-1")
    assert not learn_canary_miss(db_path, "one more", "session-1")
    assert learn_canary_miss(db_path, "one more", "session-2")
