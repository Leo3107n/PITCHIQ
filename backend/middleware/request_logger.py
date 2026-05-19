"""
Request/Response logger with timing.
Logs: METHOD /path → status_code  (Xms)
"""
import logging
import time
from flask import request, g

logger = logging.getLogger("pitchiq.http")


def register_request_logger(app):
    @app.before_request
    def start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def log_response(response):
        elapsed_ms = round((time.perf_counter() - g.start_time) * 1000, 1)
        logger.info(
            "%s %s → %d  (%sms)",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response
