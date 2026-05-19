from flask import Blueprint, request, jsonify
from backend.controllers.training_controller import handle_training_plan
from backend.utils.validators import validate_player_input, FEATURE_COLS

training_bp = Blueprint("training", __name__, url_prefix="/api/training")


@training_bp.route("/plan", methods=["POST"])
def training_plan():
    """
    Generate a personalised weekly training plan.
    Optionally accepts a 'position' field; otherwise uses the top predicted position.
    """
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs    = {c: int(data[c]) for c in FEATURE_COLS}
    position = data.get("position")
    return jsonify(handle_training_plan(attrs, position=position))
