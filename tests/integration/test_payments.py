"""Integration tests for /payments endpoints."""

import json
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import update
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
    """Returns (token, user_id)."""
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


async def _set_subscription_tier(user_id: str, tier: SubscriptionTier) -> None:
    """Directly update a user's subscription tier in the test database."""
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(subscription_tier=tier)
        )
        await session.commit()
    await engine.dispose()


# ---------------------------------------------------------------------------
# POST /payments/checkout-session
# ---------------------------------------------------------------------------


async def test_checkout_session_free_user_returns_200_with_url(client: AsyncClient) -> None:
    token, _uid = await register_and_login(client)
    resp = await client.post("/payments/checkout-session", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "url" in body
    # The URL may be empty string in test env (no real Stripe key), but the key must exist
    assert isinstance(body["url"], str)


async def test_checkout_session_already_paid_basic_returns_400(client: AsyncClient) -> None:
    token, user_id = await register_and_login(client)
    await _set_subscription_tier(user_id, SubscriptionTier.BASIC)

    resp = await client.post("/payments/checkout-session", headers=auth_headers(token))
    assert resp.status_code == 400
    assert "already" in resp.json()["detail"].lower()


async def test_checkout_session_already_paid_pro_returns_400(client: AsyncClient) -> None:
    token, user_id = await register_and_login(client)
    await _set_subscription_tier(user_id, SubscriptionTier.PRO)

    resp = await client.post("/payments/checkout-session", headers=auth_headers(token))
    assert resp.status_code == 400


async def test_checkout_session_unauthenticated_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/payments/checkout-session")
    assert resp.status_code == 401


async def test_checkout_session_bad_token_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/payments/checkout-session",
        headers={"Authorization": "Bearer garbage.token.value"},
    )
    assert resp.status_code == 401


async def test_checkout_session_free_user_can_call_twice(client: AsyncClient) -> None:
    """Each call to checkout-session for a free user should work (idempotent from API perspective)."""
    token, _uid = await register_and_login(client)
    headers = auth_headers(token)

    resp1 = await client.post("/payments/checkout-session", headers=headers)
    assert resp1.status_code == 200

    resp2 = await client.post("/payments/checkout-session", headers=headers)
    assert resp2.status_code == 200


# ---------------------------------------------------------------------------
# POST /payments/webhook
# ---------------------------------------------------------------------------


async def test_webhook_no_stripe_signature_returns_200_received_true(
    client: AsyncClient,
) -> None:
    """Without a valid Stripe signature, verify_webhook returns None and the
    endpoint still responds gracefully with {"received": True}."""
    resp = await client.post(
        "/payments/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


async def test_webhook_with_invalid_signature_returns_200_received_true(
    client: AsyncClient,
) -> None:
    payload = json.dumps({"type": "checkout.session.completed"}).encode()
    resp = await client.post(
        "/payments/webhook",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "stripe-signature": "t=invalid,v1=badsig",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


async def test_webhook_with_empty_body_returns_200_received_true(
    client: AsyncClient,
) -> None:
    resp = await client.post(
        "/payments/webhook",
        content=b"",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


async def test_webhook_with_malformed_json_body_returns_200_received_true(
    client: AsyncClient,
) -> None:
    """Stripe sends raw bytes; the endpoint reads body directly, so malformed
    JSON is fine — verify_webhook handles it gracefully."""
    resp = await client.post(
        "/payments/webhook",
        content=b"this is not json at all",
        headers={"stripe-signature": "t=123,v1=abc"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


async def test_webhook_with_non_payment_event_returns_200_received_true(
    client: AsyncClient,
) -> None:
    """An irrelevant Stripe event type should be gracefully ignored."""
    payload = json.dumps({"type": "customer.created", "data": {"object": {}}}).encode()
    resp = await client.post(
        "/payments/webhook",
        content=payload,
        headers={"stripe-signature": "t=1,v1=irrelevant"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


async def test_webhook_does_not_require_auth(client: AsyncClient) -> None:
    """Stripe webhooks must be accessible without Authorization header."""
    resp = await client.post(
        "/payments/webhook",
        content=b"{}",
    )
    assert resp.status_code == 200
