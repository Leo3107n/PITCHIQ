from flask import Blueprint, jsonify
from backend.controllers.evaluation_controller import (
    handle_model_metrics,
    handle_all_metrics,
    handle_confusion_matrix,
)

evaluation_bp = Blueprint("evaluation", __name__, url_prefix="/api/evaluate")


@evaluation_bp.route("/models", methods=["GET"])
def all_models():
    """Return accuracy, precision, recall, F1 for all trained classifiers."""
    result = handle_all_metrics()
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@evaluation_bp.route("/models/<model_name>", methods=["GET"])
def model_metrics(model_name: str):
    """
    Return metrics for a specific model.
    Valid: knn, decision_tree, random_forest, svm, neural_network, best
    """
    result = handle_model_metrics(model_name)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@evaluation_bp.route("/confusion-matrix/<model_name>", methods=["GET"])
def confusion_matrix(model_name: str):
    """Return the confusion matrix for a specific model."""
    result = handle_confusion_matrix(model_name)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@evaluation_bp.route("/status", methods=["GET"])
def status():
    """Check whether pre-computed metrics are available."""
    import os
    from backend.config import Config
    metrics_json = os.path.join(
        os.path.abspath(os.path.join(Config.ROOT_DIR, "reports")),
        "metrics.json"
    )
    return jsonify({
        "metrics_ready": os.path.exists(metrics_json),
        "metrics_path":  metrics_json,
    })
