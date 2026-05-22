"""Integration tests for /auth and /users/me endpoints."""

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


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------


async def test_register_success(client: AsyncClient) -> None:
    email = _unique_email()
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == email
    assert body["is_active"] is True
    assert body["subscription_tier"] == "free"
    assert "id" in body
    assert "created_at" in body
    # password must NOT be returned
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    email = _unique_email()
    await client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = await client.post("/auth/register", json={"email": email, "password": "other_pass"})
    assert resp.status_code == 409


async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert resp.status_code == 422


async def test_register_missing_password_returns_422(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"email": _unique_email()},
    )
    assert resp.status_code == 422


async def test_register_missing_email_returns_422(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"password": "password123"},
    )
    assert resp.status_code == 422


async def test_register_empty_body_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/auth/register", json={})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------


async def test_login_success_returns_token(client: AsyncClient) -> None:
    email = _unique_email()
    await client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    email = _unique_email()
    await client.post("/auth/register", json={"email": email, "password": "password123"})
    resp = await client.post("/auth/login", json={"email": email, "password": "wrongpass"})
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody_" + _unique_email(), "password": "password123"},
    )
    assert resp.status_code == 401


async def test_login_invalid_email_format_returns_422(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "not-valid", "password": "password123"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------


async def test_get_me_with_valid_token_returns_200(client: AsyncClient) -> None:
    email = _unique_email()
    token = await register_and_login(client, email=email)
    resp = await client.get("/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == email
    assert body["is_active"] is True
    assert body["subscription_tier"] == "free"
    assert "id" in body


async def test_get_me_with_no_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/users/me")
    assert resp.status_code == 401


async def test_get_me_with_bad_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/users/me", headers={"Authorization": "Bearer this.is.not.valid"})
    assert resp.status_code == 401


async def test_get_me_with_malformed_header_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/users/me", headers={"Authorization": "NotBearer sometoken"})
    assert resp.status_code == 401


async def test_get_me_response_has_no_password_field(client: AsyncClient) -> None:
    token = await register_and_login(client)
    resp = await client.get("/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "hashed_password" not in body
    assert "password" not in body
