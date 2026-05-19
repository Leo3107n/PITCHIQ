"""
Centralised error handlers — always return JSON.
"""
import logging
from flask import jsonify

logger = logging.getLogger("pitchiq.errors")


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "Unprocessable entity", "message": str(e)}), 422

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Unhandled server error: %s", e)
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.exception("Unhandled exception: %s", e)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
