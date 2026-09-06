from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select

from ..config import FALLBACK_FILE, HISTORY_DIR
from ..models import DatasetMeta, Price
from .parse_excel import parse_annexure


def _upsert(db, record: dict) -> None:
    existing = db.scalar(
        select(Price).where(
            Price.week_ending == record["week_ending"],
            Price.item == record["item"],
            Price.city == record["city"],
        )
    )
    if existing:
        existing.unit, existing.price = record["unit"], record["price"]
    else:
        db.add(Price(**record))
        db.flush()


def _load_workbook(db, path: Path) -> int:
    count = 0
    for record in parse_annexure(path):
        _upsert(db, record)
        count += 1
    return count


def _history_files() -> list[Path]:
    if not HISTORY_DIR.exists():
        return []
    return sorted(HISTORY_DIR.glob("*.xlsx"), key=lambda path: path.stat().st_mtime)


def seed_fallback(db) -> int:
    if not FALLBACK_FILE.exists():
        raise FileNotFoundError(f"Fallback workbook missing: {FALLBACK_FILE}")

    loaded = 0
    seen: set[Path] = set()
    for path in [*_history_files(), FALLBACK_FILE]:
        if path in seen:
            continue
        seen.add(path)
        try:
            loaded += _load_workbook(db, path)
        except Exception:
            continue

    if db.scalar(select(func.count(Price.id))) == 0:
        raise RuntimeError(
            "No price data loaded — history files and fallback workbook "
            f"did not yield any records. Check {HISTORY_DIR} and {FALLBACK_FILE}"
        )

    latest_week = db.scalar(select(func.max(Price.week_ending)))
    meta = db.get(DatasetMeta, 1) or DatasetMeta(id=1)
    meta.source = "fallback_cached"
    meta.week_ending = latest_week
    meta.updated_at = datetime.now(UTC)
    db.merge(meta)
    db.commit()
    return db.scalar(select(func.count(Price.id))) or 0
