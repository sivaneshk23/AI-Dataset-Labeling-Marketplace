"""AI assisted annotation and quality control (Day 42-59 enhancement).

This service integrates the enhancement directly into the existing workflow:

* :meth:`AIService.suggest_label` provides AI pre-labelling so annotators can
  accept or correct a suggested label instead of typing it from scratch.
* :meth:`AIService.evaluate_annotation` scores a submitted annotation against
  the job's label distribution, annotator confidence and AI agreement.
* :meth:`AIService.job_insights` aggregates agreement, duplicates and flagged
  records so dataset owners can act before exporting a dataset.

Every method degrades gracefully: when the optional external provider fails,
the offline similarity provider answers instead, and the failure is logged.
"""

from collections import Counter

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import MarketplaceError, NotFoundError
from backend.app.core.logging import get_logger
from backend.app.core.text import labels_match, normalise_label
from backend.app.models.annotation import Annotation
from backend.app.repositories.annotation_repository import (
    AnnotationRepository,
)
from backend.app.repositories.annotation_task_repository import (
    AnnotationTaskRepository,
)
from backend.app.repositories.labeling_job_repository import (
    LabelingJobRepository,
)
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.ai import (
    LabelledExample,
    LabelSuggestion,
    LocalSimilarityProvider,
    QualityEngine,
    QualityReport,
    get_provider,
    is_external_provider,
)

logger = get_logger(__name__)

MAX_EXAMPLES = 200
MAX_FLAGGED = 20
FLAG_SCORE_THRESHOLD = 80.0
EXAMPLES_STATUSES = (
    "approved",
    "submitted",
)


class AIService:
    """Business logic for the AI enhancement."""

    @staticmethod
    def provider_name() -> str:
        """Return the name of the active AI provider."""
        return get_provider().name

    @staticmethod
    def uses_external_provider() -> bool:
        """Return True when an external AI provider is active.

        The provider declares this itself (``is_external``) instead of the
        service comparing provider names, so offline providers are never
        reported as external integrations.
        """
        return is_external_provider(get_provider())

    @staticmethod
    def suggest_label(
        db: Session,
        job_id: int,
        input_text: str,
        candidate_labels: list[str] | tuple[str, ...] = (),
    ) -> LabelSuggestion:
        """Suggest a label for a record inside a labeling job.

        Args:
            db: Active database session.
            job_id: Labeling job the record belongs to.
            input_text: Record that needs a label.
            candidate_labels: Optional label set defined by the owner.

        Returns:
            The suggested label, its confidence and the provider used.

        Raises:
            NotFoundError: when the labeling job does not exist.
        """
        job = AIService._require_job(db, job_id)

        examples = AIService.approved_examples(db, job_id)
        labels = AIService.candidate_label_set(
            db,
            job_id,
            tuple(candidate_labels) + tuple(job.label_options or []),
        )

        provider = get_provider()

        try:
            return provider.suggest(
                input_text,
                labels,
                examples,
            )
        except MarketplaceError as error:
            logger.warning(
                "AI provider %s failed, falling back to local provider: %s",
                provider.name,
                error,
            )

            return LocalSimilarityProvider().suggest(
                input_text,
                labels,
                examples,
            )

    @staticmethod
    def candidate_label_set(
        db: Session,
        job_id: int,
        extra_labels: list[str] | tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        """Return the label vocabulary of a job.

        Declared labels are merged with the labels already used by annotators.
        """
        merged: dict[str, str] = {}

        for label in extra_labels:
            cleaned = " ".join(str(label).split())

            if cleaned:
                merged.setdefault(cleaned.lower(), cleaned)

        for label, _count in AnnotationRepository.label_distribution(
            db,
            job_id,
        ):
            cleaned = " ".join(str(label).split())

            if cleaned:
                merged.setdefault(cleaned.lower(), cleaned)

        return tuple(merged.values())

    @staticmethod
    def approved_examples(
        db: Session,
        job_id: int,
        limit: int = MAX_EXAMPLES,
    ) -> tuple[LabelledExample, ...]:
        """Return human labelled records used to train the suggestion model."""
        tasks = {
            task.id: task
            for task in AnnotationTaskRepository.get_by_job(
                db,
                job_id,
            )
        }

        examples = [
            LabelledExample(
                input_text=tasks[annotation.task_id].input_text,
                label=annotation.label,
            )
            for annotation in AnnotationRepository.get_by_job(
                db,
                job_id,
            )
            if annotation.status in EXAMPLES_STATUSES
            and annotation.task_id in tasks
            and annotation.label.strip()
        ]

        return tuple(examples[-limit:])

    @staticmethod
    def _require_job(
        db: Session,
        job_id: int,
    ):
        """Return a job or raise when the job is missing."""
        job = LabelingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise NotFoundError("Labeling job not found.")
        return job

    @staticmethod
    def evaluate_annotation(
        db: Session,
        annotation: Annotation,
    ) -> QualityReport:
        """Score one annotation with the AI quality engine.

        Args:
            db: Active database session.
            annotation: Annotation under evaluation.

        Returns:
            The quality report for the annotation.

        Raises:
            NotFoundError: when the parent task is missing.
        """
        task = AnnotationTaskRepository.get_by_id(
            db,
            annotation.task_id,
        )

        if task is None:
            raise NotFoundError("Annotation task not found.")

        label_counts = dict(
            AnnotationRepository.label_distribution(
                db,
                task.job_id,
            )
        )

        return AIService._engine().evaluate(
            label=annotation.label,
            notes=annotation.notes,
            confidence=annotation.confidence,
            ai_suggested_label=annotation.ai_suggested_label,
            ai_confidence=annotation.ai_confidence,
            label_counts=label_counts,
            total_annotations=sum(label_counts.values()),
            repeated_submissions=AIService.count_repetitions(
                db,
                annotation,
            ),
        )

    @staticmethod
    def count_repetitions(
        db: Session,
        annotation: Annotation,
    ) -> int:
        """Count how often an annotator repeated the same submission."""
        symbol = AIService._signature(annotation)
        task = AnnotationTaskRepository.get_by_id(
            db,
            annotation.task_id,
        )

        if task is None:
            return 0

        return sum(
            1
            for other in AnnotationRepository.get_by_job(
                db,
                task.job_id,
            )
            if other.annotator_id == annotation.annotator_id
            and AIService._signature(other) == symbol
        )

    @staticmethod
    def _signature(
        annotation: Annotation,
    ) -> tuple[int, str, str]:
        """Build a comparable signature for repetition detection."""
        return (
            annotation.annotator_id,
            normalise_label(annotation.label),
            normalise_label(annotation.notes),
        )

    @staticmethod
    def _engine() -> QualityEngine:
        """Return a quality engine configured from the environment."""
        return QualityEngine(
            min_confidence=settings.ai_min_confidence,
        )

    @staticmethod
    def job_insights(
        db: Session,
        job_id: int,
    ) -> dict:
        """Aggregate AI quality insights for a labeling job.

        Args:
            db: Active database session.
            job_id: Labeling job identifier.

        Returns:
            Insight payload consumed by
            :class:`backend.app.schemas.ai.JobInsightsResponse`.

        Raises:
            NotFoundError: when the labeling job does not exist.
        """
        AIService._require_job(db, job_id)

        tasks = AnnotationTaskRepository.get_by_job(db, job_id)
        annotations = AnnotationRepository.get_by_job(db, job_id)
        distribution = AnnotationRepository.label_distribution(
            db,
            job_id,
        )

        label_counts = dict(distribution)
        total_annotations = sum(label_counts.values())

        signatures = Counter(
            AIService._signature(annotation) for annotation in annotations
        )

        engine = AIService._engine()

        flagged: list[tuple[Annotation, QualityReport]] = []
        confidences: list[float] = []

        agreements = 0
        agreement_total = 0
        ai_assisted = 0

        annotator_totals: Counter[int] = Counter()
        annotator_approved: Counter[int] = Counter()
        annotator_ai: Counter[int] = Counter()
        annotator_agreements: Counter[int] = Counter()

        for annotation in annotations:
            annotator_totals[annotation.annotator_id] += 1

            if annotation.status == "approved":
                annotator_approved[annotation.annotator_id] += 1

            if annotation.confidence is not None:
                confidences.append(annotation.confidence)

            if annotation.ai_suggested_label:
                ai_assisted += 1
                agreement_total += 1
                annotator_ai[annotation.annotator_id] += 1

                if labels_match(
                    annotation.label,
                    annotation.ai_suggested_label,
                ):
                    agreements += 1
                    annotator_agreements[annotation.annotator_id] += 1

            report = engine.evaluate(
                label=annotation.label,
                notes=annotation.notes,
                confidence=annotation.confidence,
                ai_suggested_label=annotation.ai_suggested_label,
                ai_confidence=annotation.ai_confidence,
                label_counts=label_counts,
                total_annotations=total_annotations,
                repeated_submissions=signatures[AIService._signature(annotation)],
            )

            if report.score < FLAG_SCORE_THRESHOLD:
                flagged.append((annotation, report))

        flagged.sort(key=lambda item: item[1].score)

        users = {user.id: user for user in UserRepository.get_all(db)}

        labelled_tasks = len({annotation.task_id for annotation in annotations})

        duplicate_annotations = sum(
            count - 1 for count in signatures.values() if count > 1
        )
        agreement_rate = AIService._share(
            agreements,
            agreement_total,
        )
        ai_coverage = (
            AIService._share(
                ai_assisted,
                total_annotations,
            )
            or 0.0
        )
        average_confidence = (
            sum(confidences) / len(confidences) if confidences else None
        )
        unlabelled_tasks = max(
            0,
            len(tasks) - labelled_tasks,
        )

        return {
            "job_id": job_id,
            "provider": get_provider().name,
            "total_annotations": total_annotations,
            "labelled_tasks": labelled_tasks,
            "unlabelled_tasks": unlabelled_tasks,
            "label_distribution": [
                {
                    "label": label,
                    "count": count,
                    "share": AIService._share(
                        count,
                        total_annotations,
                    )
                    or 0.0,
                }
                for label, count in distribution
            ],
            "agreement_rate": agreement_rate,
            "average_confidence": (
                round(average_confidence, 4) if average_confidence is not None else None
            ),
            "ai_coverage": ai_coverage,
            "duplicate_annotations": duplicate_annotations,
            "flagged_annotations": [
                {
                    "annotation_id": annotation.id,
                    "task_id": annotation.task_id,
                    "label": annotation.label,
                    "quality_score": report.score,
                    "flags": [issue.code for issue in report.issues],
                }
                for annotation, report in flagged[:MAX_FLAGGED]
            ],
            "annotator_stats": [
                {
                    "annotator_id": annotator_id,
                    "annotator_name": (
                        users[annotator_id].name
                        if annotator_id in users
                        else f"User {annotator_id}"
                    ),
                    "annotations": total,
                    "approved": annotator_approved.get(
                        annotator_id,
                        0,
                    ),
                    "agreement_rate": AIService._share(
                        annotator_agreements.get(
                            annotator_id,
                            0,
                        ),
                        annotator_ai.get(annotator_id, 0),
                    ),
                }
                for annotator_id, total in sorted(
                    annotator_totals.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            ],
            "recommendations": AIService.build_recommendations(
                total_annotations=total_annotations,
                unlabelled_tasks=unlabelled_tasks,
                agreement_rate=agreement_rate,
                ai_coverage=ai_coverage,
                flagged_count=len(flagged),
                duplicate_annotations=duplicate_annotations,
                distribution=distribution,
                average_confidence=average_confidence,
            ),
        }

    @staticmethod
    def _share(
        part: int,
        whole: int,
    ) -> float | None:
        """Return ``part`` as a percentage of ``whole``."""
        if whole <= 0:
            return None

        return round(part / whole * 100, 2)

    @staticmethod
    def build_recommendations(
        total_annotations: int,
        unlabelled_tasks: int,
        agreement_rate: float | None,
        ai_coverage: float,
        flagged_count: int,
        duplicate_annotations: int,
        distribution: list[tuple[str, int]],
        average_confidence: float | None = None,
    ) -> list[str]:
        """Turn quality metrics into actionable reviewer recommendations."""
        if total_annotations == 0:
            return [
                (
                    "No annotations have been submitted yet. Start the "
                    "labeling workflow to unlock AI insights."
                )
            ]

        recommendations: list[str] = []

        if unlabelled_tasks > 0:
            recommendations.append(
                f"{unlabelled_tasks} task(s) still have no annotation submitted."
            )

        if flagged_count:
            recommendations.append(
                f"{flagged_count} annotation(s) scored below the quality "
                "threshold and need reviewer attention."
            )

        if agreement_rate is not None and agreement_rate < 70:
            recommendations.append(
                f"Human/AI agreement is {agreement_rate:.1f}% — review the "
                "labeling guidelines or add approved examples."
            )

        if ai_coverage < 50:
            recommendations.append(
                "AI assistance covered less than half of the submissions; "
                "use AI pre-labelling on the remaining tasks."
            )

        if average_confidence is not None and average_confidence < 0.6:
            recommendations.append(
                "Average annotator confidence is low — consider a "
                "second-pass review round."
            )

        if duplicate_annotations:
            recommendations.append(
                f"{duplicate_annotations} duplicate submission(s) detected; "
                "verify annotator effort."
            )

        if distribution and total_annotations >= 10:
            top_label, top_count = distribution[0]
            share = top_count / total_annotations * 100

            if share > 80:
                recommendations.append(
                    f"Label '{top_label}' dominates {share:.1f}% of the "
                    "annotations — confirm the label set is balanced."
                )

            if len(distribution) == 1:
                recommendations.append(
                    "Only one label has been used so far; verify that the "
                    "label set covers the dataset."
                )

        if not recommendations:
            recommendations.append("Quality signals look healthy — no action required.")

        return recommendations
