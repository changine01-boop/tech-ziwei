"""Unit tests for the /preview endpoint.

No database is required — the preview router calls only the chart engine.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tech_ziwei.routers.preview import router


# ---------------------------------------------------------------------------
# Shared test client
# ---------------------------------------------------------------------------

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_PAYLOAD = {
    "gregorian_date": "1990-05-15",
    "birth_time": "14:30:00",
    "is_male": True,
    "timezone_offset": -5.0,
}

_REQUIRED_FIELDS = {
    "ming_branch",
    "ming_palace_name",
    "ming_ganzhi",
    "main_stars",
    "wu_xing_ju",
    "wu_xing_ju_label",
    "year_ganzhi",
    "hook",
}


def post(payload: dict) -> "Response":  # type: ignore[name-defined]
    return client.post("/preview", json=payload)


# ---------------------------------------------------------------------------
# Tests: happy path
# ---------------------------------------------------------------------------

class TestPreviewHappyPath:
    def test_valid_birth_data_returns_200(self):
        resp = post(_VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_response_contains_all_required_fields(self):
        resp = post(_VALID_PAYLOAD)
        data = resp.json()
        for field in _REQUIRED_FIELDS:
            assert field in data, f"Missing field: {field}"

    def test_ming_branch_is_0_to_11(self):
        resp = post(_VALID_PAYLOAD)
        assert 0 <= resp.json()["ming_branch"] <= 11

    def test_wu_xing_ju_is_valid(self):
        resp = post(_VALID_PAYLOAD)
        assert resp.json()["wu_xing_ju"] in {2, 3, 4, 5, 6}

    def test_main_stars_is_a_list_of_strings(self):
        resp = post(_VALID_PAYLOAD)
        main_stars = resp.json()["main_stars"]
        assert isinstance(main_stars, list)
        for star in main_stars:
            assert isinstance(star, str)

    def test_hook_is_non_empty_string(self):
        resp = post(_VALID_PAYLOAD)
        hook = resp.json()["hook"]
        assert isinstance(hook, str)
        assert len(hook) > 0

    def test_ming_palace_name_is_non_empty_string(self):
        resp = post(_VALID_PAYLOAD)
        assert isinstance(resp.json()["ming_palace_name"], str)
        assert resp.json()["ming_palace_name"] != ""

    def test_ming_ganzhi_is_two_char_string(self):
        """Stem + branch should produce exactly two Chinese characters."""
        resp = post(_VALID_PAYLOAD)
        assert len(resp.json()["ming_ganzhi"]) == 2

    def test_year_ganzhi_is_two_char_string(self):
        resp = post(_VALID_PAYLOAD)
        assert len(resp.json()["year_ganzhi"]) == 2

    def test_wu_xing_ju_label_is_non_empty(self):
        resp = post(_VALID_PAYLOAD)
        assert resp.json()["wu_xing_ju_label"] != ""

    def test_default_timezone_offset_is_used_when_omitted(self):
        payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "timezone_offset"}
        resp = post(payload)
        assert resp.status_code == 200

    def test_female_chart_returns_200(self):
        payload = {**_VALID_PAYLOAD, "is_male": False}
        resp = post(payload)
        assert resp.status_code == 200

    def test_minimum_valid_timezone(self):
        payload = {**_VALID_PAYLOAD, "timezone_offset": -12.0}
        resp = post(payload)
        assert resp.status_code == 200

    def test_maximum_valid_timezone(self):
        payload = {**_VALID_PAYLOAD, "timezone_offset": 14.0}
        resp = post(payload)
        assert resp.status_code == 200

    def test_different_birth_dates_return_200(self):
        dates = ["1985-01-01", "2000-12-31", "1970-06-15", "1995-08-20"]
        for d in dates:
            payload = {**_VALID_PAYLOAD, "gregorian_date": d}
            resp = post(payload)
            assert resp.status_code == 200, f"Failed for date {d}: {resp.json()}"


# ---------------------------------------------------------------------------
# Tests: validation errors
# ---------------------------------------------------------------------------

class TestPreviewValidation:
    def test_invalid_date_returns_422(self):
        payload = {**_VALID_PAYLOAD, "gregorian_date": "not-a-date"}
        resp = post(payload)
        assert resp.status_code == 422

    def test_invalid_time_returns_422(self):
        payload = {**_VALID_PAYLOAD, "birth_time": "25:99:00"}
        resp = post(payload)
        assert resp.status_code == 422

    def test_missing_gregorian_date_returns_422(self):
        payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "gregorian_date"}
        resp = post(payload)
        assert resp.status_code == 422

    def test_missing_birth_time_returns_422(self):
        payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "birth_time"}
        resp = post(payload)
        assert resp.status_code == 422

    def test_missing_is_male_returns_422(self):
        payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "is_male"}
        resp = post(payload)
        assert resp.status_code == 422

    def test_timezone_offset_too_low_returns_422(self):
        payload = {**_VALID_PAYLOAD, "timezone_offset": -13.0}
        resp = post(payload)
        assert resp.status_code == 422

    def test_timezone_offset_too_high_returns_422(self):
        payload = {**_VALID_PAYLOAD, "timezone_offset": 15.0}
        resp = post(payload)
        assert resp.status_code == 422

    def test_empty_body_returns_422(self):
        resp = client.post("/preview", json={})
        assert resp.status_code == 422

    def test_completely_missing_body_returns_422(self):
        resp = client.post("/preview")
        assert resp.status_code == 422

    def test_wrong_type_for_is_male_returns_422(self):
        # Pydantic v2 coerces "yes"/"no" to bool; use a numeric value that
        # cannot be coerced to bool via the bool field (object type fails).
        payload = {**_VALID_PAYLOAD, "is_male": {"nested": "object"}}
        resp = post(payload)
        assert resp.status_code == 422
