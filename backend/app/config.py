import os
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
_backend = _root / "backend"

DATA_DIR = _backend / "data"
HISTORY_DIR = DATA_DIR / "history"
FALLBACK_FILE = DATA_DIR / "fallback_sample.xlsx"
DB_PATH = _backend / "kifayat.db"

PBS_SPI_URL = "https://www.pbs.gov.pk/price-statistics/"
PBS_SPI_FALLBACK_URLS = [
    "https://www.pbs.gov.pk/spi",
]

CITY = "Karachi"

CORS_ORIGINS = os.getenv(
    "KIFAYAT_CORS_ORIGINS",
    "*",
).split(",")

MAX_UPLOAD_MB = int(os.getenv("KIFAYAT_MAX_UPLOAD_MB", "10"))

TARGET_ITEMS = [
    "Wheat Flour", "Sugar", "Cooking Oil", "Vegetable Ghee",
    "Pulses Moong", "Pulses Mash", "Pulses Gram", "Rice Basmati Broken",
    "Rice IRRI-6", "Milk Fresh", "LPG (Cylinder)", "Onions", "Tomatoes",
]

IS_VERCEL = os.getenv("VERCEL", "").lower() in ("1", "true", "yes")

# PBS Appendix-A uses DESCRIPTION (column 2), UNIT (column 3), and
# repeated three-column city blocks. Karachi appears as "Karachi (10)"; its AVG
# price is the next column. The parser searches these labels instead of relying
# on their fixed row/column position.
