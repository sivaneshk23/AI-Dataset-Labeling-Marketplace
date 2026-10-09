"""Application configuration for the AI Dataset Labeling Marketplace backend.

All runtime configuration is environment driven. Real values live in ``.env``
(never committed) while ``.env.example`` documents every supported variable.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

#: Placeholder values shipped in ``.env.example``. They must never be used by a
#: real deployment, so :func:`verify_runtime_settings` refuses to start in
#: production when one of them is still active.
PLACEHOLDER_SECRET_KEY = "your_secret_key_here"
PLACEHOLDER_DATABASE_USER = "username:password@localhost"
MINIMUM_PRODUCTION_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """Environment-driven application settings."""

    app_name: str = "AI Dataset Labeling Marketplace API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Database
    database_url: str = (
        "postgresql://username:password@localhost:5432/dataset_labeling_marketplace"
    )

    # Authentication
    secret_key: str = PLACEHOLDER_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS: comma separated list of allowed frontend origins.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Observability
    log_level: str = "INFO"

    # Security baseline (Review-II). The rate limiter protects the public
    # deployment from accidental request floods; the headers middleware is
    # covered by tests/test_middleware.py.
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 240
    rate_limit_window_seconds: int = 60
    security_headers_enabled: bool = True
    trust_proxy_headers: bool = False
    hsts_max_age_seconds: int = 31_536_000

    # AI enhancement (Day 42-59): the local provider always works, the optional
    # Gemini provider is activated when an API key is configured.
    ai_provider: str = "auto"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    ai_min_confidence: float = 0.55

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Return the configured CORS origins as a clean list."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        """Return True when the application runs in a production environment."""
        return self.environment.strip().lower() in {
            "production",
            "prod",
        }


def verify_runtime_settings(config: Settings | None = None) -> list[str]:
    """Return the configuration problems found for the current runtime.

    The application refuses to start when it runs in production with a
    placeholder secret; during local development the same findings are only
    reported so a developer can see the problem without being blocked.

    Args:
        config: Optional settings object, defaulting to the module singleton.

    Returns:
        Human readable problem descriptions; empty when the configuration is
        safe to use.

    Raises:
        RuntimeError: when a fatal production misconfiguration is detected.
    """
    active = config if config is not None else settings

    problems: list[str] = []

    secret = active.secret_key.strip()

    if not secret or secret == PLACEHOLDER_SECRET_KEY:
        problems.append("SECRET_KEY is still the placeholder value.")
    elif len(secret) < MINIMUM_PRODUCTION_SECRET_LENGTH:
        problems.append(
            f"SECRET_KEY is shorter than {MINIMUM_PRODUCTION_SECRET_LENGTH} characters."
        )

    if PLACEHOLDER_DATABASE_USER in active.database_url:
        problems.append("DATABASE_URL still points at the local placeholder instance.")

    if not active.cors_origin_list:
        problems.append("CORS_ORIGINS must list at least one allowed origin.")

    if active.is_production and problems:
        raise RuntimeError("Refusing to start in production: " + " ".join(problems))

    return problems


settings = Settings()
