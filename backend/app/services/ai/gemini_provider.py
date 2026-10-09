"""Optional Gemini provider for AI assisted annotation (Day 42-59).

This is the project's third-party integration: Google Gemini is queried through
the official ``google-genai`` SDK. The provider is completely optional:

* it is only constructed when ``GEMINI_API_KEY`` is configured,
* the import is lazy, so the application runs even when the SDK is absent,
* any failure raises :class:`ExternalServiceError` and the AI service falls
  back to the offline similarity provider, keeping the product functional.

The API key is read from the environment only, never from source code.
"""

import json

from backend.app.core.config import settings
from backend.app.core.errors import ExternalServiceError
from backend.app.services.ai.base import (
    LabelledExample,
    LabelSuggestion,
)

PROMPT_TEMPLATE = (
    "You are an annotation assistant for a dataset labeling marketplace.\n"
    "Choose exactly one label for the record below.\n"
    "Allowed labels: {labels}\n"
    "Previously approved examples:\n{examples}\n"
    "Record: {record}\n"
    'Answer with JSON only: {{"label": "...", "confidence": 0.0-1.0, '
    '"rationale": "..."}}'
)

MAX_EXAMPLE_LINES = 12


class GeminiProvider:
    """Label suggestion provider backed by the Google Gemini API."""

    name = "gemini"
    is_external = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        client: object | None = None,
    ) -> None:
        """Create the provider.

        Args:
            api_key: Gemini API key, defaults to the configured secret.
            model: Gemini model name, defaults to the configured model.
            client: Optional pre-built client, injected by tests.
        """
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._client = client

        if self._client is None and not self.api_key:
            raise ExternalServiceError("GEMINI_API_KEY is not configured.")

    @property
    def client(self) -> object:
        """Return a lazily created Gemini client."""
        if self._client is None:
            try:
                from google import genai
            except ImportError as error:  # pragma: no cover
                raise ExternalServiceError(
                    "The google-genai package is not installed."
                ) from error

            self._client = genai.Client(api_key=self.api_key)

        return self._client

    def suggest(
        self,
        input_text: str,
        candidate_labels: tuple[str, ...],
        examples: tuple[LabelledExample, ...],
    ) -> LabelSuggestion:
        """Ask Gemini for the most likely label.

        Raises:
            ExternalServiceError: when the API call fails or the response
                cannot be parsed.
        """
        if not candidate_labels and not examples:
            return LabelSuggestion(
                label="",
                confidence=0.0,
                rationale="No candidate labels are available yet.",
                provider=self.name,
            )

        prompt = PROMPT_TEMPLATE.format(
            labels=", ".join(candidate_labels) or "(derive from examples)",
            examples=self._format_examples(examples),
            record=input_text.strip(),
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            payload = self._parse_response(getattr(response, "text", "") or "")
        except ExternalServiceError:
            raise
        except Exception as error:
            raise ExternalServiceError(f"Gemini request failed: {error}") from error

        return LabelSuggestion(
            label=payload.get("label", ""),
            confidence=float(payload.get("confidence", 0.0)),
            rationale=str(payload.get("rationale", "Suggested by Gemini.")),
            provider=self.name,
        )

    @staticmethod
    def _format_examples(
        examples: tuple[LabelledExample, ...],
    ) -> str:
        """Render approved examples for the prompt."""
        if not examples:
            return "(none yet)"

        lines = [
            f"- {example.input_text.strip()[:160]} => {example.label}"
            for example in examples[:MAX_EXAMPLE_LINES]
        ]

        return "\n".join(lines)

    @staticmethod
    def _parse_response(text: str) -> dict:
        """Extract the JSON object returned by the model."""
        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ExternalServiceError("Gemini returned an unexpected response.")

        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as error:
            raise ExternalServiceError("Gemini returned malformed JSON.") from error

        if not isinstance(payload, dict):
            raise ExternalServiceError("Gemini returned an unexpected payload.")

        return payload
