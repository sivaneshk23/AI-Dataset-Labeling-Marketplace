"""Tests for the optional Gemini provider.

The Gemini client is replaced with a fake, so these tests never touch the
network and run in CI without any API key.
"""

import pytest

from backend.app.core.errors import ExternalServiceError
from backend.app.services.ai.base import LabelledExample
from backend.app.services.ai.gemini_provider import GeminiProvider


class FakeResponse:
    """Minimal stand-in for a Gemini response object."""

    def __init__(self, text: str) -> None:
        self.text = text


class FakeModels:
    """Records the prompt and returns a canned response or raises."""

    def __init__(
        self,
        text: str = "",
        error: Exception | None = None,
    ) -> None:
        self.text = text
        self.error = error
        self.calls: list[dict] = []

    def generate_content(self, model: str, contents: str) -> FakeResponse:
        self.calls.append({"model": model, "contents": contents})

        if self.error is not None:
            raise self.error

        return FakeResponse(self.text)


class FakeClient:
    """Minimal stand-in for the google-genai client."""

    def __init__(self, models: FakeModels) -> None:
        self.models = models


EXAMPLES = (LabelledExample("invoice total mismatch", "billing"),)


def test_suggest_parses_a_json_response():
    """The provider extracts the label, confidence and rationale."""
    models = FakeModels(
        text=(
            "```json\n"
            '{"label": "billing", "confidence": 0.81, '
            '"rationale": "Invoice wording detected."}\n'
            "```"
        )
    )

    provider = GeminiProvider(
        api_key="test-key",
        model="gemini-test",
        client=FakeClient(models),
    )

    suggestion = provider.suggest(
        "The invoice is wrong",
        ("billing", "delivery"),
        EXAMPLES,
    )

    assert suggestion.label == "billing"
    assert suggestion.confidence == pytest.approx(0.81)
    assert suggestion.provider == "gemini"
    assert models.calls[0]["model"] == "gemini-test"
    assert "invoice total mismatch" in models.calls[0]["contents"]


def test_api_key_is_required_without_an_injected_client():
    """A missing API key disables the provider."""
    with pytest.raises(ExternalServiceError):
        GeminiProvider(api_key="")


def test_malformed_response_raises_external_service_error():
    """Responses without JSON raise a domain error."""
    provider = GeminiProvider(
        api_key="test-key",
        client=FakeClient(FakeModels(text="definitely not json")),
    )

    with pytest.raises(ExternalServiceError):
        provider.suggest("record", ("billing",), EXAMPLES)


def test_api_failure_is_wrapped():
    """Transport or API errors are converted into domain errors."""
    provider = GeminiProvider(
        api_key="test-key",
        client=FakeClient(FakeModels(error=RuntimeError("boom"))),
    )

    with pytest.raises(
        ExternalServiceError,
        match="Gemini request failed",
    ):
        provider.suggest("record", ("billing",), EXAMPLES)


def test_empty_candidate_set_skips_the_api_call():
    """Nothing is sent to the API when no labels are known yet."""
    models = FakeModels(error=AssertionError("API must not be called"))

    provider = GeminiProvider(
        api_key="test-key",
        client=FakeClient(models),
    )

    suggestion = provider.suggest("record", (), ())

    assert suggestion.label == ""
    assert models.calls == []
