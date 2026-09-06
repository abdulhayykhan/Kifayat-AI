"""Price trend and buy/wait recommendations for tracked Karachi items."""
from __future__ import annotations

import statistics
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import TARGET_ITEMS
from ..models import Price

WINDOW = 8


def _history(db: Session, item: str) -> list[dict]:
    rows = db.scalars(
        select(Price)
        .where(Price.item == item, Price.city == "Karachi")
        .order_by(Price.week_ending.desc())
        .limit(WINDOW)
    ).all()
    return [
        {"week_ending": row.week_ending.isoformat(), "price": row.price, "unit": row.unit}
        for row in reversed(rows)
    ]


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 2)


def _trend(prices: list[float]) -> str:
    if len(prices) < 2:
        return "flat"
    midpoint = len(prices) // 2
    early = statistics.mean(prices[:midpoint]) if midpoint else prices[0]
    late = statistics.mean(prices[midpoint:]) if midpoint < len(prices) else prices[-1]
    delta = late - early
    threshold = early * 0.005 if early else 0
    if delta > threshold:
        return "rising"
    if delta < -threshold:
        return "falling"
    return "flat"


def _volatility_score(changes: list[float]) -> float:
    if len(changes) < 2:
        return 0.0
    return round(statistics.pstdev(changes), 2)


def _verdict(pct_1w: float, trend: str) -> str:
    if pct_1w > 2 and trend == "rising":
        return "Buy now — price is climbing"
    if pct_1w < -2 and trend == "falling":
        return "Wait — price is dropping"
    return "Stable — no urgency either way"


def item_summary(db: Session, item: str) -> dict | None:
    history = _history(db, item)
    if not history:
        return None

    prices = [point["price"] for point in history]
    current = prices[-1]

    if len(prices) < 2:
        return {
            "item": item,
            "current_price": current,
            "unit": history[-1]["unit"],
            "pct_change_1w": 0.0,
            "direction": "flat",
            "volatility_score": 0.0,
            "verdict": "Insufficient data — need at least 2 weeks",
            "history": history,
        }

    pct_1w = _pct_change(current, prices[-2])
    weekly_changes = [_pct_change(prices[i], prices[i - 1]) for i in range(1, len(prices))]
    trend = _trend(prices)

    return {
        "item": item,
        "current_price": current,
        "unit": history[-1]["unit"],
        "pct_change_1w": pct_1w,
        "direction": trend,
        "volatility_score": _volatility_score(weekly_changes),
        "verdict": _verdict(pct_1w, trend),
        "history": history,
    }


def all_summaries(db: Session) -> list[dict]:
    return [summary for item in TARGET_ITEMS if (summary := item_summary(db, item))]
