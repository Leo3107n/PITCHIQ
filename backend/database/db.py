"""
SQLite database connection and session management for PitchIQ.
Uses Python's built-in sqlite3 — no ORM required.
"""
import sqlite3
import json
import os
import uuid
from datetime import datetime

from backend.config import Config

_DB_PATH = Config.DB_PATH


def get_connection() -> sqlite3.Connection:
    """Returns a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Creates tables from schema.sql if they don't exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with get_connection() as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
    return True


# ── Session CRUD ─────────────────────────────────────────────────────────────

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]


def save_session(player_name: str, player_age: int, attrs: dict,
                 predictions=None, gap=None, plan=None, cluster=None) -> str:
    """
    Persists a full analysis session. Returns the session_token (UUID).
    """
    token = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analysis_sessions
                (session_token, player_name, player_age,
                 pace, shooting, passing, dribbling, defending,
                 physical, stamina, strength, agility, vision,
                 predictions, gap_analysis, training_plan, cluster_info)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                token,
                player_name or "Anonymous",
                player_age,
                *[attrs.get(c, 50) for c in FEATURE_COLS],
                json.dumps(predictions) if predictions else None,
                json.dumps(gap)         if gap         else None,
                json.dumps(plan)        if plan        else None,
                json.dumps(cluster)     if cluster     else None,
            )
        )
    return token


def get_session(token: str) -> dict | None:
    """Fetches a session by token. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM analysis_sessions WHERE session_token = ?", (token,)
        ).fetchone()
    if not row:
        return None
    return _row_to_dict(row)


def list_sessions(limit: int = 20, offset: int = 0) -> list:
    """Returns the most recent sessions (summary only, no JSON blobs)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, session_token, player_name, player_age, created_at,
                   pace, shooting, passing, dribbling, defending,
                   physical, stamina, strength, agility, vision
            FROM analysis_sessions
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_session(token: str) -> bool:
    """Deletes a session. Returns True if a row was deleted."""
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM analysis_sessions WHERE session_token = ?", (token,)
        )
    return cur.rowcount > 0


def session_count() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM analysis_sessions").fetchone()[0]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("predictions", "gap_analysis", "training_plan", "cluster_info"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d
