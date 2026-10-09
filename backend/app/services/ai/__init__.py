"""AI enhancement package (Day 42-59).

Exposes the provider registry used by :mod:`backend.app.services.ai_service`.
"""

from functools import lru_cache

from backend.app.core.config import settings
from backend.app.core.errors import ExternalServiceError
from backend.app.core.logging import get_logger
from backend.app.services.ai.base import (
    LabelledExample,
    LabelSuggestion,
    LabelSuggestionProvider,
)
from backend.app.services.ai.gemini_provider import GeminiProvider
from backend.app.services.ai.local_provider import (
    LocalSimilarityProvider,
)
from backend.app.services.ai.quality import (
    QualityEngine,
    QualityIssue,
    QualityReport,
)

logger = get_logger(__name__)

GEMINI_PROVIDER = "gemini"
LOCAL_PROVIDER = "local"


def build_provider() -> LabelSuggestionProvider:
    """Create the configured label suggestion provider.

    Returns:
        A Gemini backed provider when an API key is configured, otherwise the
        offline similarity provider so the feature always works.
    """
    configured = (settings.ai_provider or "auto").strip().lower()

    wants_gemini = configured in {"gemini", "auto"}

    if wants_gemini and settings.gemini_api_key:
        try:
            provider = GeminiProvider()

            logger.info("AI label suggestions using the Gemini provider.")

            return provider
        except ExternalServiceError as error:
            logger.warning(
                "Gemini provider unavailable, using local provider: %s",
                error,
            )

    return LocalSimilarityProvider()


@lru_cache(maxsize=1)
def get_provider() -> LabelSuggestionProvider:
    """Return the cached application wide AI provider."""
    return build_provider()


def is_external_provider(provider: LabelSuggestionProvider) -> bool:
    """Return True when ``provider`` calls an external AI service.

    Providers advertise this through the ``is_external`` attribute instead of
    comparing names, so the reported AI status stays correct for every future
    provider as well.
    """
    return bool(getattr(provider, "is_external", False))


def reset_provider_cache() -> None:
    """Clear the cached provider (used by tests and configuration reloads)."""
    get_provider.cache_clear()


__all__ = [
    "GEMINI_PROVIDER",
    "LOCAL_PROVIDER",
    "LabelSuggestion",
    "LabelSuggestionProvider",
    "LabelledExample",
    "LocalSimilarityProvider",
    "QualityEngine",
    "QualityIssue",
    "QualityReport",
    "build_provider",
    "get_provider",
    "is_external_provider",
    "reset_provider_cache",
]
