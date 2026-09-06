from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from ..config import HISTORY_DIR, PBS_SPI_FALLBACK_URLS, PBS_SPI_URL


def _find_annexure_link(soup: BeautifulSoup, base_url: str) -> str | None:
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        href = a["href"]
        if "annexure" in text and href.lower().endswith(".xlsx"):
            return urljoin(base_url, href)
    return None


def _find_report_link(soup: BeautifulSoup, base_url: str) -> str | None:
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        href = a["href"]
        if "spi" in text and "report" in text and href.lower().endswith(".xlsx"):
            return urljoin(base_url, href)
    return None


def _find_week_date(soup: BeautifulSoup) -> datetime.date | None:
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        match = re.search(r"(\d{2})-(\d{2})-(\d{4})", text)
        if match:
            return datetime.strptime(match.group(0), "%d-%m-%Y").date()
    blob = " ".join(str(x) for x in soup.stripped_strings)
    match = re.search(r"week\s+ended\s+(\d{2}-\d{2}-\d{4})", blob, re.IGNORECASE)
    if match:
        return datetime.strptime(match.group(1), "%d-%m-%Y").date()
    match = re.search(r"(\d{2})-(\d{2})-(\d{4})", blob)
    if match:
        return datetime.strptime(match.group(0), "%d-%m-%Y").date()
    return None


def discover_latest() -> tuple[str, str, datetime.date]:
    response = requests.get(PBS_SPI_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    annexure = _find_annexure_link(soup, PBS_SPI_URL)
    report = _find_report_link(soup, PBS_SPI_URL)
    week = _find_week_date(soup)

    if not annexure:
        raise RuntimeError("PBS Annexure Excel link not found on landing page")
    if not week:
        raise RuntimeError("PBS week-ending date not found on landing page")

    return annexure, report or "", week


def download_latest() -> Path:
    url, _, week = discover_latest()
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    target = HISTORY_DIR / f"{week.isoformat()}.xlsx"
    payload = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    payload.raise_for_status()
    target.write_bytes(payload.content)
    return target
