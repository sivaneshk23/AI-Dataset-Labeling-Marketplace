"""Business logic for annotation tasks.

Tasks are the unit of work of the marketplace. This service enforces the
workflow rules: a job must exist and be open, work can only be assigned to
active annotators, and status transitions follow a defined state machine.
"""

from sqlalchemy.orm import Session

from backend.app.core.errors import (
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationError,
)
from backend.app.core.logging import get_logger
from backend.app.core.roles import ADMINISTRATOR, ANNOTATOR
from backend.app.core.text import normalise_label
from backend.app.models.annotation_task import (
    OPEN_TASK_STATUSES,
    AnnotationTask,
)
from backend.app.models.user import User
from backend.app.repositories.annotation_task_repository import (
    AnnotationTaskRepository,
)
from backend.app.repositories.labeling_job_repository import (
    LabelingJobRepository,
)
from backend.app.repositories.user_repository import UserRepository

logger = get_logger(__name__)

MAX_BULK_ITEMS = 500
BLOCKED_JOB_STATUSES = (
    "closed",
    "archived",
)

# Allowed manual status transitions for dataset owners/administrators.
MANUAL_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "pending": ("pending", "in_progress"),
    "in_progress": ("pending", "in_progress"),
    "submitted": ("in_progress",),
    "approved": ("in_progress",),
    "rejected": ("pending", "in_progress"),
}

# Mapping between a quality review decision and the resulting task status.
REVIEW_DECISION_TO_TASK_STATUS = {
    "approved": "approved",
    "rejected": "rejected",
    "needs_revision": "in_progress",
}


class AnnotationTaskService:
    """Business logic for annotation tasks."""

    @staticmethod
    def create_task(
        db: Session,
        job_id: int,
        input_text: str,
        assigned_to: int | None = None,
        dataset_record_id: int | None = None,
    ) -> AnnotationTask:
        """Create a single annotation task.

        Args:
            db: Active database session.
            job_id: Parent labeling job.
            input_text: Record to annotate.
            assigned_to: Optional annotator to assign immediately.

        Returns:
            The persisted annotation task.

        Raises:
            NotFoundError: when the job or assignee does not exist.
            ValidationError: when the record is empty.
            InvalidStateError: when the job no longer accepts new tasks.
        """
        AnnotationTaskService._require_open_job(db, job_id)

        cleaned_text = (input_text or "").strip()

        if not cleaned_text:
            raise ValidationError("input_text must not be empty.")

        task = AnnotationTask(
            job_id=job_id,
            dataset_record_id=dataset_record_id,
            assigned_to=assigned_to,
            input_text=cleaned_text,
            status="pending",
        )

        if assigned_to is not None:
            AnnotationTaskService._require_annotator(
                db,
                assigned_to,
            )

        created = AnnotationTaskRepository.create(db, task)

        logger.info(
            "Annotation task %s created for job %s.",
            created.id,
            job_id,
        )

        return created

    @staticmethod
    def create_tasks_bulk(
        db: Session,
        job_id: int,
        items: list[str],
        assigned_to: int | None = None,
        skip_duplicates: bool = True,
    ) -> list[AnnotationTask]:
        """Create several annotation tasks in one transaction."""
        AnnotationTaskService._require_open_job(db, job_id)

        if not items:
            raise ValidationError("At least one record is required.")

        if len(items) > MAX_BULK_ITEMS:
            raise ValidationError(
                f"A maximum of {MAX_BULK_ITEMS} records can be created at once."
            )

        existing = {
            normalise_label(task.input_text)
            for task in AnnotationTaskRepository.get_by_job(db, job_id)
        }

        tasks: list[AnnotationTask] = []
        seen: set[str] = set()

        for item in items:
            cleaned = " ".join(str(item or "").split())

            if not cleaned:
                continue

            signature = normalise_label(cleaned)

            if skip_duplicates and (signature in existing or signature in seen):
                continue

            seen.add(signature)

            tasks.append(
                AnnotationTask(
                    job_id=job_id,
                    assigned_to=assigned_to,
                    input_text=cleaned,
                    status="pending",
                )
            )

        if assigned_to is not None:
            AnnotationTaskService._require_annotator(
                db,
                assigned_to,
            )

        if not tasks:
            raise ValidationError(
                "No new records were provided; every item already exists in this job."
            )

        created = AnnotationTaskRepository.create_many(db, tasks)

        logger.info(
            "%s annotation task(s) created for job %s.",
            len(created),
            job_id,
        )

        return created

    @staticmethod
    def create_tasks_from_dataset_records(
        db: Session,
        job_id: int,
        records: list,
        assigned_to: int | None = None,
    ) -> list[AnnotationTask]:
        """Create one task per imported source record without collapsing duplicates."""
        AnnotationTaskService._require_open_job(db, job_id)
        if not records:
            raise ValidationError("No uploaded dataset records are available.")
        if len(records) > 1000:
            raise ValidationError(
                "A maximum of 1000 uploaded records can be imported at once."
            )
        if assigned_to is not None:
            AnnotationTaskService._require_annotator(db, assigned_to)

        existing_record_ids = {
            task.dataset_record_id
            for task in AnnotationTaskRepository.get_by_job(db, job_id)
            if task.dataset_record_id is not None
        }
        tasks: list[AnnotationTask] = []
        for record in records:
            if record.id in existing_record_ids:
                continue
            tasks.append(
                AnnotationTask(
                    job_id=job_id,
                    dataset_record_id=record.id,
                    assigned_to=assigned_to,
                    input_text=record.input_text,
                    status="pending",
                )
            )
        if not tasks:
            raise ValidationError(
                "Every selected dataset record is already imported into this job."
            )
        return AnnotationTaskRepository.create_many(db, tasks)

    @staticmethod
    def get_task(
        db: Session,
        task_id: int,
    ) -> AnnotationTask | None:
        """Return one task or ``None``."""
        return AnnotationTaskRepository.get_by_id(db, task_id)

    @staticmethod
    def require_task(
        db: Session,
        task_id: int,
    ) -> AnnotationTask:
        """Return one task or raise :class:`NotFoundError`."""
        task = AnnotationTaskRepository.get_by_id(db, task_id)

        if task is None:
            raise NotFoundError("Annotation task not found.")

        return task

    @staticmethod
    def get_tasks(
        db: Session,
        job_id: int | None = None,
    ) -> list[AnnotationTask]:
        """Return tasks, optionally limited to one labeling job."""
        return AnnotationTaskRepository.get_all(
            db,
            job_id=job_id,
        )

    @staticmethod
    def get_tasks_for_job(
        db: Session,
        job_id: int,
    ) -> list[AnnotationTask]:
        """Return every task of a labeling job."""
        AnnotationTaskService._require_job(db, job_id)

        return AnnotationTaskRepository.get_by_job(db, job_id)

    @staticmethod
    def get_tasks_for_viewer(
        db: Session,
        current_user: User,
        job_id: int | None = None,
    ) -> list[AnnotationTask]:
        """Return the tasks a role is allowed to see.

        Annotators only ever see the tasks assigned to them, while dataset
        owners and administrators see the complete workload.
        """
        if current_user.role == ANNOTATOR:
            tasks = AnnotationTaskRepository.get_by_assignee(
                db,
                current_user.id,
            )

            if job_id is not None:
                tasks = [task for task in tasks if task.job_id == job_id]

            return tasks

        tasks = AnnotationTaskService.get_tasks(db, job_id)
        if current_user.role == ADMINISTRATOR:
            return tasks
        owned_job_ids = {
            job.id
            for job in LabelingJobRepository.get_all(db)
            if job.created_by == current_user.id
        }
        return [task for task in tasks if task.job_id in owned_job_ids]

    @staticmethod
    def assign_task(
        db: Session,
        task_id: int,
        assigned_to: int,
    ) -> AnnotationTask:
        """Assign a task to an annotator."""
        task = AnnotationTaskService.require_task(db, task_id)

        if task.status == "approved":
            raise InvalidStateError("An approved task can no longer be reassigned.")

        AnnotationTaskService._require_annotator(db, assigned_to)

        task.assigned_to = assigned_to

        if task.status == "pending":
            task.status = "in_progress"

        updated = AnnotationTaskRepository.update(db, task)

        logger.info(
            "Annotation task %s assigned to user %s.",
            task_id,
            assigned_to,
        )

        return updated

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        input_text: str | None = None,
        status: str | None = None,
        assigned_to: int | None = None,
    ) -> AnnotationTask:
        """Update the record, assignment or status of a task."""
        task = AnnotationTaskService.require_task(db, task_id)

        if input_text is not None:
            cleaned = input_text.strip()

            if not cleaned:
                raise ValidationError("input_text must not be empty.")

            task.input_text = cleaned

        if assigned_to is not None:
            AnnotationTaskService._require_annotator(
                db,
                assigned_to,
            )

            task.assigned_to = assigned_to

        if status is not None and status != task.status:
            AnnotationTaskService._validate_transition(
                task.status,
                status,
            )

            task.status = status

        return AnnotationTaskRepository.update(db, task)

    @staticmethod
    def mark_submitted(
        db: Session,
        task: AnnotationTask,
    ) -> AnnotationTask:
        """Move a task to the ``submitted`` state after a label arrives."""
        task.status = "submitted"

        return AnnotationTaskRepository.update(db, task)

    @staticmethod
    def apply_review_decision(
        db: Session,
        task: AnnotationTask,
        decision: str,
    ) -> AnnotationTask:
        """Apply a quality review decision to the underlying task."""
        task.status = REVIEW_DECISION_TO_TASK_STATUS.get(
            decision,
            task.status,
        )

        return AnnotationTaskRepository.update(db, task)

    @staticmethod
    def complete_job_if_finished(
        db: Session,
        job_id: int,
    ) -> bool:
        """Mark a job completed when every task has been approved.

        Returns:
            True when the job status changed to ``completed``.
        """
        tasks = AnnotationTaskRepository.get_by_job(db, job_id)
        job = LabelingJobRepository.get_by_id(db, job_id)

        if job is None or not tasks:
            return False

        if any(task.status != "approved" for task in tasks):
            return False

        if job.status == "completed":
            return False

        job.status = "completed"
        LabelingJobRepository.update(db, job)

        logger.info(
            "Labeling job %s completed; all tasks approved.",
            job_id,
        )

        return True

    @staticmethod
    def delete_task(
        db: Session,
        task_id: int,
    ) -> None:
        """Delete a task that has not been approved yet."""
        task = AnnotationTaskService.require_task(db, task_id)

        if task.status == "approved":
            raise ConflictError(
                "Approved tasks cannot be deleted because the label is "
                "part of the exported dataset."
            )

        AnnotationTaskRepository.delete(db, task)

    @staticmethod
    def get_open_tasks_for_annotator(
        db: Session,
        user_id: int,
    ) -> list[AnnotationTask]:
        """Return the not-yet-approved tasks assigned to an annotator."""
        return AnnotationTaskRepository.get_by_assignee(
            db,
            user_id,
            statuses=OPEN_TASK_STATUSES,
        )

    @staticmethod
    def _require_job(
        db: Session,
        job_id: int,
    ) -> None:
        """Raise :class:`NotFoundError` when the job is missing."""
        if LabelingJobRepository.get_by_id(db, job_id) is None:
            raise NotFoundError("Labeling job not found.")

    @staticmethod
    def _require_open_job(
        db: Session,
        job_id: int,
    ) -> None:
        """Ensure the job exists and still accepts new work."""
        job = LabelingJobRepository.get_by_id(db, job_id)

        if job is None:
            raise NotFoundError("Labeling job not found.")

        if job.status in BLOCKED_JOB_STATUSES:
            raise InvalidStateError(
                f"Labeling job is {job.status} and no longer accepts new tasks."
            )

    @staticmethod
    def _require_annotator(
        db: Session,
        user_id: int,
    ) -> User:
        """Ensure the user exists, is active and can annotate."""
        user = UserRepository.get_by_id(db, user_id)

        if user is None:
            raise NotFoundError("Annotator not found.")

        if not user.is_active:
            raise ValidationError("The selected annotator account is inactive.")

        if user.role != ANNOTATOR:
            raise ValidationError(
                "Only users with the annotator role can be assigned annotation tasks."
            )

        return user

    @staticmethod
    def _validate_transition(
        current_status: str,
        requested_status: str,
    ) -> None:
        """Validate a manual task status transition."""
        allowed = MANUAL_TRANSITIONS.get(current_status, ())

        if requested_status not in allowed:
            raise InvalidStateError(
                f"A task in status '{current_status}' cannot be moved to "
                f"'{requested_status}'. Allowed: "
                + (", ".join(allowed) if allowed else "none")
                + "."
            )
