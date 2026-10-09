"""Tests for the security baseline middleware (Review-II, Sections 9.5/9.6).

The suite covers the response hardening headers, the environment dependent HSTS
header, the health probes used by the hosting platform and the behaviour of the
sliding window rate limiter (both the helper class and the 429 response).
"""

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.middleware import (
    STATIC_SECURITY_HEADERS,
    RateLimitMiddleware,
    SlidingWindowLimiter,
)
from backend.app.main import app


def test_security_headers_are_attached_to_responses():
    """Every response carries the hardening headers."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    for name, value in STATIC_SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_hsts_header_is_added_only_in_production(monkeypatch):
    """HSTS is skipped locally so the browser still accepts http://localhost."""
    with TestClient(app) as client:
        assert "strict-transport-security" not in client.get("/health").headers

    monkeypatch.setattr(settings, "environment", "production")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.headers["strict-transport-security"] == (
        f"max-age={settings.hsts_max_age_seconds}; includeSubDomains"
    )


def test_security_headers_can_be_disabled(monkeypatch):
    """The feature flag lets a developer debug without the extra headers."""
    monkeypatch.setattr(settings, "security_headers_enabled", False)

    with TestClient(app) as client:
        response = client.get("/health")

    assert "x-content-type-options" not in response.headers


def test_health_endpoints_report_the_service_status():
    """The monitoring endpoints used by the deployment keep working."""
    with TestClient(app) as client:
        root = client.get("/")
        health = client.get("/api/health")

    assert root.json()["data"]["status"] == "running"
    assert health.json()["data"]["status"] == "healthy"
    assert health.json()["success"] is True


def test_rate_limit_exemptions_cover_probes_and_documentation():
    """Health probes and the hosted API documentation are never throttled."""
    assert RateLimitMiddleware.is_exempt("/") is True
    assert RateLimitMiddleware.is_exempt("/health") is True
    assert RateLimitMiddleware.is_exempt("/api/health") is True
    assert RateLimitMiddleware.is_exempt("/docs") is True
    assert RateLimitMiddleware.is_exempt("/openapi.json") is True
    assert RateLimitMiddleware.is_exempt("/api/datasets") is False


def test_rate_limit_answers_with_the_standard_envelope(monkeypatch):
    """A burst of requests is rejected with 429 and the shared envelope."""
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_requests", 2)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)

    with TestClient(app) as client:
        first = client.get("/api/datasets")
        second = client.get("/api/datasets")
        third = client.get("/api/datasets")

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429
    assert third.json()["success"] is False
    assert "Too many requests" in third.json()["message"]
    assert third.headers["Retry-After"].isdigit()


def test_sliding_window_limiter_allows_requests_again_after_the_window():
    """Counters expire once the rolling window has moved on."""
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=10)

    assert limiter.hit("client", now=0.0) == (True, 0)
    assert limiter.hit("client", now=1.0) == (True, 0)

    allowed, retry_after = limiter.hit("client", now=2.0)

    assert allowed is False
    assert retry_after == 8

    assert limiter.hit("client", now=11.0) == (True, 0)

    limiter.reset()

    assert limiter.hit("client", now=12.0) == (True, 0)


def test_sliding_window_limiter_tracks_clients_independently():
    """One noisy client must not throttle everybody else."""
    limiter = SlidingWindowLimiter(max_requests=1, window_seconds=30)

    assert limiter.hit("first", now=0.0) == (True, 0)
    assert limiter.hit("first", now=0.0)[0] is False
    assert limiter.hit("second", now=0.0) == (True, 0)
