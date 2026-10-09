"""Business logic for annotation submission.

Whenever a label is submitted the service:

1. validates the workflow rules (task ownership, task state, label quality),
2. asks the AI enhancement for a pre-label suggestion so human/AI agreement can
   be measured, and
3. stores the annotation and moves the task into the ``submitted`` state.
"""

from sqlalchemy.orm import Session

from backend.app.core.errors import (
    ConflictError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from backend.app.core.logging import get_logger
from backend.app.core.roles import (
    ADMINISTRATOR,
    ANNOTATOR,
    DATASET_OWNER,
)
from backend.app.models.annotation import Annotation
from backend.app.models.user import User
from backend.app.repositories.annotation_repository import (
    AnnotationRepository,
)
from backend.app.repositories.annotation_task_repository import AnnotationTaskRepository
from backend.app.repositories.labeling_job_repository import LabelingJobRepository
from backend.app.services.ai_service import AIService
from backend.app.services.annotation_task_service import (
    AnnotationTaskService,
)

logger = get_logger(__name__)

RESUBMITTABLE_TASK_STATUSES = (
    "pending",
    "in_progress",
    "rejected",
)

MIN_LABEL_LENGTH = 2
REVIEWER_ROLES = (
    DATASET_OWNER,
    ADMINISTRATOR,
)


class AnnotationService:
    """Business logic for submitted annotations."""

    @staticmethod
    def submit_annotation(
        db: Session,
        task_id: int,
        annotator: User,
        label: str,
        notes: str | None = None,
        confidence: float | None = None,
    ) -> Annotation:
        """Submit a label for an annotation task.

        Args:
            db: Active database session.
            task_id: Task receiving the label.
            annotator: Authenticated annotator.
            label: Submitted label.
            notes: Optional reviewer notes.
            confidence: Optional annotator confidence between 0 and 1.

        Returns:
            The persisted annotation.

        Raises:
            NotFoundError: when the task does not exist.
            PermissionDeniedError: when the user may not work on the task.
            InvalidStateError: when the task is not awaiting an annotation.
            ValidationError: when the label is not usable.
        """
        task = AnnotationTaskService.require_task(db, task_id)

        AnnotationService._validate_submission(
            task,
            annotator,
            label,
        )

        suggestion = AIService.suggest_label(
            db,
            task.job_id,
            task.input_text,
        )

        annotation = Annotation(
            task_id=task.id,
            annotator_id=annotator.id,
            label=" ".join(label.split()).strip(),
            notes=(notes or None),
            confidence=confidence,
            ai_suggested_label=suggestion.label or None,
            ai_confidence=(suggestion.confidence if suggestion.label else None),
            status="submitted",
        )

        created = AnnotationRepository.create(db, annotation)

        if task.assigned_to is None:
            task.assigned_to = annotator.id

        AnnotationTaskService.mark_submitted(db, task)

        logger.info(
            "Annotation %s submitted for task %s by user %s.",
            created.id,
            task.id,
            annotator.id,
        )

        return created

    @staticmethod
    def get_annotation(
        db: Session,
        annotation_id: int,
    ) -> Annotation | None:
        """Return one annotation or ``None``."""
        return AnnotationRepository.get_by_id(db, annotation_id)

    @staticmethod
    def require_annotation(
        db: Session,
        annotation_id: int,
    ) -> Annotation:
        """Return one annotation or raise :class:`NotFoundError`."""
        annotation = AnnotationRepository.get_by_id(
            db,
            annotation_id,
        )

        if annotation is None:
            raise NotFoundError("Annotation not found.")

        return annotation

    @staticmethod
    def get_annotations_for_viewer(
        db: Session,
        current_user: User,
        job_id: int | None = None,
    ) -> list[Annotation]:
        """Return the annotations a role is allowed to see."""
        if current_user.role == ANNOTATOR:
            return AnnotationRepository.get_by_annotator(
                db,
                current_user.id,
            )

        if current_user.role == ADMINISTRATOR:
            if job_id is not None:
                return AnnotationRepository.get_by_job(db, job_id)
            return AnnotationRepository.get_all(db)

        annotations = AnnotationRepository.get_all(db)
        owned_job_ids = {
            job.id
            for job in LabelingJobRepository.get_all(db)
            if job.created_by == current_user.id
        }
        annotations = [
            annotation
            for annotation in annotations
            if annotation.task_id
            in {
                task.id
                for task in AnnotationTaskRepository.get_all(db)
                if task.job_id in owned_job_ids
            }
        ]
        if job_id is not None:
            task_ids = {
                task.id for task in AnnotationTaskRepository.get_by_job(db, job_id)
            }
            annotations = [
                annotation
                for annotation in annotations
                if annotation.task_id in task_ids
            ]
        return annotations

    @staticmethod
    def get_annotations_for_job(
        db: Session,
        job_id: int,
    ) -> list[Annotation]:
        """Return every annotation recorded for a labeling job."""
        return AnnotationRepository.get_by_job(db, job_id)

    @staticmethod
    def get_annotations_for_task(
        db: Session,
        task_id: int,
    ) -> list[Annotation]:
        """Return the annotation history of a task."""
        return AnnotationRepository.get_by_task(db, task_id)

    @staticmethod
    def update_annotation(
        db: Session,
        annotation_id: int,
        current_user: User,
        label: str | None = None,
        notes: str | None = None,
        confidence: float | None = None,
    ) -> Annotation:
        """Revise a previously submitted annotation."""
        annotation = AnnotationService.require_annotation(
            db,
            annotation_id,
        )

        if annotation.status == "approved":
            raise ConflictError(
                "Approved annotations are immutable because the label is "
                "already part of the exported dataset."
            )

        AnnotationService._require_modify_permission(
            annotation,
            current_user,
        )

        if label is not None:
            cleaned = " ".join(label.split()).strip()

            if len(cleaned) < MIN_LABEL_LENGTH:
                raise ValidationError(
                    f"label must contain at least {MIN_LABEL_LENGTH} characters."
                )

            annotation.label = cleaned

        if notes is not None:
            annotation.notes = notes.strip() or None

        if confidence is not None:
            annotation.confidence = confidence

        annotation.status = "submitted"

        updated = AnnotationRepository.update(db, annotation)

        task = AnnotationTaskService.require_task(
            db,
            annotation.task_id,
        )

        AnnotationTaskService.mark_submitted(db, task)

        return updated

    @staticmethod
    def delete_annotation(
        db: Session,
        annotation_id: int,
        current_user: User,
    ) -> None:
        """Withdraw an annotation that has not been approved yet."""
        annotation = AnnotationService.require_annotation(
            db,
            annotation_id,
        )

        if annotation.status == "approved":
            raise ConflictError("Approved annotations cannot be deleted.")

        AnnotationService._require_modify_permission(
            annotation,
            current_user,
        )

        task = AnnotationTaskService.require_task(
            db,
            annotation.task_id,
        )

        AnnotationRepository.delete(db, annotation)

        if task.status in ("submitted", "approved"):
            task.status = "in_progress"
            AnnotationTaskService.update_task(db, task.id)

    @staticmethod
    def _validate_submission(
        task,
        annotator: User,
        label: str,
    ) -> None:
        """Validate that the annotator may submit this label."""
        if annotator.role != ANNOTATOR:
            raise PermissionDeniedError("Only annotator accounts can submit labels.")

        if not annotator.is_active:
            raise PermissionDeniedError(
                "Your account is inactive and cannot submit labels."
            )

        if task.assigned_to is not None and task.assigned_to != annotator.id:
            raise PermissionDeniedError("This task is assigned to another annotator.")

        if task.status not in RESUBMITTABLE_TASK_STATUSES:
            raise InvalidStateError(
                f"The task is currently '{task.status}' and cannot "
                "receive a new annotation."
            )

        cleaned = " ".join(str(label or "").split()).strip()

        if len(cleaned) < MIN_LABEL_LENGTH:
            raise ValidationError(
                f"label must contain at least {MIN_LABEL_LENGTH} characters."
            )

    @staticmethod
    def _require_modify_permission(
        annotation: Annotation,
        current_user: User,
    ) -> None:
        """Allow reviewers or the owning annotator to modify a label."""
        if current_user.role in REVIEWER_ROLES:
            return

        if annotation.annotator_id == current_user.id:
            return

        raise PermissionDeniedError("You can only modify your own annotations.")
