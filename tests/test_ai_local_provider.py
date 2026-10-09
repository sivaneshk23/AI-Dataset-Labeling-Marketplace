"""Tests for the offline AI label suggestion provider."""

from backend.app.services.ai.base import LabelledExample
from backend.app.services.ai.local_provider import (
    LocalSimilarityProvider,
)

EXAMPLES = (
    LabelledExample(
        input_text="The parcel was delivered to the front door",
        label="delivery",
    ),
    LabelledExample(
        input_text="The shipment arrived two days late",
        label="delivery",
    ),
    LabelledExample(
        input_text="The invoice total does not match the order",
        label="billing",
    ),
    LabelledExample(
        input_text="Duplicate charge appears on my statement",
        label="billing",
    ),
)

CANDIDATES = (
    "delivery",
    "billing",
)


def test_suggest_returns_the_closest_neighbour_label():
    """A record similar to delivery examples is labelled delivery."""
    provider = LocalSimilarityProvider()

    suggestion = provider.suggest(
        "My parcel has not been delivered yet",
        CANDIDATES,
        EXAMPLES,
    )

    assert suggestion.label == "delivery"
    assert suggestion.confidence > 0
    assert suggestion.provider == "local-similarity"
    assert suggestion.alternatives


def test_suggest_is_deterministic():
    """Repeated calls produce identical results."""
    provider = LocalSimilarityProvider()

    first = provider.suggest("Refund for a damaged item", CANDIDATES, EXAMPLES)
    second = provider.suggest("Refund for a damaged item", CANDIDATES, EXAMPLES)

    assert first == second


def test_suggest_uses_label_names_when_no_examples_exist():
    """Without approved examples the label vocabulary is still usable."""
    provider = LocalSimilarityProvider()

    suggestion = provider.suggest(
        "refund request",
        ("refund", "delivery"),
        (),
    )

    assert suggestion.label == "refund"
    assert suggestion.confidence > 0


def test_suggest_without_candidates_returns_empty_suggestion():
    """An empty label vocabulary produces an explanatory empty result."""
    suggestion = LocalSimilarityProvider().suggest(
        "Any record",
        (),
        (),
    )

    assert suggestion.label == ""
    assert suggestion.confidence == 0.0
    assert "No candidate labels" in suggestion.rationale


def test_suggest_with_blank_record_returns_empty_suggestion():
    """Blank records cannot be classified."""
    suggestion = LocalSimilarityProvider().suggest(
        "    ",
        CANDIDATES,
        EXAMPLES,
    )

    assert suggestion.label == ""
    assert suggestion.confidence == 0.0
    assert "usable text tokens" in suggestion.rationale


def test_confidence_never_exceeds_one():
    """Confidence is clamped to the 0-1 range."""
    provider = LocalSimilarityProvider()

    suggestion = provider.suggest(
        "The invoice total does not match the order",
        CANDIDATES,
        EXAMPLES,
    )

    assert 0.0 <= suggestion.confidence <= 1.0

    for _label, confidence in suggestion.alternatives:
        assert 0.0 <= confidence <= 1.0
