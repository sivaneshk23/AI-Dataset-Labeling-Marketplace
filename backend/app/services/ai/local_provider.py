"""Local, dependency-free AI label suggestion provider.

The provider implements a lightweight nearest-neighbour classifier over
previously approved records:

* records and labels are converted into token frequency vectors,
* the cosine similarity between the new record and every labelled example is
  computed (a term-frequency based k-nearest-neighbour score),
* the weighted vote of the closest neighbours plus the lexical similarity to
  each candidate label name produces the final confidence.

Because the algorithm is deterministic and completely offline it can be unit
tested in CI and always remains available as a graceful fallback when the
optional external provider is unreachable.
"""

from collections import Counter
from math import sqrt

from backend.app.core.text import tokenize
from backend.app.services.ai.base import (
    LabelledExample,
    LabelSuggestion,
)

MAX_NEIGHBOURS = 25
LABEL_NAME_WEIGHT = 0.35
NEIGHBOUR_WEIGHT = 0.65


class LocalSimilarityProvider:
    """Offline nearest-neighbour label suggestion provider."""

    name = "local-similarity"
    is_external = False

    def suggest(
        self,
        input_text: str,
        candidate_labels: tuple[str, ...],
        examples: tuple[LabelledExample, ...],
    ) -> LabelSuggestion:
        """Suggest a label using lexical similarity to approved records."""
        tokens = tokenize(input_text)

        if not tokens:
            return LabelSuggestion(
                label="",
                confidence=0.0,
                rationale=("The record does not contain usable text tokens."),
                provider=self.name,
            )

        candidates = self._candidate_labels(
            candidate_labels,
            examples,
        )

        if not candidates:
            return LabelSuggestion(
                label="",
                confidence=0.0,
                rationale=(
                    "No candidate labels are available yet. Approve at "
                    "least one annotation to enable suggestions."
                ),
                provider=self.name,
            )

        record_vector = self._vector(tokens)

        neighbour_scores = self._neighbour_scores(
            record_vector,
            examples,
        )

        scores = [
            (
                label,
                self._score_label(
                    label,
                    record_vector,
                    neighbour_scores,
                ),
            )
            for label in candidates
        ]

        scores.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        best_label, best_score = scores[0]

        confidence = round(
            min(1.0, max(0.0, best_score)),
            4,
        )

        alternatives = tuple(
            (label, round(min(1.0, max(0.0, score)), 4))
            for label, score in scores[1:4]
            if score > 0
        )

        return LabelSuggestion(
            label=best_label,
            confidence=confidence,
            rationale=(
                f"Chosen from {len(candidates)} candidate labels using "
                f"{len(neighbour_scores)} similar approved record(s)."
            ),
            provider=self.name,
            alternatives=alternatives,
        )

    @staticmethod
    def _candidate_labels(
        candidate_labels: tuple[str, ...],
        examples: tuple[LabelledExample, ...],
    ) -> tuple[str, ...]:
        """Merge declared labels with labels observed in examples."""
        merged: dict[str, str] = {}

        for label in candidate_labels:
            cleaned = " ".join(str(label).split())

            if cleaned:
                merged.setdefault(cleaned.lower(), cleaned)

        for example in examples:
            cleaned = " ".join(str(example.label).split())

            if cleaned:
                merged.setdefault(cleaned.lower(), cleaned)

        return tuple(merged.values())

    @staticmethod
    def _vector(tokens: list[str]) -> dict[str, float]:
        """Build a normalised token frequency vector."""
        counts = Counter(tokens)
        total = float(len(tokens))

        return {token: count / total for token, count in counts.items()}

    @staticmethod
    def _cosine(
        first: dict[str, float],
        second: dict[str, float],
    ) -> float:
        """Return the cosine similarity between two sparse vectors."""
        if not first or not second:
            return 0.0

        keys = set(first) & set(second)

        if not keys:
            return 0.0

        dot = sum(first[key] * second[key] for key in keys)

        first_norm = sqrt(sum(value**2 for value in first.values()))
        second_norm = sqrt(sum(value**2 for value in second.values()))

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return dot / (first_norm * second_norm)

    def _neighbour_scores(
        self,
        record_vector: dict[str, float],
        examples: tuple[LabelledExample, ...],
    ) -> list[tuple[str, float]]:
        """Return similarity scores of the closest labelled examples."""
        scored: list[tuple[str, float]] = []

        for example in examples:
            example_vector = self._vector(tokenize(example.input_text))

            similarity = self._cosine(
                record_vector,
                example_vector,
            )

            if similarity > 0:
                scored.append((example.label, similarity))

        scored.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scored[:MAX_NEIGHBOURS]

    def _score_label(
        self,
        label: str,
        record_vector: dict[str, float],
        neighbour_scores: list[tuple[str, float]],
    ) -> float:
        """Combine neighbour votes with label name similarity."""
        name_similarity = self._cosine(
            record_vector,
            self._vector(tokenize(label)),
        )

        neighbour_total = sum(score for _, score in neighbour_scores)

        if neighbour_total > 0:
            neighbour_score = (
                sum(
                    score
                    for example_label, score in neighbour_scores
                    if example_label.strip().lower() == label.strip().lower()
                )
                / neighbour_total
            )
        else:
            neighbour_score = 0.0

        return neighbour_score * NEIGHBOUR_WEIGHT + name_similarity * LABEL_NAME_WEIGHT
