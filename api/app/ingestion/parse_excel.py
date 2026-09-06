"""Normalize PBS Appendix-A workbooks into Karachi price records.

Verified against Annex_03.09.2026.xlsx: Appendix-A has multiple horizontal
blocks. Each has a city-name row (e.g. ``Karachi (10)``), then DESCRIPTION,
UNIT and MIN/AVG/MAX headings. The Karachi AVG sits one column to the right of
the city heading. This parser finds that block dynamically.
"""
from __future__ import annotations
import re
from datetime import datetime, date
from pathlib import Path
import pandas as pd
from ..config import CITY, TARGET_ITEMS

def _canonical_item(label: object) -> str | None:
    text = str(label).lower().replace("/", " ")
    checks = {
        "Wheat Flour": ("wheat flour", "flour bag"), "Sugar": ("sugar",),
        "Cooking Oil": ("cooking oil",), "Vegetable Ghee": ("vegetable ghee",),
        "Pulses Moong": ("pulse moong", "gram pulse", "moong"), "Pulses Mash": ("pulse mash", "mash"),
        "Pulses Gram": ("pulse gram", "gram whole", "gram pulse"),
        "Rice Basmati Broken": ("rice basmati broken",), "Rice IRRI-6": ("rice irri",),
        "Milk Fresh": ("milk fresh", "milk (fresh"), "LPG (Cylinder)": ("lpg", "gas cylinder"),
        "Onions": ("onion",), "Tomatoes": ("tomato",),
    }
    for canonical, needles in checks.items():
        if any(needle in text for needle in needles):
            return canonical
    return None

def _workbook_date(frame: pd.DataFrame, path: Path) -> date:
    blob = " ".join(str(x) for x in frame.fillna("").to_numpy().ravel()[:600]) + " " + path.name
    match = re.search(r"(\d{2})[-.](\d{2})[-.](\d{4})", blob)
    if not match:
        raise ValueError("Could not find week-ending date in workbook")
    return datetime.strptime(match.group(0).replace(".", "-"), "%d-%m-%Y").date()

def parse_annexure(path: str | Path) -> list[dict]:
    path = Path(path)
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    appendix = next((df for name, df in sheets.items() if "appendix-a" in name.lower()), None)
    if appendix is None:
        raise ValueError("No Appendix-A sheet found in PBS workbook")
    week_ending = _workbook_date(appendix, path)
    records: dict[str, dict] = {}
    found_karachi = False
    for header_row, row in appendix.iterrows():
        if found_karachi:
            break
        for city_col, cell in row.items():
            if CITY.lower() not in str(cell).lower():
                continue
            labels = appendix.iloc[header_row + 1] if header_row + 1 < len(appendix) else pd.Series()
            description_col = next((i for i, value in labels.items() if "description" in str(value).lower()), 1)
            unit_col = next((i for i, value in labels.items() if "unit" in str(value).lower()), 2)
            avg_col = city_col + 1
            for _, data in appendix.iloc[header_row + 4:].iterrows():
                item = _canonical_item(data.iloc[description_col])
                if not item or item not in TARGET_ITEMS:
                    continue
                price = pd.to_numeric(data.iloc[avg_col], errors="coerce")
                if pd.notna(price) and float(price) > 0:
                    records[item] = {"week_ending": week_ending, "item": item, "city": CITY,
                                     "unit": str(data.iloc[unit_col]).strip(), "price": round(float(price), 2)}
            found_karachi = True
            break
    if not records:
        raise ValueError("Karachi city block or supported item prices were not found")
    return list(records.values())
