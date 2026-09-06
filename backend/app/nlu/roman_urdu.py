"""Rule-based Roman Urdu / English keyword matcher — no LLM required."""
from __future__ import annotations

import re

from ..config import TARGET_ITEMS

ITEM_ALIASES: dict[str, str] = {
    "chawal": "Rice Basmati Broken",
    "rice": "Rice Basmati Broken",
    "basmati": "Rice Basmati Broken",
    "irri": "Rice IRRI-6",
    "tail": "Cooking Oil",
    "tel": "Cooking Oil",
    "oil": "Cooking Oil",
    "ghee": "Vegetable Ghee",
    "cheeni": "Sugar",
    "sugar": "Sugar",
    "shakkar": "Sugar",
    "atta": "Wheat Flour",
    "aata": "Wheat Flour",
    "flour": "Wheat Flour",
    "daal": "Pulses Moong",
    "dal": "Pulses Moong",
    "moong": "Pulses Moong",
    "mash": "Pulses Mash",
    "gram": "Pulses Gram",
    "chana": "Pulses Gram",
    "gas": "LPG (Cylinder)",
    "cylinder": "LPG (Cylinder)",
    "lpg": "LPG (Cylinder)",
    "doodh": "Milk Fresh",
    "milk": "Milk Fresh",
    "pyaz": "Onions",
    "onion": "Onions",
    "onions": "Onions",
    "tamatar": "Tomatoes",
    "tomato": "Tomatoes",
    "tomatoes": "Tomatoes",
}


def match_items(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    matched: list[str] = []
    for token in tokens:
        item = ITEM_ALIASES.get(token)
        if item and item in TARGET_ITEMS and item not in matched:
            matched.append(item)
    return matched
