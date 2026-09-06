"""Vercel serverless entry point for Kifayat AI."""
import os

os.environ.setdefault("KIFAYAT_IN_MEMORY", "1")
os.environ.setdefault("KIFAYAT_CORS_ORIGINS", "*")

from app.main import app  # noqa: E402
