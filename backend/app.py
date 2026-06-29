"""
PitchIQ — Flask Application Factory
=====================================
Start the server:
    python backend/app.py
    python -m backend.app
"""
import sys
import os
import logging

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.database.db import init_db

# ── Routes ───────────────────────────────────────────────────────────────────
from backend.routes.prediction_routes  import prediction_bp
from backend.routes.clustering_routes  import clustering_bp
from backend.routes.training_routes    import training_bp
from backend.routes.analytics_routes   import analytics_bp
from backend.routes.evaluation_routes  import evaluation_bp
from backend.routes.session_routes     import session_bp

# ── Middleware ────────────────────────────────────────────────────────────────
from backend.middleware.error_handler  import register_error_handlers
from backend.middleware.request_logger import register_request_logger


def configure_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )


def create_app() -> Flask:
    configure_logging(Config.LOG_LEVEL)
    logger = logging.getLogger("pitchiq")

    app = Flask(__name__)
    app.config.from_object(Config)

    # ── CORS ─────────────────────────────────────────────────────────
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    # ── Database ─────────────────────────────────────────────────────
    with app.app_context():
        init_db()
        logger.info("Database initialised at %s", Config.DB_PATH)

    # ── Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(prediction_bp)
    app.register_blueprint(clustering_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(session_bp)

    # ── Middleware ────────────────────────────────────────────────────
    register_error_handlers(app)
    register_request_logger(app)

    # ── Health check ──────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({
            "status":  "ok",
            "service": "PitchIQ API",
            "version": "2.0.0",
        })

    # ── API map ───────────────────────────────────────────────────────
    @app.route("/api")
    def api_index():
        return jsonify({
            "endpoints": {
                "health":              "GET  /api/health",
                "predict_positions":   "POST /api/predict/positions",
                "gap_analysis":        "POST /api/predict/gap-analysis",
                "full_analysis":       "POST /api/predict/full",
                "similar_players":     "POST /api/cluster/similar",
                "cluster_info":        "POST /api/cluster/info",
                "training_plan":       "POST /api/training/plan",
                "analytics_overview":  "POST /api/analytics/overview",
                "position_profiles":   "GET  /api/analytics/position-profiles",
                "all_model_metrics":   "GET  /api/evaluate/models",
                "model_metrics":       "GET  /api/evaluate/models/<name>",
                "confusion_matrix":    "GET  /api/evaluate/confusion-matrix/<name>",
                "list_sessions":       "GET  /api/sessions/",
                "get_session":         "GET  /api/sessions/<token>",
                "delete_session":      "DELETE /api/sessions/<token>",
            }
        })

    logger.info("PitchIQ API ready — %d blueprints registered", 6)

    # Print all registered routes at startup so you can verify
    predict_routes = [r.rule for r in app.url_map.iter_rules() if "predict" in r.rule]
    logger.info("Predict routes: %s", predict_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False,   # prevents double-startup that drops routes
    )
