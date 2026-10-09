"""Data transfer objects shared by the AI enhancement providers."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class LabelledExample:
    """A previously approved record used as training signal."""

    input_text: str
    label: str


@dataclass(frozen=True)
class LabelSuggestion:
    """Label suggested by an AI provider for one record."""

    label: str
    confidence: float
    rationale: str
    provider: str
    alternatives: tuple[tuple[str, float], ...] = field(
        default=(),
    )


class LabelSuggestionProvider(Protocol):
    """Interface implemented by every AI label suggestion provider."""

    name: str
    # True only for providers backed by an external service. The registry uses
    # this flag to report the AI configuration without guessing from the name.
    is_external: bool

    def suggest(
        self,
        input_text: str,
        candidate_labels: tuple[str, ...],
        examples: tuple[LabelledExample, ...],
    ) -> LabelSuggestion:
        """Return the most likely label for ``input_text``."""
