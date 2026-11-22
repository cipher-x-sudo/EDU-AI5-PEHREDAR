import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .state import session_key

MAX_PER_SOURCE_DAY = 20


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def is_known_attack(db_path: Path, normalized_text: str) -> bool:
    with sqlite3.connect(db_path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS confirmed_attacks "
            "(text_hash TEXT PRIMARY KEY, source_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        return db.execute(
            "SELECT 1 FROM confirmed_attacks WHERE text_hash = ?", (text_hash(normalized_text),)
        ).fetchone() is not None


def learn_canary_miss(db_path: Path, normalized_text: str, session_id: str | None) -> bool:
    if not session_id or not normalized_text:
        return False
    source = session_key(session_id)
    today = datetime.now(timezone.utc).date().isoformat()
    with sqlite3.connect(db_path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS confirmed_attacks "
            "(text_hash TEXT PRIMARY KEY, source_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        count = db.execute(
            "SELECT COUNT(*) FROM confirmed_attacks WHERE source_hash = ? AND created_at >= ?",
            (source, today),
        ).fetchone()[0]
        if count >= MAX_PER_SOURCE_DAY:
            return False
        cursor = db.execute(
            "INSERT OR IGNORE INTO confirmed_attacks(text_hash, source_hash, created_at) VALUES (?, ?, ?)",
            (text_hash(normalized_text), source, datetime.now(timezone.utc).isoformat()),
        )
        return cursor.rowcount == 1
