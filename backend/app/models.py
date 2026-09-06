from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint("week_ending", "item", "city", name="uq_price_week_item_city"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_ending: Mapped[date] = mapped_column(Date, index=True)
    item: Mapped[str] = mapped_column(String, index=True)
    city: Mapped[str] = mapped_column(String, index=True)
    unit: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)

class DatasetMeta(Base):
    __tablename__ = "dataset_meta"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String, default="fallback_cached")
    week_ending: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
