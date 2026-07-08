"""
WSGI entry point for Gunicorn (production server).
Render uses this file to start the app:
    gunicorn wsgi:app

Run locally in production mode:
    gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2
"""
import sys
import os

# Ensure project root is in Python path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app import create_app

app = create_app()
