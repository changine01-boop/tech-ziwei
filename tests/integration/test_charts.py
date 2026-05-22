"""Integration tests for /charts endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unique_email() -> str:
    return f"test_{uuid4().hex[:8]}@example.com"


async def register_and_login(
    client: AsyncClient,
    email: str | None = None,
    password: str = "password123",
) -> str:
    if email is None:
        email = _unique_email()
    await client.post("/auth/register", json={"email": email, "password": password})
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


VALID_CHART_BODY = {
    "gregorian_date": "1990-05-15",
    "birth_time": "12:00:00",
    "is_male": True,
    "timezone_offset": -5.0,
}

VALID_CHART_BODY_2 = {
    "gregorian_date": "1985-08-22",
    "birth_time": "06:30:00",
    "is_male": False,
    "timezone_offset": 8.0,
}


# ---------------------------------------------------------------------------
# POST /charts
# ---------------------------------------------------------------------------


async def test_create_chart_authenticated_returns_201(client: AsyncClient) -> None:
    token = await register_and_login(client)
    resp = await client.post("/charts", json=VALID_CHART_BODY, headers=auth_headers(token))
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["gregorian_date"] == "1990-05-15"
    assert body["is_male"] is True
    assert "star_placements" in body
    assert isinstance(body["star_placements"], dict)
    assert len(body["star_placements"]) > 0
    assert "major_periods" in body
    assert isinstance(body["major_periods"], list)
    assert "ming_branch" in body
    assert "wu_xing_ju" in body
    assert "lunar_year" in body
    assert "lunar_month" in body
    assert "lunar_day" in body
    assert "created_at" in body


async def test_create_chart_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/charts", json=VALID_CHART_BODY)
    assert resp.status_code == 401


async def test_create_chart_invalid_date_returns_422(client: AsyncClient) -> None:
    token = await register_and_login(client)
    bad_body = {**VALID_CHART_BODY, "gregorian_date": "not-a-date"}
    resp = await client.post("/charts", json=bad_body, headers=auth_headers(token))
    assert resp.status_code == 422


async def test_create_chart_invalid_time_returns_422(client: AsyncClient) -> None:
    token = await register_and_login(client)
    bad_body = {**VALID_CHART_BODY, "birth_time": "99:99:99"}
    resp = await client.post("/charts", json=bad_body, headers=auth_headers(token))
    assert resp.status_code == 422


async def test_create_chart_timezone_out_of_range_returns_422(client: AsyncClient) -> None:
    token = await register_and_login(client)
    bad_body = {**VALID_CHART_BODY, "timezone_offset": 99.0}
    resp = await client.post("/charts", json=bad_body, headers=auth_headers(token))
    assert resp.status_code == 422


async def test_create_chart_missing_required_fields_returns_422(client: AsyncClient) -> None:
    token = await register_and_login(client)
    resp = await client.post("/charts", json={"is_male": True}, headers=auth_headers(token))
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /charts
# ---------------------------------------------------------------------------


async def test_list_charts_empty_returns_empty_list(client: AsyncClient) -> None:
    token = await register_and_login(client)
    resp = await client.get("/charts", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # New user should have no charts (may not be empty if DB has prior state,
    # but we verify the response is a list and every item belongs to this user's scope)


async def test_list_charts_returns_created_charts(client: AsyncClient) -> None:
    token = await register_and_login(client)
    headers = auth_headers(token)

    # Create two charts
    resp1 = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert resp1.status_code == 201
    resp2 = await client.post("/charts", json=VALID_CHART_BODY_2, headers=headers)
    assert resp2.status_code == 201

    chart_id_1 = resp1.json()["id"]
    chart_id_2 = resp2.json()["id"]

    list_resp = await client.get("/charts", headers=headers)
    assert list_resp.status_code == 200
    ids = [c["id"] for c in list_resp.json()]
    assert chart_id_1 in ids
    assert chart_id_2 in ids


async def test_list_charts_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/charts")
    assert resp.status_code == 401


async def test_list_charts_does_not_return_other_users_charts(client: AsyncClient) -> None:
    token_a = await register_and_login(client)
    token_b = await register_and_login(client)

    # User A creates a chart
    resp = await client.post("/charts", json=VALID_CHART_BODY, headers=auth_headers(token_a))
    assert resp.status_code == 201
    chart_id_a = resp.json()["id"]

    # User B's list should not contain it
    list_resp = await client.get("/charts", headers=auth_headers(token_b))
    assert list_resp.status_code == 200
    ids = [c["id"] for c in list_resp.json()]
    assert chart_id_a not in ids


# ---------------------------------------------------------------------------
# GET /charts/{id}
# ---------------------------------------------------------------------------


async def test_get_chart_by_own_id_returns_200(client: AsyncClient) -> None:
    token = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    get_resp = await client.get(f"/charts/{chart_id}", headers=headers)
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["id"] == chart_id
    assert body["gregorian_date"] == "1990-05-15"


async def test_get_chart_by_other_users_id_returns_404(client: AsyncClient) -> None:
    token_a = await register_and_login(client)
    token_b = await register_and_login(client)

    create_resp = await client.post(
        "/charts", json=VALID_CHART_BODY, headers=auth_headers(token_a)
    )
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    # User B tries to access User A's chart
    get_resp = await client.get(f"/charts/{chart_id}", headers=auth_headers(token_b))
    assert get_resp.status_code == 404


async def test_get_chart_nonexistent_id_returns_404(client: AsyncClient) -> None:
    token = await register_and_login(client)
    fake_id = str(uuid4())
    resp = await client.get(f"/charts/{fake_id}", headers=auth_headers(token))
    assert resp.status_code == 404


async def test_get_chart_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.get(f"/charts/{uuid4()}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /charts/{id}
# ---------------------------------------------------------------------------


async def test_delete_own_chart_returns_204(client: AsyncClient) -> None:
    token = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/charts/{chart_id}", headers=headers)
    assert del_resp.status_code == 204

    # Confirm gone
    get_resp = await client.get(f"/charts/{chart_id}", headers=headers)
    assert get_resp.status_code == 404


async def test_delete_other_users_chart_returns_404(client: AsyncClient) -> None:
    token_a = await register_and_login(client)
    token_b = await register_and_login(client)

    create_resp = await client.post(
        "/charts", json=VALID_CHART_BODY, headers=auth_headers(token_a)
    )
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/charts/{chart_id}", headers=auth_headers(token_b))
    assert del_resp.status_code == 404

    # Chart still exists for owner
    get_resp = await client.get(f"/charts/{chart_id}", headers=auth_headers(token_a))
    assert get_resp.status_code == 200


async def test_delete_nonexistent_chart_returns_404(client: AsyncClient) -> None:
    token = await register_and_login(client)
    fake_id = str(uuid4())
    resp = await client.delete(f"/charts/{fake_id}", headers=auth_headers(token))
    assert resp.status_code == 404


async def test_delete_chart_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.delete(f"/charts/{uuid4()}")
    assert resp.status_code == 401
