from flask import Blueprint, request, jsonify
from backend.controllers.session_controller import (
    handle_get_session, handle_list_sessions, handle_delete_session
)

session_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@session_bp.route("/", methods=["GET"])
def list_sessions():
    """List recent analysis sessions (paginated)."""
    limit  = min(int(request.args.get("limit",  20)), 100)
    offset = int(request.args.get("offset", 0))
    return jsonify(handle_list_sessions(limit=limit, offset=offset))


@session_bp.route("/<token>", methods=["GET"])
def get_session(token: str):
    """Retrieve a full session by its token."""
    session = handle_get_session(token)
    if not session:
        return jsonify({"error": "Session not found."}), 404
    return jsonify(session)


@session_bp.route("/<token>", methods=["DELETE"])
def delete_session(token: str):
    """Delete a session by its token."""
    return jsonify(handle_delete_session(token))
