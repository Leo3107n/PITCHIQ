"""
Evaluation Service
===================
Serves pre-computed model metrics from reports/metrics.json.
This file is written by the training pipeline so the API never
needs to re-run predictions on 50k+ rows at request time.

Falls back to live computation only if metrics.json is missing.
"""
import os
import sys
import json
import logging

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from backend.config import Config

logger = logging.getLogger("pitchiq.evaluation")

METRICS_JSON = os.path.join(ROOT, "reports", "metrics.json")

MODEL_FILES = {
    "knn":               "knn_model.pkl",
    "decision_tree":     "decision_tree.pkl",
    "random_forest":     "random_forest.pkl",
    "svm":               "svm_model.pkl",
    "neural_network":    "neural_network.pkl",
    "gradient_boosting": "gradient_boosting.pkl",
    "best":              "best_classifier.pkl",
}

MODEL_DISPLAY = {
    "knn":               "K-Nearest Neighbours",
    "decision_tree":     "Decision Tree",
    "random_forest":     "Random Forest",
    "svm":               "Support Vector Machine",
    "neural_network":    "Neural Network (MLP)",
    "gradient_boosting": "Gradient Boosting",
}

# ── In-memory cache ───────────────────────────────────────────────────────────
_metrics_cache: dict | None = None
_matrix_cache:  dict        = {}


def _load_metrics_json() -> dict | None:
    """Read pre-computed metrics from JSON file. Returns None if missing."""
    if not os.path.exists(METRICS_JSON):
        return None
    try:
        with open(METRICS_JSON, "r") as f:
            data = json.load(f)
        logger.info("Loaded metrics from %s", METRICS_JSON)
        return data
    except Exception as e:
        logger.warning("Could not read metrics.json: %s", e)
        return None


def _compute_live() -> dict:
    """
    Fallback: compute metrics by running predictions on the test split.
    Only used if metrics.json doesn't exist (e.g. first run before training).
    """
    logger.warning("metrics.json not found — computing live (this is slow).")
    from ml_models.evaluation.accuracy_metrics import evaluate_model

    results = {}
    for name, filename in MODEL_FILES.items():
        if name == "best":
            continue
        path = os.path.join(Config.MODELS_DIR, filename)
        if not os.path.exists(path):
            continue
        try:
            m = evaluate_model(path)
            m.pop("report", None)
            results[name] = m
        except Exception as e:
            logger.error("Failed to evaluate %s: %s", name, e)
            results[name] = {"error": str(e)}

    valid    = {k: v for k, v in results.items() if "f1" in v}
    best_key = max(valid, key=lambda k: valid[k]["f1"]) if valid else None
    return {"models": results, "best_model": best_key}


def get_all_metrics() -> dict:
    """Returns all model metrics. Reads from JSON cache, falls back to live."""
    global _metrics_cache
    if _metrics_cache is not None:
        return _metrics_cache

    data = _load_metrics_json()
    if data is None:
        data = _compute_live()

    _metrics_cache = data
    return _metrics_cache


def get_model_metrics(model_name: str = "best") -> dict:
    """Returns metrics for a single named model."""
    if model_name not in MODEL_FILES:
        raise ValueError(f"Unknown model '{model_name}'. Valid: {list(MODEL_FILES.keys())}")

    all_m = get_all_metrics()

    # "best" → look up which model is best, return its metrics
    if model_name == "best":
        best_key = all_m.get("best_model")
        if best_key and best_key in all_m.get("models", {}):
            return {
                "model":   best_key,
                "display": MODEL_DISPLAY.get(best_key, best_key),
                "metrics": all_m["models"][best_key],
            }

    if model_name in all_m.get("models", {}):
        return {
            "model":   model_name,
            "display": MODEL_DISPLAY.get(model_name, model_name),
            "metrics": all_m["models"][model_name],
        }

    raise FileNotFoundError(f"Metrics not found for model: {model_name}")


def get_model_confusion_matrix(model_name: str = "best") -> dict:
    """
    Returns confusion matrix for a model.
    Computed on demand and cached — only runs once per model per server session.
    """
    global _matrix_cache

    # Resolve "best" to actual model key
    if model_name == "best":
        all_m = get_all_metrics()
        model_name = all_m.get("best_model", "svm")

    if model_name in _matrix_cache:
        return _matrix_cache[model_name]

    filename = MODEL_FILES.get(model_name)
    if not filename:
        raise ValueError(f"Unknown model '{model_name}'.")

    path = os.path.join(Config.MODELS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {filename}")

    logger.info("Computing confusion matrix for %s ...", model_name)
    from ml_models.evaluation.confusion_matrix import get_confusion_matrix
    cm, labels = get_confusion_matrix(path)

    result = {
        "model":   model_name,
        "display": MODEL_DISPLAY.get(model_name, model_name),
        "labels":  labels,
        "matrix":  cm.tolist(),
    }
    _matrix_cache[model_name] = result
    logger.info("Confusion matrix cached for %s", model_name)
    return result


def invalidate_cache():
    """Call after retraining to force fresh reads."""
    global _metrics_cache, _matrix_cache
    _metrics_cache = None
    _matrix_cache  = {}
    logger.info("Evaluation cache cleared.")
