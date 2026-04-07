"""ASGI entrypoint to make running with uvicorn robust regardless of cwd.

Usage: uvicorn asgi:app --reload
"""
import sys
import os

# Ensure project root (this file's directory) is on sys.path so 'app' package is importable.
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app  # noqa: E402

