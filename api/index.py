"""Vercel serverless entry point for Kifayat AI."""
import os
import sys
from pathlib import Path

os.environ.setdefault("KIFAYAT_IN_MEMORY", "1")
os.environ.setdefault("KIFAYAT_CORS_ORIGINS", "*")

# Vercel's CWD is /var/task/, but app code is at api/app/
# Add api/ to sys.path so "from app.main import app" resolves
_api_dir = str(Path(__file__).resolve().parent)
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

from app.main import app  # noqa: E402
