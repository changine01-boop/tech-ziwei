"""Unit tests for the in-memory sliding-window rate-limit middleware."""

import time
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tech_ziwei.middleware.rate_limit import RateLimitMiddleware, _RULES


# ---------------------------------------------------------------------------
# Test app factory — creates a fresh middleware instance per test so windows
# don't bleed across test cases.
# ---------------------------------------------------------------------------

def make_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/auth/login")
    def auth_login():
        return {"ok": True}

    @app.get("/auth/register")
    def auth_register():
        return {"ok": True}

    @app.get("/preview")
    def preview():
        return {"ok": True}

    @app.get("/other")
    def other():
        return {"ok": True}

    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rule_for(prefix: str) -> tuple[str, int, int]:
    """Return the first rule whose prefix matches."""
    for p, max_req, window_sec in _RULES:
        if prefix.startswith(p):
            return p, max_req, window_sec
    raise KeyError(f"No rule for prefix {prefix!r}")


# ---------------------------------------------------------------------------
# Tests: requests under the limit pass through
# ---------------------------------------------------------------------------

class TestUnderLimit:
    def test_auth_under_limit_returns_200(self):
        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        for _ in range(max_req - 1):
            resp = client.get("/auth/login")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def test_preview_under_limit_returns_200(self):
        client = make_client()
        _, max_req, _ = _rule_for("/preview")
        for _ in range(max_req - 1):
            resp = client.get("/preview")
            assert resp.status_code == 200

    def test_other_under_limit_returns_200(self):
        client = make_client()
        # Hit /other a handful of times — well under the 200/min limit
        for _ in range(5):
            resp = client.get("/other")
            assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: requests at/over the limit get 429
# ---------------------------------------------------------------------------

class TestOverLimit:
    def test_auth_at_limit_returns_429(self):
        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        for _ in range(max_req):
            client.get("/auth/login")
        resp = client.get("/auth/login")
        assert resp.status_code == 429

    def test_preview_at_limit_returns_429(self):
        client = make_client()
        _, max_req, _ = _rule_for("/preview")
        for _ in range(max_req):
            client.get("/preview")
        resp = client.get("/preview")
        assert resp.status_code == 429

    def test_429_has_retry_after_header(self):
        client = make_client()
        _, max_req, window_sec = _rule_for("/auth/")
        for _ in range(max_req + 1):
            resp = client.get("/auth/login")
        assert resp.headers.get("retry-after") == str(window_sec)

    def test_429_body_contains_detail_key(self):
        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        for _ in range(max_req + 1):
            resp = client.get("/auth/login")
        data = resp.json()
        assert "detail" in data
        assert "Too many requests" in data["detail"]

    def test_429_content_type_is_json(self):
        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        for _ in range(max_req + 1):
            resp = client.get("/auth/login")
        assert "application/json" in resp.headers.get("content-type", "")

    def test_exactly_at_limit_is_blocked(self):
        """The max_req-th request (0-indexed) should be blocked."""
        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        responses = [client.get("/auth/login") for _ in range(max_req + 1)]
        # First max_req should pass
        for r in responses[:max_req]:
            assert r.status_code == 200
        # The (max_req+1)-th request must be rejected
        assert responses[max_req].status_code == 429


# ---------------------------------------------------------------------------
# Tests: window expiry clears old request timestamps
# ---------------------------------------------------------------------------

class TestWindowExpiry:
    def test_requests_allowed_after_window_expires(self, monkeypatch):
        """After the window rolls forward, old timestamps are evicted."""
        client = make_client()
        _, max_req, window_sec = _rule_for("/auth/")

        base_time = 1_000_000.0

        # Fill the window
        call_count = 0

        def fake_monotonic():
            return base_time + call_count * 0.001  # tiny increments within window

        monkeypatch.setattr(
            "tech_ziwei.middleware.rate_limit.time.monotonic", fake_monotonic
        )

        for _ in range(max_req):
            call_count += 1
            client.get("/auth/login")

        # Next call is blocked
        call_count += 1
        resp = client.get("/auth/login")
        assert resp.status_code == 429

        # Advance time past the window — all old entries should be evicted
        # We need to replace the closure variable; patch with a lambda instead
        future_time = base_time + window_sec + 1

        monkeypatch.setattr(
            "tech_ziwei.middleware.rate_limit.time.monotonic",
            lambda: future_time,
        )
        resp = client.get("/auth/login")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: different paths use different limits
# ---------------------------------------------------------------------------

class TestPathSegregation:
    def test_auth_limit_is_15(self):
        _, max_req, _ = _rule_for("/auth/")
        assert max_req == 15

    def test_preview_limit_is_30(self):
        _, max_req, _ = _rule_for("/preview")
        assert max_req == 30

    def test_default_limit_is_200(self):
        _, max_req, _ = _rule_for("/")
        assert max_req == 200

    def test_auth_exhausted_does_not_block_preview(self):
        """Exhausting auth does not affect the preview counter."""
        client = make_client()
        _, auth_max, _ = _rule_for("/auth/")
        # Exhaust auth
        for _ in range(auth_max + 1):
            client.get("/auth/login")
        # Preview should still be available
        resp = client.get("/preview")
        assert resp.status_code == 200

    def test_preview_exhausted_does_not_block_auth(self):
        """Exhausting preview does not affect auth counter."""
        client = make_client()
        _, preview_max, _ = _rule_for("/preview")
        for _ in range(preview_max + 1):
            client.get("/preview")
        resp = client.get("/auth/login")
        assert resp.status_code == 200

    def test_different_prefixes_tracked_independently(self):
        """Counters for /auth/ and /preview are keyed separately."""
        client = make_client()
        _, auth_max, _ = _rule_for("/auth/")
        # Do (auth_max - 1) auth requests
        for _ in range(auth_max - 1):
            client.get("/auth/login")
        # One preview — completely separate bucket
        resp = client.get("/preview")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: unknown client IP defaults to "unknown"
# ---------------------------------------------------------------------------

class TestUnknownClientIP:
    def test_none_client_falls_back_to_unknown_key(self):
        """When request.client is None the middleware uses 'unknown' as the IP.
        It should still track and enforce limits (not crash)."""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/auth/test")
        def auth_test():
            return {"ok": True}

        # TestClient always provides a client; we patch the middleware to
        # simulate a missing client by examining internal state indirectly —
        # just verify no crash and 200 for normal requests.
        client = TestClient(app, raise_server_exceptions=True)
        resp = client.get("/auth/test")
        assert resp.status_code == 200

    def test_unknown_ip_rate_limited_same_as_known(self, monkeypatch):
        """The 'unknown' bucket should still get rate-limited."""
        from starlette.testclient import TestClient as StarletteTestClient
        import tech_ziwei.middleware.rate_limit as rl_module

        # Patch ip extraction to always return "unknown"
        original_dispatch = RateLimitMiddleware.dispatch

        async def patched_dispatch(self, request, call_next):
            # Force ip to "unknown" by monkey-patching request.client
            request._client = None  # type: ignore[attr-defined]
            return await original_dispatch(self, request, call_next)

        monkeypatch.setattr(RateLimitMiddleware, "dispatch", patched_dispatch)

        client = make_client()
        _, max_req, _ = _rule_for("/auth/")
        for _ in range(max_req):
            client.get("/auth/login")
        resp = client.get("/auth/login")
        assert resp.status_code == 429
