from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import IN_MEMORY, Base, engine, SessionLocal, get_db
from .models import DatasetMeta
from .ingestion.seed_fallback import seed_fallback, _upsert
from .ingestion.parse_excel import parse_annexure
from .ingestion.discover import download_latest
from .analytics.volatility import all_summaries, item_summary
from .nlu.roman_urdu import match_items
from .config import CORS_ORIGINS, HISTORY_DIR, IS_VERCEL, MAX_UPLOAD_MB

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
_initialized = False


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="User query in Roman Urdu or English")


def _init_db():
    """Create tables and seed fallback data. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.scalar(select(DatasetMeta))
        if not existing:
            seed_fallback(db)
    except Exception:
        pass
    finally:
        db.close()

    if IS_VERCEL:
        db = SessionLocal()
        try:
            meta = db.get(DatasetMeta, 1)
            path = download_latest()
            records = parse_annexure(path)
            for record in records:
                _upsert(db, record)
            if not meta:
                meta = DatasetMeta(id=1)
            meta.source = "live"
            meta.week_ending = records[0]["week_ending"]
            meta.updated_at = datetime.now(timezone.utc)
            db.merge(meta)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()

    _initialized = True


def refresh(db: Optional[Session] = None) -> dict:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        try:
            path = download_latest()
            records = parse_annexure(path)
            for record in records:
                _upsert(db, record)
            meta = db.get(DatasetMeta, 1) or DatasetMeta(id=1)
            meta.source = "live"
            meta.week_ending = records[0]["week_ending"]
            meta.updated_at = datetime.now(timezone.utc)
            db.merge(meta)
            db.commit()
            return {"source": "live", "records": len(records)}
        except Exception as exc:
            count = seed_fallback(db)
            meta_row = db.get(DatasetMeta, 1)
            return {
                "source": meta_row.source if meta_row else "fallback_cached",
                "records": count,
                "detail": str(exc),
            }
    finally:
        if own_session:
            db.close()


if IS_VERCEL:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _init_db()
        yield
else:
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler(timezone="Asia/Karachi")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(bind=engine)
        refresh()
        scheduler.add_job(
            refresh, "cron", day_of_week="fri", hour=18, minute=0,
            id="pbs-refresh", replace_existing=True,
        )
        scheduler.start()
        yield
        scheduler.shutdown(wait=False)


app = FastAPI(title="Kifayat AI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def meta(db: Session) -> dict:
    row = db.get(DatasetMeta, 1)
    return {
        "source": row.source if row else "fallback_cached",
        "week_ending": row.week_ending.isoformat() if row and row.week_ending else None,
        "last_updated": row.updated_at.isoformat() if row else None,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def get_meta(db: Session = Depends(get_db)):
    if IS_VERCEL:
        _init_db()
    return meta(db)


@app.get("/api/items")
def get_items(db: Session = Depends(get_db)):
    if IS_VERCEL:
        _init_db()
    return {"items": all_summaries(db), "meta": meta(db)}


@app.get("/api/suggested")
def suggested(db: Session = Depends(get_db)):
    if IS_VERCEL:
        _init_db()
    items = all_summaries(db)
    movers = sorted(
        [i for i in items if abs(i["pct_change_1w"]) > 0.5],
        key=lambda x: abs(x["pct_change_1w"]),
        reverse=True,
    )[:3]
    if not movers:
        movers = sorted(items, key=lambda x: abs(x["pct_change_1w"]), reverse=True)[:3]
    return {
        "chips": [
            {"item": m["item"], "verdict": m["verdict"], "pct": m["pct_change_1w"]}
            for m in movers
        ]
    }


@app.get("/api/items/{item_name}/history")
def history(item_name: str, db: Session = Depends(get_db)):
    if IS_VERCEL:
        _init_db()
    summary = item_summary(db, item_name)
    if not summary:
        raise HTTPException(404, "Item not found")
    return {"item": item_name, "history": summary["history"], "meta": meta(db)}


@app.post("/api/query")
def query(body: QueryRequest, db: Session = Depends(get_db)):
    if IS_VERCEL:
        _init_db()
    items = match_items(body.text)
    if not items:
        return {
            "matched_items": [],
            "answers": [],
            "message": "Mujhe samajh nahi aaya — flour, oil, sugar, ghee, daal, chawal, ya gas ke baare mein poochain.",
            "meta": meta(db),
        }
    return {
        "matched_items": items,
        "answers": [s for item in items if (s := item_summary(db, item))],
        "meta": meta(db),
    }


@app.post("/api/admin/refresh")
def admin_refresh(db: Session = Depends(get_db)):
    return refresh(db)


@app.post("/api/admin/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if IS_VERCEL:
        raise HTTPException(
            501,
            "Manual upload is not supported on Vercel — the filesystem is ephemeral. "
            "Use the /api/admin/refresh endpoint to pull the latest PBS data.",
        )

    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(400, "Please upload an .xlsx file")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            413,
            f"File too large — maximum {MAX_UPLOAD_MB} MB allowed.",
        )

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    target = HISTORY_DIR / f"manual-{datetime.now():%Y%m%d%H%M%S}.xlsx"
    target.write_bytes(contents)
    try:
        records = parse_annexure(target)
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(422, str(exc))

    for record in records:
        _upsert(db, record)
    record = records[0]
    state = db.get(DatasetMeta, 1) or DatasetMeta(id=1)
    state.source = "manual_upload"
    state.week_ending = record["week_ending"]
    state.updated_at = datetime.now(timezone.utc)
    db.merge(state)
    db.commit()
    return {"source": "manual_upload", "records": len(records), "meta": meta(db)}
