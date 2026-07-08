"""
Scouting Controller
Calls the scouting service, persists the report if a session token is given.
Never touches Flask request/response objects.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import logging
from backend.services.scouting_service import generate_scouting_report, ScoutingReportError
from backend.database.db import get_session, get_connection

logger = logging.getLogger("pitchiq.scouting")


def handle_generate_report(context: dict) -> dict:
    """
    context keys expected:
        player_name, player_age, attributes,
        predictions, gap_analysis, similar_players,
        session_token (optional)
    Returns: {"report": "...", "session_token": "..."} or raises ScoutingReportError
    """
    report = generate_scouting_report(context)

    # Persist to session if a token was provided
    session_token = context.get("session_token")
    if session_token:
        try:
            _save_report_to_session(session_token, report)
        except Exception as e:
            # Non-fatal — report still returned even if save fails
            logger.warning("Could not save report to session %s: %s", session_token, e)

    return {"report": report, "session_token": session_token}


def _save_report_to_session(token: str, report: str):
    """Add/update the scouting_report column for an existing session."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE analysis_sessions SET scouting_report = ? WHERE session_token = ?",
            (report, token)
        )
