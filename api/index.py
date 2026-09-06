"""Vercel serverless entry point for Kifayat AI."""
import os
import sys
from pathlib import Path

os.environ.setdefault("KIFAYAT_IN_MEMORY", "1")
os.environ.setdefault("KIFAYAT_CORS_ORIGINS", "*")

_api_dir = str(Path(__file__).resolve().parent)
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

from app.db import Base, engine, SessionLocal  # noqa: E402
from app.models import DatasetMeta, Price  # noqa: E402
from app.ingestion.seed_fallback import seed_fallback  # noqa: E402
from sqlalchemy import select  # noqa: E402

# Create tables + seed BEFORE importing the app
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if not db.scalar(select(DatasetMeta)):
        seed_fallback(db)
except Exception:
    pass
finally:
    db.close()

from app.main import app  # noqa: E402
