"""
Session Controller
Handles CRUD operations for persisted analysis sessions.
"""
from backend.database.db import (
    get_session, list_sessions, delete_session, session_count
)


def handle_get_session(token: str) -> dict | None:
    return get_session(token)


def handle_list_sessions(limit: int = 20, offset: int = 0) -> dict:
    sessions = list_sessions(limit=limit, offset=offset)
    total    = session_count()
    return {
        "sessions": sessions,
        "total":    total,
        "limit":    limit,
        "offset":   offset,
    }


def handle_delete_session(token: str) -> dict:
    deleted = delete_session(token)
    return {"deleted": deleted, "session_token": token}
