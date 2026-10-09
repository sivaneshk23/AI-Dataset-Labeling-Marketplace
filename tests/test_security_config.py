"""Tests for the runtime configuration guard (Review-II, Section 9.5).

The guard exists so a deployment can never go live with the placeholder secret
from ``.env.example`` or with a local-only database URL. Local development only
receives warnings, which keeps the getting-started instructions in the README
usable on a fresh machine.
"""

import pytest

from backend.app.core.config import (
    MINIMUM_PRODUCTION_SECRET_LENGTH,
    PLACEHOLDER_DATABASE_USER,
    PLACEHOLDER_SECRET_KEY,
    Settings,
    verify_runtime_settings,
)

SAFE_SECRET = "s" * MINIMUM_PRODUCTION_SECRET_LENGTH
SAFE_DATABASE_URL = "postgresql://marketplace:secret@db.internal:5432/marketplace"


def build_settings(**overrides) -> Settings:
    """Build an isolated settings object for a test case."""
    values = {
        "secret_key": SAFE_SECRET,
        "database_url": SAFE_DATABASE_URL,
        "cors_origins": "https://marketplace.example",
    }
    values.update(overrides)

    return Settings(**values)


def test_development_reports_the_placeholder_secret_without_failing():
    """A developer sees the warning but is not blocked from working."""
    problems = verify_runtime_settings(
        build_settings(secret_key=PLACEHOLDER_SECRET_KEY)
    )

    assert any("SECRET_KEY" in problem for problem in problems)


def test_short_secret_is_reported():
    """Weak secrets are reported even outside production."""
    problems = verify_runtime_settings(build_settings(secret_key="short"))

    assert any("shorter" in problem for problem in problems)


def test_placeholder_database_url_is_reported():
    """The local placeholder database is flagged."""
    placeholder_url = f"postgresql://{PLACEHOLDER_DATABASE_USER}/marketplace"

    problems = verify_runtime_settings(build_settings(database_url=placeholder_url))

    assert any("DATABASE_URL" in problem for problem in problems)


def test_empty_cors_origins_is_reported():
    """CORS must list at least one origin instead of relying on a wildcard."""
    problems = verify_runtime_settings(build_settings(cors_origins=" , "))

    assert any("CORS_ORIGINS" in problem for problem in problems)


def test_production_accepts_a_secure_configuration():
    """A properly configured production environment has no findings."""
    config = build_settings(environment="production")

    assert config.is_production is True
    assert verify_runtime_settings(config) == []


def test_production_refuses_to_start_with_the_placeholder_secret():
    """The guard raises instead of booting an insecure production service."""
    config = build_settings(
        environment="production",
        secret_key=PLACEHOLDER_SECRET_KEY,
    )

    with pytest.raises(RuntimeError, match="Refusing to start in production"):
        verify_runtime_settings(config)
