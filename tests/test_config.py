"""Configuration layer tests."""

from backend.app.core.config import Settings, settings


def test_configuration_values():
    """The environment driven settings keep their documented defaults."""
    assert settings.database_url
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.app_name


def test_cors_origin_list_is_parsed():
    """Comma separated CORS origins are exposed as a clean list."""
    custom = Settings(cors_origins="https://app.example.com, https://x.test,")

    assert custom.cors_origin_list == [
        "https://app.example.com",
        "https://x.test",
    ]


def test_environment_flags():
    """Production detection is case insensitive."""
    assert Settings(environment="production").is_production is True
    assert Settings(environment="PROD").is_production is True
    assert Settings(environment="development").is_production is False


def test_ai_settings_defaults():
    """The AI enhancement defaults to the offline auto provider."""
    assert settings.ai_provider in {"auto", "local", "gemini"}
    assert 0.0 <= settings.ai_min_confidence <= 1.0
    assert settings.gemini_model
