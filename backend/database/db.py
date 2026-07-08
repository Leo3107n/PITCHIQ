"""
PitchIQ — MongoDB database layer.
Replaces the previous SQLite implementation with PyMongo.
Public API is unchanged — all callers (controllers, scouting controller,
conftest patches) work without modification.

Collection: analysis_sessions
Each document stores one full player analysis session.
"""
import uuid
import logging
from datetime import datetime, timezone

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection

from backend.config import Config

logger = logging.getLogger("pitchiq.db")

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

# ── Connection pool (module-level singleton) ──────────────────────────────────
_client: MongoClient | None = None
_col:    Collection  | None = None


def _get_collection() -> Collection:
    """Returns the analysis_sessions collection, creating the client once."""
    global _client, _col
    if _col is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        db   = _client[Config.MONGO_DB]
        _col = db["analysis_sessions"]
        # Indexes
        _col.create_index("session_token", unique=True)
        _col.create_index([("created_at", DESCENDING)])
        logger.info("MongoDB connected: %s / %s", Config.MONGO_URI, Config.MONGO_DB)
    return _col


def init_db():
    """Verifies the MongoDB connection and ensures indexes exist."""
    try:
        col = _get_collection()
        col.database.client.admin.command("ping")
        logger.info("MongoDB ping OK — collection: analysis_sessions")
        return True
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        raise


# ── Session CRUD ──────────────────────────────────────────────────────────────

def save_session(player_name: str, player_age: int, attrs: dict,
                 predictions=None, gap=None, plan=None, cluster=None) -> str:
    """Inserts a new analysis session. Returns the UUID session_token."""
    token = str(uuid.uuid4())
    doc = {
        "session_token":  token,
        "player_name":    player_name or "Anonymous",
        "player_age":     player_age  or 0,
        "created_at":     datetime.now(timezone.utc),
        # Raw attributes
        **{c: attrs.get(c, 50) for c in FEATURE_COLS},
        # Computed results stored natively as dicts/lists (no JSON serialisation needed)
        "predictions":    predictions or None,
        "gap_analysis":   gap         or None,
        "training_plan":  plan        or None,
        "cluster_info":   cluster     or None,
        "scouting_report": None,
    }
    _get_collection().insert_one(doc)
    return token


def get_session(token: str) -> dict | None:
    """Fetches a session by token. Returns None if not found."""
    doc = _get_collection().find_one({"session_token": token})
    return _mongo_to_dict(doc) if doc else None


def list_sessions(limit: int = 20, offset: int = 0) -> list:
    """
    Returns the most recent sessions, summary only.
    Projection excludes the large computed blobs for performance.
    """
    projection = {
        "_id": 0,
        "session_token": 1, "player_name": 1, "player_age": 1, "created_at": 1,
        **{c: 1 for c in FEATURE_COLS},
        # Include predictions so Sessions page can show top position
        "predictions": 1,
    }
    cursor = (
        _get_collection()
        .find({}, projection)
        .sort("created_at", DESCENDING)
        .skip(offset)
        .limit(limit)
    )
    return [_mongo_to_dict(d) for d in cursor]


def delete_session(token: str) -> bool:
    """Deletes a session by token. Returns True if a document was deleted."""
    result = _get_collection().delete_one({"session_token": token})
    return result.deleted_count > 0


def session_count() -> int:
    return _get_collection().count_documents({})


def get_connection():
    """
    Compatibility shim used by scouting_controller to save a report.
    Returns a context-manager-compatible object that exposes .execute().
    """
    return _MongoCompat(_get_collection())


# ── Mongo → plain dict ────────────────────────────────────────────────────────

def _mongo_to_dict(doc: dict) -> dict:
    """Converts a MongoDB document to a plain dict safe for JSON serialisation."""
    d = dict(doc)
    d.pop("_id", None)                         # remove ObjectId
    if isinstance(d.get("created_at"), datetime):
        d["created_at"] = d["created_at"].isoformat()
    return d


# ── Compatibility shim for scouting_controller ────────────────────────────────

class _MongoCompat:
    """
    Minimal context-manager shim so scouting_controller can call:
        with get_connection() as conn:
            conn.execute("UPDATE analysis_sessions SET scouting_report = ? ...", (report, token))
    We parse only the UPDATE scouting_report pattern — all other SQL is ignored.
    """
    def __init__(self, col: Collection):
        self._col = col

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def execute(self, sql: str, params: tuple = ()):
        sql_lower = sql.strip().lower()
        if "update" in sql_lower and "scouting_report" in sql_lower:
            report, token = params[0], params[1]
            self._col.update_one(
                {"session_token": token},
                {"$set": {"scouting_report": report}},
            )
