"""
Pytest fixtures shared across all backend tests.
Uses mongomock to replace PyMongo with an in-memory MongoDB implementation —
no real MongoDB instance required for tests.
"""
import sys
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

# ── Patch MongoDB with mongomock BEFORE importing the app ─────────────────────
import mongomock
import backend.database.db as _db_module
from pymongo import DESCENDING

# Create a single mongomock client shared across the test session
_mock_client = mongomock.MongoClient()
_mock_db     = _mock_client["pitchiq_test"]
_mock_col    = _mock_db["analysis_sessions"]

# Ensure indexes exist on the mock collection
_mock_col.create_index("session_token", unique=True)
_mock_col.create_index([("created_at", DESCENDING)])


def _get_mock_collection():
    return _mock_col


# Patch the module-level collection getter so all db.py calls use mongomock
_db_module._get_collection = _get_mock_collection
_db_module.init_db         = lambda: True   # skip real MongoDB ping in tests

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


@pytest.fixture(autouse=True)
def clear_sessions():
    """Wipe the mock collection before each test for isolation."""
    _mock_col.delete_many({})
    yield
    _mock_col.delete_many({})


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
