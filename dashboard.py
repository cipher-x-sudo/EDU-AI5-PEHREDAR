import os
import sqlite3
from pathlib import Path

import streamlit as st

DB_PATH = Path(os.getenv("PEHREDAR_DB_PATH", "/state/pehredar.db"))
st.set_page_config(page_title="Pehredar", layout="wide")
st.title("Pehredar")
st.caption("Local decisions and review metadata. Prompt text is not stored.")

if not DB_PATH.exists():
    st.info("No gateway database found yet.")
    st.stop()

with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as db:
    decisions = db.execute(
        "SELECT action, COUNT(*) FROM decisions GROUP BY action ORDER BY action"
    ).fetchall()
    recent = db.execute(
        "SELECT created_at, action, risk, language, tags, text_hash, layer_latency_ms FROM decisions "
        "ORDER BY id DESC LIMIT 100"
    ).fetchall()
    review_table = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='review_queue'"
    ).fetchone()
    pending_count = db.execute(
        "SELECT COUNT(*) FROM review_queue WHERE status='pending'"
    ).fetchone()[0] if review_table else 0

columns = st.columns(4)
counts = dict(decisions)
for column, name in zip(columns, ("allow", "warn", "block")):
    column.metric(name.title(), counts.get(name, 0))
columns[3].metric("Pending review", pending_count)
st.subheader("Recent decisions")
st.dataframe(
    [
        {"time": time, "action": action, "risk": risk, "language": language,
         "tags": tags, "text_hash": digest, "layer_latency_ms": latencies}
        for time, action, risk, language, tags, digest, latencies in recent
    ],
    use_container_width=True,
)
