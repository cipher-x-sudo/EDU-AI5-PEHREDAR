import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS review_queue "
    "(id INTEGER PRIMARY KEY, text_hash TEXT UNIQUE NOT NULL, risk REAL NOT NULL, "
    "language TEXT NOT NULL, tags TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', "
    "label TEXT, reviewer TEXT, created_at TEXT NOT NULL, reviewed_at TEXT)"
)


def enqueue(db_path: Path, text_hash: str, risk: float, language: str, tags: list[str]) -> None:
    with sqlite3.connect(db_path) as db:
        db.execute(SCHEMA)
        db.execute(
            "INSERT OR IGNORE INTO review_queue(text_hash, risk, language, tags, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (text_hash, risk, language, ",".join(tags), datetime.now(timezone.utc).isoformat()),
        )


def pending(db_path: Path) -> list[dict]:
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        db.execute(SCHEMA)
        return [dict(row) for row in db.execute(
            "SELECT id, text_hash, risk, language, tags, created_at FROM review_queue "
            "WHERE status = 'pending' ORDER BY id LIMIT 100"
        )]


def submit(db_path: Path, item_id: int, label: str, reviewer: str, text_hash: str) -> bool:
    with sqlite3.connect(db_path) as db:
        db.execute(SCHEMA)
        row = db.execute(
            "SELECT text_hash FROM review_queue WHERE id = ? AND status = 'pending'", (item_id,)
        ).fetchone()
        if not row:
            return False
        if row[0] != text_hash:
            raise ValueError("Submitted text does not match the pending review hash")
        db.execute(
            "UPDATE review_queue SET status = 'reviewed', label = ?, reviewer = ?, reviewed_at = ? WHERE id = ?",
            (label, reviewer, datetime.now(timezone.utc).isoformat(), item_id),
        )
        if label == "attack":
            db.execute(
                "CREATE TABLE IF NOT EXISTS confirmed_attacks "
                "(text_hash TEXT PRIMARY KEY, source_hash TEXT NOT NULL, created_at TEXT NOT NULL)"
            )
            db.execute(
                "INSERT OR IGNORE INTO confirmed_attacks(text_hash, source_hash, created_at) VALUES (?, ?, ?)",
                (row[0], f"human-review:{item_id}", datetime.now(timezone.utc).isoformat()),
            )
        return True
