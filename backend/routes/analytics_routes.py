from flask import Blueprint, request, jsonify
from backend.controllers.analytics_controller import (
    handle_overview, handle_position_profiles
)
from backend.utils.validators import validate_player_input, FEATURE_COLS

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/overview", methods=["POST"])
def overview():
    """Full analytics overview: rating, predictions, gap analysis, similar players."""
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs = {c: int(data[c]) for c in FEATURE_COLS}
    return jsonify(handle_overview(attrs))


@analytics_bp.route("/position-profiles", methods=["GET"])
def position_profiles():
    """Return ideal attribute profiles for all 11 positions."""
    return jsonify(handle_position_profiles())
