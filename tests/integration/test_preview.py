"""Integration tests for the public /preview endpoint (no auth required)."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PREVIEW_BODY = {
    "gregorian_date": "1990-05-15",
    "birth_time": "12:00:00",
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

_VALID_WU_XING_JU = {2, 3, 4, 5, 6}


# ---------------------------------------------------------------------------
# POST /preview — happy-path and response shape
# ---------------------------------------------------------------------------


async def test_preview_valid_body_returns_200(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200


async def test_preview_response_contains_all_required_fields(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    for field in _REQUIRED_FIELDS:
        assert field in body, f"Missing field: {field}"


async def test_preview_ming_branch_is_integer_in_valid_range(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["ming_branch"], int)
    assert 0 <= body["ming_branch"] <= 11


async def test_preview_wu_xing_ju_is_valid_value(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert body["wu_xing_ju"] in _VALID_WU_XING_JU


async def test_preview_wu_xing_ju_label_matches_wu_xing_ju(client: AsyncClient) -> None:
    labels = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    expected_label = labels.get(body["wu_xing_ju"], "")
    assert body["wu_xing_ju_label"] == expected_label


async def test_preview_main_stars_is_list(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["main_stars"], list)


async def test_preview_ming_ganzhi_is_non_empty_string(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["ming_ganzhi"], str)
    assert len(body["ming_ganzhi"]) >= 2


async def test_preview_year_ganzhi_is_non_empty_string(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["year_ganzhi"], str)
    assert len(body["year_ganzhi"]) >= 2


async def test_preview_hook_is_non_empty_string(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["hook"], str)
    assert len(body["hook"]) > 0


async def test_preview_ming_palace_name_is_string(client: AsyncClient) -> None:
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["ming_palace_name"], str)
    assert len(body["ming_palace_name"]) > 0


# ---------------------------------------------------------------------------
# POST /preview — no auth required
# ---------------------------------------------------------------------------


async def test_preview_does_not_require_auth_header(client: AsyncClient) -> None:
    """Verify no Authorization header is needed — the endpoint is public."""
    resp = await client.post("/preview", json=VALID_PREVIEW_BODY)
    assert resp.status_code == 200


async def test_preview_ignores_auth_header_gracefully(client: AsyncClient) -> None:
    """Even if a Bearer token is supplied, the endpoint accepts it without error."""
    resp = await client.post(
        "/preview",
        json=VALID_PREVIEW_BODY,
        headers={"Authorization": "Bearer fake.token.value"},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /preview — various birth dates produce valid results
# ---------------------------------------------------------------------------


async def test_preview_different_birth_date_male(client: AsyncClient) -> None:
    body = {
        "gregorian_date": "1975-03-01",
        "birth_time": "08:00:00",
        "is_male": True,
        "timezone_offset": 8.0,
    }
    resp = await client.post("/preview", json=body)
    assert resp.status_code == 200
    result = resp.json()
    for field in _REQUIRED_FIELDS:
        assert field in result
    assert result["wu_xing_ju"] in _VALID_WU_XING_JU


async def test_preview_different_birth_date_female(client: AsyncClient) -> None:
    body = {
        "gregorian_date": "1985-11-30",
        "birth_time": "23:45:00",
        "is_male": False,
        "timezone_offset": -8.0,
    }
    resp = await client.post("/preview", json=body)
    assert resp.status_code == 200
    result = resp.json()
    for field in _REQUIRED_FIELDS:
        assert field in result


async def test_preview_early_morning_birth(client: AsyncClient) -> None:
    body = {
        "gregorian_date": "2000-01-01",
        "birth_time": "00:30:00",
        "is_male": True,
        "timezone_offset": 0.0,
    }
    resp = await client.post("/preview", json=body)
    assert resp.status_code == 200
    for field in _REQUIRED_FIELDS:
        assert field in resp.json()


async def test_preview_default_timezone_offset(client: AsyncClient) -> None:
    """timezone_offset should be optional with a default."""
    body = {
        "gregorian_date": "1995-07-04",
        "birth_time": "14:00:00",
        "is_male": False,
    }
    resp = await client.post("/preview", json=body)
    assert resp.status_code == 200
    for field in _REQUIRED_FIELDS:
        assert field in resp.json()


async def test_preview_two_different_births_produce_different_or_equal_results(
    client: AsyncClient,
) -> None:
    """Two different birth dates should each produce a valid, structurally correct response."""
    body_a = {
        "gregorian_date": "1980-02-14",
        "birth_time": "10:00:00",
        "is_male": True,
        "timezone_offset": -5.0,
    }
    body_b = {
        "gregorian_date": "1992-09-09",
        "birth_time": "16:00:00",
        "is_male": False,
        "timezone_offset": 5.5,
    }
    resp_a = await client.post("/preview", json=body_a)
    resp_b = await client.post("/preview", json=body_b)
    assert resp_a.status_code == 200
    assert resp_b.status_code == 200
    for field in _REQUIRED_FIELDS:
        assert field in resp_a.json()
        assert field in resp_b.json()


# ---------------------------------------------------------------------------
# POST /preview — validation errors
# ---------------------------------------------------------------------------


async def test_preview_invalid_date_format_returns_422(client: AsyncClient) -> None:
    bad_body = {**VALID_PREVIEW_BODY, "gregorian_date": "15-05-1990"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_invalid_date_string_returns_422(client: AsyncClient) -> None:
    bad_body = {**VALID_PREVIEW_BODY, "gregorian_date": "not-a-date"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_invalid_time_format_returns_422(client: AsyncClient) -> None:
    bad_body = {**VALID_PREVIEW_BODY, "birth_time": "99:99:99"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_timezone_too_low_returns_422(client: AsyncClient) -> None:
    bad_body = {**VALID_PREVIEW_BODY, "timezone_offset": -13.0}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_timezone_too_high_returns_422(client: AsyncClient) -> None:
    bad_body = {**VALID_PREVIEW_BODY, "timezone_offset": 15.0}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_missing_gregorian_date_returns_422(client: AsyncClient) -> None:
    bad_body = {k: v for k, v in VALID_PREVIEW_BODY.items() if k != "gregorian_date"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_missing_birth_time_returns_422(client: AsyncClient) -> None:
    bad_body = {k: v for k, v in VALID_PREVIEW_BODY.items() if k != "birth_time"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_missing_is_male_returns_422(client: AsyncClient) -> None:
    bad_body = {k: v for k, v in VALID_PREVIEW_BODY.items() if k != "is_male"}
    resp = await client.post("/preview", json=bad_body)
    assert resp.status_code == 422


async def test_preview_empty_body_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/preview", json={})
    assert resp.status_code == 422
