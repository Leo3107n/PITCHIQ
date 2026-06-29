"""
PitchIQ Backend Starter
========================
Run from the project root:
    python start_backend.py

This ensures Python's module resolution works correctly for all imports.
Do NOT run from inside the backend/ folder.
"""
import sys
import os

# Guarantee the project root is in sys.path before anything else loads
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Now import and run the app
from backend.app import create_app
from backend.config import Config

if __name__ == "__main__":
    app = create_app()
    print(f"\nPitchIQ API running at http://localhost:{Config.PORT}")
    print(f"Frontend expected at: http://localhost:5173\n")
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=False,          # debug=False avoids the reloader double-start issue
        use_reloader=False,
    )
