from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import FALLBACK_FILE, TARGET_ITEMS
from app.ingestion.parse_excel import parse_annexure
from app.nlu.roman_urdu import match_items


@pytest.mark.skipif(not FALLBACK_FILE.exists(), reason="fallback workbook not bundled")
def test_parse_annexure_returns_karachi_rows():
    records = parse_annexure(FALLBACK_FILE)
    assert records
    assert {field for field in records[0]} == {"week_ending", "item", "city", "unit", "price"}
    assert all(record["city"] == "Karachi" for record in records)
    assert all(record["item"] in TARGET_ITEMS for record in records)


def test_roman_urdu_matches_common_queries():
    assert "Cooking Oil" in match_items("oil sasta hoga?")
    assert "Rice Basmati Broken" in match_items("chawal ka rate?")
    assert "Sugar" in match_items("cheeni mehngi hogi?")
    assert "Wheat Flour" in match_items("atta ka trend?")
    assert match_items("random gibberish xyz") == []


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_meta(client):
    r = client.get("/api/meta")
    assert r.status_code == 200
    data = r.json()
    assert "source" in data
    assert data["source"] in ("live", "fallback_cached", "manual_upload")


def test_items(client):
    r = client.get("/api/items")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "meta" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    item = data["items"][0]
    assert "item" in item
    assert "current_price" in item
    assert "pct_change_1w" in item
    assert "direction" in item
    assert "verdict" in item
    assert "history" in item
    assert "pct_change_4w" not in item


def test_items_history(client):
    r = client.get("/api/items/Wheat Flour/history")
    assert r.status_code == 200
    data = r.json()
    assert data["item"] == "Wheat Flour"
    assert "history" in data
    assert isinstance(data["history"], list)


def test_items_history_not_found(client):
    r = client.get("/api/items/Nonexistent Item/history")
    assert r.status_code == 404


def test_suggested(client):
    r = client.get("/api/suggested")
    assert r.status_code == 200
    data = r.json()
    assert "chips" in data
    assert isinstance(data["chips"], list)
    assert len(data["chips"]) <= 3
    if data["chips"]:
        chip = data["chips"][0]
        assert "item" in chip
        assert "verdict" in chip
        assert "pct" in chip


def test_query_valid(client):
    r = client.post("/api/query", json={"text": "oil ka rate?"})
    assert r.status_code == 200
    data = r.json()
    assert "matched_items" in data
    assert "answers" in data
    assert "meta" in data
    if data["matched_items"]:
        assert "Cooking Oil" in data["matched_items"]


def test_query_no_match(client):
    r = client.post("/api/query", json={"text": "random gibberish"})
    assert r.status_code == 200
    data = r.json()
    assert data["matched_items"] == []
    assert data["answers"] == []
    assert "message" in data


def test_query_empty_text_rejected(client):
    r = client.post("/api/query", json={"text": ""})
    assert r.status_code == 422


def test_query_missing_text_rejected(client):
    r = client.post("/api/query", json={})
    assert r.status_code == 422


def test_query_text_too_long_rejected(client):
    r = client.post("/api/query", json={"text": "a" * 501})
    assert r.status_code == 422


def test_upload_rejects_non_xlsx(client):
    r = client.post(
        "/api/admin/upload",
        files={"file": ("test.txt", b"not an excel file", "text/plain")},
    )
    assert r.status_code == 400


def test_cors_headers(client):
    r = client.options(
        "/api/health",
        headers={
            "Origin": "http://127.0.0.1:8000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 200
    assert "access-control-allow-origin" in r.headers
