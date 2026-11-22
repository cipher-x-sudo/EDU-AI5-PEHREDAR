import hashlib
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


def session_key(session_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", session_id):
        raise ValueError("Invalid x-session-id")
    return hashlib.sha256(session_id.encode()).hexdigest()


def update_escalation(db_path: Path, session_id: str | None, risk: float) -> float:
    if not session_id:
        return 0.0
    key = session_key(session_id)
    with sqlite3.connect(db_path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS sessions "
            "(session_hash TEXT PRIMARY KEY, scores TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        db.execute("DELETE FROM sessions WHERE updated_at < ?", (cutoff,))
        existing = db.execute("SELECT scores FROM sessions WHERE session_hash = ?", (key,)).fetchone()
        scores = json.loads(existing[0]) if existing else []
        scores = (scores + [risk])[-5:]
        db.execute(
            "INSERT INTO sessions(session_hash, scores, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(session_hash) DO UPDATE SET scores=excluded.scores, updated_at=excluded.updated_at",
            (key, json.dumps(scores), datetime.now(timezone.utc).isoformat()),
        )
    weights = list(range(1, len(scores) + 1))
    return sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
