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
sys.path.insert(0, str(_root / "backend"))

from app.main import app  # noqa: E402
