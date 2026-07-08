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

    # ── MongoDB ──────────────────────────────────────────────────────
    MONGO_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB   = os.getenv("MONGO_DB",  "pitchiq")

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # ── OpenAI ───────────────────────────────────────────────────────
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
