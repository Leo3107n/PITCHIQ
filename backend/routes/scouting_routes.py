from flask import Blueprint, request, jsonify
from backend.controllers.scouting_controller import handle_generate_report
from backend.services.scouting_service import ScoutingReportError
from backend.utils.validators import validate_player_input, FEATURE_COLS
from backend.database.db import get_session

scouting_bp = Blueprint("scouting", __name__, url_prefix="/api/scouting")


@scouting_bp.route("/report", methods=["POST"])
def generate_report():
    data = request.get_json(force=True)
    valid, err = validate_player_input(data)
    if not valid:
        return jsonify({"error": err}), 400
    if not data.get("predictions"):
        return jsonify({"error": "Missing 'predictions' field. Run ML analysis first."}), 400
    if not data.get("gap_analysis"):
        return jsonify({"error": "Missing 'gap_analysis' field. Run ML analysis first."}), 400

    context = {
        "player_name":     data.get("player_name", ""),
        "player_age":      data.get("player_age", 0),
        "attributes":      {c: int(data[c]) for c in FEATURE_COLS},
        "predictions":     data["predictions"],
        "gap_analysis":    data["gap_analysis"],
        "similar_players": data.get("similar_players", []),
        "session_token":   data.get("session_token"),
    }
    try:
        result = handle_generate_report(context)
        return jsonify(result)
    except ScoutingReportError as e:
        return jsonify({"error": e.user_message, "retry": e.retry}), 502
    except Exception as e:
        return jsonify({"error": "Unexpected error generating report.", "retry": True}), 500


@scouting_bp.route("/<token>", methods=["GET"])
def get_saved_report(token):
    session = get_session(token)
    if not session:
        return jsonify({"error": "Session not found."}), 404
    report = session.get("scouting_report")
    if not report:
        return jsonify({"error": "No scouting report saved for this session."}), 404
    return jsonify({"report": report, "session_token": token})
