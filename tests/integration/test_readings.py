"""Integration tests for reading-related endpoints on /charts/{id}/readings and /charts/{id}/report."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tech_ziwei.models.user import SubscriptionTier, User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEST_DB_URL = "postgresql+asyncpg://test:test@localhost/tech_ziwei_test"


def _unique_email() -> str:
    return f"test_{uuid4().hex[:8]}@example.com"


async def register_and_login(
    client: AsyncClient,
    email: str | None = None,
    password: str = "password123",
) -> tuple[str, str]:
    """Returns (token, email)."""
    if email is None:
        email = _unique_email()
    reg_resp = await client.post("/auth/register", json={"email": email, "password": password})
    assert reg_resp.status_code == 201, reg_resp.text
    user_id: str = reg_resp.json()["id"]
    login_resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, login_resp.text
    return login_resp.json()["access_token"], user_id


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


VALID_CHART_BODY = {
    "gregorian_date": "1990-05-15",
    "birth_time": "12:00:00",
    "is_male": True,
    "timezone_offset": -5.0,
}


async def _upgrade_user_to_basic(user_id: str) -> None:
    """Directly update the user's subscription_tier in the test DB."""
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(subscription_tier=SubscriptionTier.BASIC)
        )
        await session.commit()
    await engine.dispose()


# ---------------------------------------------------------------------------
# GET /charts/{id}/readings/{type}
# ---------------------------------------------------------------------------


async def test_get_reading_nonexistent_returns_404(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    resp = await client.get(f"/charts/{chart_id}/readings/core", headers=headers)
    assert resp.status_code == 404


async def test_get_reading_all_types_nonexistent_returns_404(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    for reading_type in ("core", "relationship", "career", "annual"):
        resp = await client.get(f"/charts/{chart_id}/readings/{reading_type}", headers=headers)
        assert resp.status_code == 404, f"Expected 404 for {reading_type}, got {resp.status_code}"


async def test_get_reading_invalid_type_returns_422(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    resp = await client.get(f"/charts/{chart_id}/readings/bogus_type", headers=headers)
    assert resp.status_code == 422


async def test_get_reading_verifies_chart_ownership(client: AsyncClient) -> None:
    token_a, _uid_a = await register_and_login(client)
    token_b, _uid_b = await register_and_login(client)

    # User A creates a chart
    create_resp = await client.post(
        "/charts", json=VALID_CHART_BODY, headers=auth_headers(token_a)
    )
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    # User B should get 404 (chart not found for them), not 404 reading-specific
    resp = await client.get(f"/charts/{chart_id}/readings/core", headers=auth_headers(token_b))
    assert resp.status_code == 404


async def test_get_reading_nonexistent_chart_returns_404(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    fake_chart_id = str(uuid4())
    resp = await client.get(
        f"/charts/{fake_chart_id}/readings/core", headers=auth_headers(token)
    )
    assert resp.status_code == 404


async def test_get_reading_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.get(f"/charts/{uuid4()}/readings/core")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /charts/{id}/report  (paywall enforcement)
# ---------------------------------------------------------------------------


async def test_request_report_free_user_returns_402(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    resp = await client.post(f"/charts/{chart_id}/report", headers=headers)
    assert resp.status_code == 402


async def test_request_report_free_user_detail_is_payment_required(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    resp = await client.post(f"/charts/{chart_id}/report", headers=headers)
    assert resp.status_code == 402
    assert resp.json()["detail"] == "payment_required"


async def test_request_report_free_user_all_reading_types_are_blocked(
    client: AsyncClient,
) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    for rt in ("core", "relationship", "career", "annual"):
        resp = await client.post(
            f"/charts/{chart_id}/report?reading_type={rt}", headers=headers
        )
        assert resp.status_code == 402, f"Expected 402 for reading_type={rt}"


async def test_request_report_nonexistent_chart_free_user_returns_402(
    client: AsyncClient,
) -> None:
    # Free user paywall is checked before chart lookup — should still be 402
    token, _uid = await register_and_login(client)
    fake_id = str(uuid4())
    resp = await client.post(f"/charts/{fake_id}/report", headers=auth_headers(token))
    assert resp.status_code == 402


async def test_request_report_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.post(f"/charts/{uuid4()}/report")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Paywall lifted: BASIC user can trigger a report
# ---------------------------------------------------------------------------


async def test_request_report_basic_user_nonexistent_chart_returns_404(
    client: AsyncClient,
) -> None:
    token, user_id = await register_and_login(client)
    await _upgrade_user_to_basic(user_id)

    fake_id = str(uuid4())
    resp = await client.post(f"/charts/{fake_id}/report", headers=auth_headers(token))
    assert resp.status_code == 404


async def test_request_report_basic_user_own_chart_returns_202(client: AsyncClient) -> None:
    token, user_id = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    await _upgrade_user_to_basic(user_id)

    resp = await client.post(f"/charts/{chart_id}/report", headers=headers)
    assert resp.status_code == 202
    body = resp.json()
    assert body["chart_id"] == chart_id
    assert body["reading_type"] == "core"
    assert body["status"] in ("pending", "generating", "complete", "failed")
    assert "id" in body


async def test_request_report_basic_user_other_users_chart_returns_404(
    client: AsyncClient,
) -> None:
    token_a, uid_a = await register_and_login(client)
    token_b, uid_b = await register_and_login(client)

    # User A creates a chart
    create_resp = await client.post(
        "/charts", json=VALID_CHART_BODY, headers=auth_headers(token_a)
    )
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    # Upgrade user B to basic
    await _upgrade_user_to_basic(uid_b)

    # User B tries to generate a report on User A's chart
    resp = await client.post(f"/charts/{chart_id}/report", headers=auth_headers(token_b))
    assert resp.status_code == 404


async def test_get_reading_after_report_creation_returns_200(client: AsyncClient) -> None:
    token, user_id = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    await _upgrade_user_to_basic(user_id)

    # Trigger report generation
    report_resp = await client.post(f"/charts/{chart_id}/report", headers=headers)
    assert report_resp.status_code == 202

    # Reading record now exists — GET should return 200
    get_resp = await client.get(f"/charts/{chart_id}/readings/core", headers=headers)
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["chart_id"] == chart_id
    assert body["reading_type"] == "core"


# ---------------------------------------------------------------------------
# GET /charts/{id}/pdf  (paywall enforcement)
# ---------------------------------------------------------------------------


async def test_download_pdf_free_user_returns_402(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    create_resp = await client.post("/charts", json=VALID_CHART_BODY, headers=headers)
    assert create_resp.status_code == 201
    chart_id = create_resp.json()["id"]

    resp = await client.get(f"/charts/{chart_id}/pdf", headers=headers)
    assert resp.status_code == 402


async def test_download_pdf_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.get(f"/charts/{uuid4()}/pdf")
    assert resp.status_code == 401
