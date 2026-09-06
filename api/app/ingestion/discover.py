from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from ..config import HISTORY_DIR, PBS_SPI_FALLBACK_URLS, PBS_SPI_URL


def _weekly_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [
        urljoin(base_url, anchor["href"])
        for anchor in soup.find_all("a", href=True)
        if "weekly-sensitive-price-indicator" in anchor["href"] and "week-ended" in anchor["href"]
    ]


def discover_latest() -> tuple[str, str, datetime.date]:
    candidates: list[str] = []
    for landing in (PBS_SPI_URL, *PBS_SPI_FALLBACK_URLS):
        response = requests.get(landing, timeout=15, headers={"User-Agent": "KifayatAI/1.0"})
        response.raise_for_status()
        candidates.extend(_weekly_links(response.text, landing))
        if "weekly-sensitive-price-indicator" in landing and "week-ended" in landing:
            candidates.append(landing)
    if not candidates:
        raise RuntimeError("PBS latest weekly release link not found")
    weekly = candidates[0]
    page = requests.get(weekly, timeout=15, headers={"User-Agent": "KifayatAI/1.0"})
    page.raise_for_status()
    detail = BeautifulSoup(page.text, "html.parser")
    annexure = next(
        (
            a.get("href")
            for a in detail.find_all("a", href=True)
            if "annexure" in a.get_text(" ", strip=True).lower() and a["href"].lower().endswith(".xlsx")
        ),
        None,
    )
    if not annexure:
        raise RuntimeError("PBS Annexure Excel link not found")
    report = next(
        (
            a.get("href")
            for a in detail.find_all("a", href=True)
            if "report" in a.get_text(" ", strip=True).lower() and a["href"].lower().endswith(".xlsx")
        ),
        None,
    )
    match = re.search(r"(\d{2}-\d{2}-\d{4})", page.text)
    if not match:
        raise RuntimeError("PBS week-ending date not found")
    week = datetime.strptime(match.group(1), "%d-%m-%Y").date()
    return urljoin(weekly, annexure), urljoin(weekly, report) if report else "", week

def download_latest() -> Path:
    url, _, week = discover_latest()
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    target = HISTORY_DIR / f"{week.isoformat()}.xlsx"
    payload = requests.get(url, timeout=30, headers={"User-Agent": "KifayatAI/1.0"})
    payload.raise_for_status()
    target.write_bytes(payload.content)
    return target
