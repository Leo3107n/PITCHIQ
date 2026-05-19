from flask import Blueprint, request, jsonify
from backend.controllers.prediction_controller import (
    handle_predict, handle_gap_analysis, handle_full_analysis
)
from backend.utils.validators import validate_player_input, FEATURE_COLS

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/predict")


@prediction_bp.route("/positions", methods=["POST"])
def predict():
    """Predict top-5 positions with confidence scores."""
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs = {c: int(data[c]) for c in FEATURE_COLS}
    return jsonify(handle_predict(attrs))


@prediction_bp.route("/gap-analysis", methods=["POST"])
def gap():
    """Gap analysis for a specific position."""
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    position = data.get("position")
    if not position:
        return jsonify({"error": "Missing 'position' field."}), 400

    attrs = {c: int(data[c]) for c in FEATURE_COLS}
    return jsonify(handle_gap_analysis(attrs, position))


@prediction_bp.route("/full", methods=["POST"])
def full_analysis():
    """
    Full pipeline in one call:
    predictions + gap analysis + similar players + cluster + training plan.
    Persists the session and returns a session_token.
    """
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs       = {c: int(data[c]) for c in FEATURE_COLS}
    player_name = data.get("player_name", "")
    player_age  = int(data.get("player_age", 0))
    save        = data.get("save", True)

    result = handle_full_analysis(
        attrs=attrs,
        player_name=player_name,
        player_age=player_age,
        save=save,
    )
    return jsonify(result)
