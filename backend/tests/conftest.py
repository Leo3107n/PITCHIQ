"""
Pytest fixtures shared across all backend tests.
"""
import sys
import os
import sqlite3
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

# ── Patch DB to in-memory BEFORE importing app ────────────────────────────────
import backend.database.db as _db_module

_SCHEMA_PATH = os.path.join(ROOT, "backend", "database", "schema.sql")

# Override get_connection to use a shared in-memory connection
_mem_conn = None

def _get_mem_connection():
    global _mem_conn
    if _mem_conn is None:
        _mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
        _mem_conn.row_factory = sqlite3.Row
        _mem_conn.execute("PRAGMA foreign_keys=ON")
        with open(_SCHEMA_PATH) as f:
            _mem_conn.executescript(f.read())
    return _mem_conn

_db_module.get_connection = _get_mem_connection
_db_module.init_db = lambda: True   # schema already applied above

# ── Now import the app ────────────────────────────────────────────────────────
from backend.app import create_app


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture
def valid_attrs():
    return {
        "pace": 75, "shooting": 80, "passing": 65,
        "dribbling": 72, "defending": 30, "physical": 70,
        "stamina": 72, "strength": 68, "agility": 74, "vision": 66,
    }


@pytest.fixture
def weak_attrs():
    return {
        "pace": 50, "shooting": 45, "passing": 55,
        "dribbling": 50, "defending": 40, "physical": 52,
        "stamina": 55, "strength": 48, "agility": 52, "vision": 50,
    }
