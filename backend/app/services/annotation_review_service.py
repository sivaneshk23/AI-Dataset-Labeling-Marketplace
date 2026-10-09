"""Business logic for annotation quality review.

A review decision drives the rest of the workflow: it updates the annotation,
moves the task to its next state and closes the labeling job automatically once
every task has been approved.
"""

from sqlalchemy.orm import Session

from backend.app.core.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from backend.app.core.logging import get_logger
from backend.app.core.roles import ADMINISTRATOR
from backend.app.models.annotation_review import AnnotationReview
from backend.app.models.user import User
from backend.app.repositories.annotation_repository import (
    AnnotationRepository,
)
from backend.app.repositories.annotation_review_repository import (
    AnnotationReviewRepository,
)
from backend.app.repositories.labeling_job_repository import LabelingJobRepository
from backend.app.services.annotation_service import AnnotationService
from backend.app.services.annotation_task_service import (
    AnnotationTaskService,
)

logger = get_logger(__name__)

REVIEWABLE_ANNOTATION_STATUSES = (
    "submitted",
    "rejected",
    "needs_revision",
)


class AnnotationReviewService:
    """Business logic for quality review decisions."""

    @staticmethod
    def submit_review(
        db: Session,
        annotation_id: int,
        reviewer: User,
        decision: str,
        comment: str | None = None,
    ) -> AnnotationReview:
        """Record a quality decision and propagate it through the workflow.

        Args:
            db: Active database session.
            annotation_id: Annotation being reviewed.
            reviewer: Authenticated dataset owner or administrator.
            decision: ``approved``, ``rejected`` or ``needs_revision``.
            comment: Optional reviewer feedback.

        Returns:
            The persisted review decision.

        Raises:
            NotFoundError: when the annotation does not exist.
            ConflictError: when the annotation is already approved.
            PermissionDeniedError: when a reviewer reviews their own work.
        """
        annotation = AnnotationService.require_annotation(
            db,
            annotation_id,
        )

        task = AnnotationTaskService.require_task(db, annotation.task_id)
        job = LabelingJobRepository.get_by_id(db, task.job_id)
        if job is None:
            raise NotFoundError("Labeling job not found.")
        if annotation.annotator_id == reviewer.id:
            raise PermissionDeniedError(
                "Reviewers cannot review annotations they submitted themselves."
            )

        if reviewer.role != ADMINISTRATOR and job.created_by != reviewer.id:
            raise PermissionDeniedError("You do not own this labeling job.")

        if annotation.status == "approved":
            raise ConflictError("This annotation has already been approved.")

        if annotation.status not in REVIEWABLE_ANNOTATION_STATUSES:
            raise ConflictError(
                f"An annotation in status '{annotation.status}' cannot "
                "be reviewed again."
            )

        review = AnnotationReview(
            annotation_id=annotation.id,
            reviewer_id=reviewer.id,
            decision=decision,
            comment=(comment or None),
        )

        created = AnnotationReviewRepository.create(db, review)

        annotation.status = decision
        AnnotationRepository.update(db, annotation)

        AnnotationTaskService.apply_review_decision(
            db,
            task,
            decision,
        )
        AnnotationTaskService.complete_job_if_finished(
            db,
            task.job_id,
        )

        logger.info(
            "Annotation %s reviewed as '%s' by user %s.",
            annotation.id,
            decision,
            reviewer.id,
        )

        return created

    @staticmethod
    def get_review(
        db: Session,
        review_id: int,
    ) -> AnnotationReview | None:
        """Return one review or ``None``."""
        return AnnotationReviewRepository.get_by_id(db, review_id)

    @staticmethod
    def require_review(
        db: Session,
        review_id: int,
    ) -> AnnotationReview:
        """Return one review or raise :class:`NotFoundError`."""
        review = AnnotationReviewRepository.get_by_id(
            db,
            review_id,
        )

        if review is None:
            raise NotFoundError("Annotation review not found.")

        return review

    @staticmethod
    def get_reviews(
        db: Session,
    ) -> list[AnnotationReview]:
        """Return every review decision, newest first."""
        return AnnotationReviewRepository.get_all(db)

    @staticmethod
    def get_reviews_for_viewer(db: Session, actor: User) -> list[AnnotationReview]:
        """Return only quality reviews visible to the current manager."""
        reviews = AnnotationReviewRepository.get_all(db)
        if actor.role == ADMINISTRATOR:
            return reviews
        owned_jobs = {
            job.id
            for job in LabelingJobRepository.get_all(db)
            if job.created_by == actor.id
        }
        visible = []
        for review in reviews:
            annotation = AnnotationRepository.get_by_id(db, review.annotation_id)
            if annotation is None:
                continue
            task = AnnotationTaskService.get_task(db, annotation.task_id)
            if task and task.job_id in owned_jobs:
                visible.append(review)
        return visible

    @staticmethod
    def get_reviews_for_annotation(
        db: Session,
        annotation_id: int,
    ) -> list[AnnotationReview]:
        """Return the review history of an annotation."""
        return AnnotationReviewRepository.get_by_annotation(
            db,
            annotation_id,
        )

    @staticmethod
    def get_reviews_for_job(
        db: Session,
        job_id: int,
    ) -> list[AnnotationReview]:
        """Return every review recorded for a labeling job."""
        return AnnotationReviewRepository.get_by_job(db, job_id)

    @staticmethod
    def delete_review(
        db: Session,
        review_id: int,
    ) -> None:
        """Delete a review decision (administrative correction)."""
        review = AnnotationReviewService.require_review(
            db,
            review_id,
        )

        AnnotationReviewRepository.delete(db, review)
