import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Config:
    # ── Flask ────────────────────────────────────────────────────────
    DEBUG      = os.getenv("FLASK_DEBUG", "0") == "1"
    PORT       = int(os.getenv("PORT", 5000))
    SECRET_KEY = os.getenv("SECRET_KEY", "pitchiq-dev-secret-change-in-prod")

    # ── Paths ────────────────────────────────────────────────────────
    ROOT_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    MODELS_DIR = os.path.join(ROOT_DIR, "saved_models")
    DATA_DIR   = os.path.join(ROOT_DIR, "dataset", "processed")
    DB_PATH    = os.path.join(ROOT_DIR, "backend", "database", "pitchiq.db")

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
