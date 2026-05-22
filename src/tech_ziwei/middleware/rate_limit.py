"""Simple in-memory sliding-window rate limiter middleware."""

import time
from collections import defaultdict, deque
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# (path_prefix, max_requests, window_seconds)
# More restrictive rules come first; first match wins.
_RULES: list[tuple[str, int, int]] = [
    ("/auth/",    15,  60),   # auth endpoints: 15 req/min
    ("/preview",  30,  60),   # public preview: 30 req/min
    ("/",        200, 60),    # everything else: 200 req/min
]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    IP-based sliding-window rate limiter.
    Uses in-memory storage — suitable for single-process deployments.
    For multi-process deployments, replace with a Redis-backed solution.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        # key: (ip, path_prefix) → deque of request timestamps
        self._windows: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ip = (request.client.host if request.client else "unknown")
        path = request.url.path

        for prefix, max_req, window_sec in _RULES:
            if path.startswith(prefix):
                key = (ip, prefix)
                now = time.monotonic()
                window_start = now - window_sec
                q = self._windows[key]

                # Evict timestamps outside the window
                while q and q[0] < window_start:
                    q.popleft()

                if len(q) >= max_req:
                    return Response(
                        content='{"detail":"Too many requests. Please slow down."}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": str(window_sec)},
                    )
                q.append(now)
                break

        return await call_next(request)
