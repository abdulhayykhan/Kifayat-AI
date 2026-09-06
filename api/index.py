"""Vercel serverless entry point for Kifayat AI.

Loads the FastAPI app and initializes an in-memory SQLite database
from the bundled fallback workbook on cold start.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("KIFAYAT_IN_MEMORY", "1")
os.environ.setdefault("KIFAYAT_CORS_ORIGINS", "*")

_root = Path(__file__).resolve().parent.parent
_backend = _root / "backend"

# Add backend to path so `app.*` imports resolve
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

# Also add project root for absolute imports
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.main import app  # noqa: E402
