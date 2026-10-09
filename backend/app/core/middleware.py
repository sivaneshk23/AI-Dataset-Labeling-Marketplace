"""Cross-cutting HTTP middleware: security headers and rate limiting.

Review-II (Sections 9.5 and 9.6) asks for a sensible security baseline and for
basic monitoring. Passwords are already hashed with bcrypt, every payload is
validated with Pydantic, CORS is restricted to configured origins and all
database access goes through SQLAlchemy, so this module adds the two remaining
browser-facing protections plus a lightweight abuse guard:

* :class:`SecurityHeadersMiddleware` sets the hardening response headers that a
  reviewer looks for when they open the browser developer tools.
* :class:`RateLimitMiddleware` throttles repeated requests from one client and
  answers with the standard ``{success, data, message}`` envelope.

Both are *pure ASGI* wrappers rather than ``BaseHTTPMiddleware`` subclasses so
they never interfere with streaming responses such as the CSV export.
"""

import time
from collections import deque
from threading import Lock

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.schemas.response import error_response

logger = get_logger(__name__)

#: Paths the hosting platform polls constantly; throttling them would make the
#: service look unhealthy. The API documentation routes are exempt as well so
#: the hosted Swagger UI keeps working once the limit is reached.
RATE_LIMIT_EXEMPT_PATHS = frozenset(
    {
        "/",
        "/health",
        "/api/health",
        "/favicon.ico",
        "/openapi.json",
    }
)

RATE_LIMIT_EXEMPT_PREFIXES = (
    "/docs",
    "/redoc",
)

#: Headers applied to every API response. ``frame-ancestors`` is used instead
#: of a full ``default-src 'none'`` policy because a restrictive policy would
#: break the Swagger UI bundle loaded from a CDN at ``/docs``.
STATIC_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Content-Security-Policy": "frame-ancestors 'none'",
}


class SecurityHeadersMiddleware:
    """Attach hardening headers to every HTTP response.

    Args:
        app: The next ASGI application in the stack.
    """

    def __init__(self, app) -> None:
        self.app = app

    def build_headers(self) -> dict[str, str]:
        """Return the header set for the current environment.

        Returns:
            The static hardening headers, plus ``Strict-Transport-Security``
            when the application runs in production over HTTPS.
        """
        headers = dict(STATIC_SECURITY_HEADERS)

        if settings.is_production:
            headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age_seconds}; includeSubDomains"
            )

        return headers

    async def __call__(self, scope, receive, send) -> None:
        """Wrap the response start message and merge in the headers."""
        if scope["type"] != "http" or not settings.security_headers_enabled:
            await self.app(scope, receive, send)
            return

        headers = self.build_headers()

        async def send_with_headers(message) -> None:
            """Attach security headers to the ASGI response start event."""
            if message["type"] == "http.response.start":
                mutable = MutableHeaders(scope=message)

                for name, value in headers.items():
                    mutable.setdefault(name, value)

            await send(message)

        await self.app(scope, receive, send_with_headers)


class SlidingWindowLimiter:
    """Count requests per key inside a rolling time window.

    The counters live in process memory, which is enough for the single
    instance used by this capstone deployment. A multi-instance deployment
    would move the same logic to Redis.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max(1, max_requests)
        self.window_seconds = max(1, window_seconds)
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def hit(self, key: str, now: float | None = None) -> tuple[bool, int]:
        """Record one request for ``key``.

        Args:
            key: Identifier of the caller (usually the client address).
            now: Optional monotonic timestamp, injected by tests.

        Returns:
            A ``(allowed, retry_after_seconds)`` tuple. ``retry_after_seconds``
            is ``0`` when the request is allowed.
        """
        moment = time.monotonic() if now is None else now
        cutoff = moment - self.window_seconds

        with self._lock:
            bucket = self._hits.setdefault(key, deque())

            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = max(1, int(bucket[0] + self.window_seconds - moment))

                return False, retry_after

            bucket.append(moment)

            return True, 0

    def reset(self) -> None:
        """Clear every counter; used between tests."""
        with self._lock:
            self._hits.clear()


class RateLimitMiddleware:
    """Reject abusive request bursts with ``429 Too Many Requests``.

    Args:
        app: The next ASGI application in the stack.

    Notes:
        The effective limits are read from :mod:`backend.app.core.config` on
        every request, so the hosting platform can change them through
        environment variables without a code change.
    """

    def __init__(self, app) -> None:
        self.app = app
        self._limiter: SlidingWindowLimiter | None = None
        self._signature: tuple[int, int] | None = None

    def limiter(self) -> SlidingWindowLimiter:
        """Return the limiter, rebuilding it when the settings changed.

        Returns:
            The limiter that matches the current configuration.
        """
        signature = (
            settings.rate_limit_requests,
            settings.rate_limit_window_seconds,
        )

        if self._limiter is None or self._signature != signature:
            self._limiter = SlidingWindowLimiter(*signature)
            self._signature = signature

        return self._limiter

    @staticmethod
    def is_exempt(path: str) -> bool:
        """Return True when ``path`` must never be throttled.

        Args:
            path: Request path taken from the ASGI scope.

        Returns:
            True for health probes and for the API documentation routes.
        """
        if path in RATE_LIMIT_EXEMPT_PATHS:
            return True

        return path.startswith(RATE_LIMIT_EXEMPT_PREFIXES)

    @staticmethod
    def client_key(scope) -> str:
        """Resolve the throttling key for a request.

        Args:
            scope: ASGI connection scope.

        Returns:
            The forwarded client address when the deployment runs behind a
            trusted proxy, otherwise the direct peer address.
        """
        if settings.trust_proxy_headers:
            forwarded = MutableHeaders(scope=scope).get("x-forwarded-for")

            if forwarded:
                return forwarded.split(",")[0].strip()

        client = scope.get("client")

        if client:
            return str(client[0])

        return "unknown"

    async def __call__(self, scope, receive, send) -> None:
        """Throttle the request or forward it to the application."""
        if scope["type"] != "http" or not settings.rate_limit_enabled:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        if self.is_exempt(path):
            await self.app(scope, receive, send)
            return

        key = self.client_key(scope)
        allowed, retry_after = self.limiter().hit(key)

        if allowed:
            await self.app(scope, receive, send)
            return

        logger.warning(
            "Rate limit reached for %s on %s.",
            key,
            path,
        )

        response = JSONResponse(
            status_code=429,
            content=error_response(
                "Too many requests. Please slow down and try again shortly."
            ).model_dump(),
            headers={"Retry-After": str(retry_after)},
        )

        await response(scope, receive, send)
