import threading
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, requests: int, window_seconds: int) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.requests = requests
        self.window_seconds = window_seconds
        self._events: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path == "/health":
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        key = f"{client}:{request.url.path if request.url.path == '/api/auth/login' else 'api'}"
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and events[0] <= now - self.window_seconds:
                events.popleft()
            if len(events) >= self.requests:
                return Response(
                    content='{"detail":"Rate limit exceeded"}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(self.window_seconds)},
                )
            events.append(now)
        return await call_next(request)
