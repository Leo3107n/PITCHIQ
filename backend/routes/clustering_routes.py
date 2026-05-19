from flask import Blueprint, request, jsonify
from backend.controllers.clustering_controller import (
    handle_similar_players, handle_cluster_info
)
from backend.utils.validators import validate_player_input, FEATURE_COLS

clustering_bp = Blueprint("clustering", __name__, url_prefix="/api/cluster")


@clustering_bp.route("/similar", methods=["POST"])
def similar():
    """Find the N most similar players by playing style."""
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs = {c: int(data[c]) for c in FEATURE_COLS}
    top_n = min(int(data.get("top_n", 5)), 20)   # cap at 20
    return jsonify(handle_similar_players(attrs, top_n=top_n))


@clustering_bp.route("/info", methods=["POST"])
def cluster_info():
    """Return cluster assignment and statistics for a player."""
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400

    attrs = {c: int(data[c]) for c in FEATURE_COLS}
    return jsonify(handle_cluster_info(attrs))
