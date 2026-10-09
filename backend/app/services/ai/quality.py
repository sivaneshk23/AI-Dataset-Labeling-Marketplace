"""Quality rules used by the AI quality-control enhancement.

The engine is pure: it receives the annotation under test plus pre-computed
aggregates and returns a score, a recommendation and a list of issues. Keeping
the rules side-effect free makes the enhancement fully unit testable.
"""

from dataclasses import dataclass, field

from backend.app.core.text import labels_match, normalise_label

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

RECOMMENDATION_APPROVE = "approve"
RECOMMENDATION_REVIEW = "review"
RECOMMENDATION_REVISE = "revise"

MIN_ACCEPTABLE_SCORE = 80.0
MIN_REVIEW_SCORE = 60.0

RARE_LABEL_THRESHOLD = 0.05
DOMINANT_LABEL_THRESHOLD = 0.8
MIN_ANNOTATIONS_FOR_DISTRIBUTION = 5
MIN_ANNOTATIONS_FOR_DOMINANCE = 10
REPETITION_LIMIT = 3


@dataclass(frozen=True)
class QualityIssue:
    """A single quality rule violation."""

    code: str
    message: str
    severity: str
    penalty: float


@dataclass(frozen=True)
class QualityReport:
    """Outcome of the quality evaluation for one annotation."""

    score: float
    recommendation: str
    agreement: bool | None
    issues: tuple[QualityIssue, ...] = field(default=())


class QualityEngine:
    """Rule based quality scoring for submitted annotations."""

    def __init__(
        self,
        min_confidence: float = 0.55,
    ) -> None:
        """Store the configured confidence threshold.

        Args:
            min_confidence: Confidence below this value is flagged.
        """
        self.min_confidence = min_confidence

    def evaluate(
        self,
        label: str,
        notes: str | None = None,
        confidence: float | None = None,
        ai_suggested_label: str | None = None,
        ai_confidence: float | None = None,
        label_counts: dict[str, int] | None = None,
        total_annotations: int = 0,
        repeated_submissions: int = 0,
    ) -> QualityReport:
        """Evaluate one annotation and return a quality report."""
        issues: list[QualityIssue] = []

        cleaned_label = " ".join(str(label or "").split())

        if len(cleaned_label) < 2:
            issues.append(
                QualityIssue(
                    code="invalid_label",
                    message=("The submitted label is too short to be useful."),
                    severity=SEVERITY_HIGH,
                    penalty=40.0,
                )
            )

        if confidence is not None and confidence < self.min_confidence:
            issues.append(
                QualityIssue(
                    code="low_confidence",
                    message=(
                        f"Annotator confidence {confidence:.2f} is below "
                        f"the configured threshold "
                        f"{self.min_confidence:.2f}."
                    ),
                    severity=SEVERITY_MEDIUM,
                    penalty=15.0,
                )
            )

        agreement = self._agreement(
            cleaned_label,
            ai_suggested_label,
        )

        if agreement is False and (ai_confidence or 0) >= 0.75:
            issues.append(
                QualityIssue(
                    code="ai_disagreement",
                    message=(
                        "The human label differs from the AI suggestion "
                        f"'{ai_suggested_label}'."
                    ),
                    severity=SEVERITY_HIGH,
                    penalty=20.0,
                )
            )

        if not (notes or "").strip():
            issues.append(
                QualityIssue(
                    code="missing_notes",
                    message=("No annotation notes were provided for reviewers."),
                    severity=SEVERITY_LOW,
                    penalty=5.0,
                )
            )

        issues.extend(
            self._distribution_issues(
                cleaned_label,
                label_counts or {},
                total_annotations,
            )
        )

        if repeated_submissions > REPETITION_LIMIT:
            issues.append(
                QualityIssue(
                    code="repetitive_submission",
                    message=(
                        "The same label and notes were submitted "
                        f"{repeated_submissions} times for this job."
                    ),
                    severity=SEVERITY_MEDIUM,
                    penalty=10.0,
                )
            )

        score = max(
            0.0,
            100.0 - sum(issue.penalty for issue in issues),
        )

        return QualityReport(
            score=round(score, 2),
            recommendation=self._recommendation(
                score,
                issues,
            ),
            agreement=agreement,
            issues=tuple(issues),
        )

    @staticmethod
    def _agreement(
        label: str,
        ai_suggested_label: str | None,
    ) -> bool | None:
        """Return whether the human label matches the AI suggestion."""
        if not ai_suggested_label:
            return None

        return labels_match(label, ai_suggested_label)

    @staticmethod
    def _distribution_issues(
        label: str,
        label_counts: dict[str, int],
        total_annotations: int,
    ) -> list[QualityIssue]:
        """Detect rare and dominant labels for the job."""
        issues: list[QualityIssue] = []

        if total_annotations <= 0:
            return issues

        normalised_counts = {
            normalise_label(key): value for key, value in label_counts.items()
        }

        count = normalised_counts.get(normalise_label(label), 0)
        share = count / total_annotations

        if (
            total_annotations >= MIN_ANNOTATIONS_FOR_DISTRIBUTION
            and share < RARE_LABEL_THRESHOLD
        ):
            issues.append(
                QualityIssue(
                    code="rare_label",
                    message=(
                        f"The label '{label}' covers only "
                        f"{share * 100:.1f}% of submitted annotations."
                    ),
                    severity=SEVERITY_MEDIUM,
                    penalty=10.0,
                )
            )

        if (
            total_annotations >= MIN_ANNOTATIONS_FOR_DOMINANCE
            and share > DOMINANT_LABEL_THRESHOLD
        ):
            issues.append(
                QualityIssue(
                    code="dominant_label",
                    message=(
                        f"The label '{label}' covers "
                        f"{share * 100:.1f}% of submitted annotations, "
                        "which may indicate label bias."
                    ),
                    severity=SEVERITY_MEDIUM,
                    penalty=10.0,
                )
            )

        return issues

    @staticmethod
    def _recommendation(
        score: float,
        issues: list[QualityIssue],
    ) -> str:
        """Translate the score and issues into a reviewer recommendation."""
        has_high_severity = any(issue.severity == SEVERITY_HIGH for issue in issues)

        if score >= MIN_ACCEPTABLE_SCORE and not has_high_severity:
            return RECOMMENDATION_APPROVE

        if score >= MIN_REVIEW_SCORE and not has_high_severity:
            return RECOMMENDATION_REVIEW

        return RECOMMENDATION_REVISE
