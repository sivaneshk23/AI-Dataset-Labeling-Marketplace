"""Export of completed labeled datasets.

The platform exports one row per annotation so the file can be joined with the
original records or handed to a model training pipeline. CSV is used because it
opens directly in Excel and pandas without extra dependencies.
"""

import csv
import re
from io import StringIO

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError, PermissionDeniedError
from backend.app.core.roles import ADMINISTRATOR
from backend.app.models.user import User
from backend.app.repositories.annotation_repository import (
    AnnotationRepository,
)
from backend.app.repositories.annotation_review_repository import (
    AnnotationReviewRepository,
)
from backend.app.repositories.annotation_task_repository import (
    AnnotationTaskRepository,
)
from backend.app.repositories.dataset_repository import (
    DatasetRepository,
)
from backend.app.repositories.labeling_job_repository import (
    LabelingJobRepository,
)
from backend.app.repositories.user_repository import UserRepository

EXPORT_COLUMNS = (
    "task_id",
    "job_id",
    "job_title",
    "dataset_id",
    "dataset_title",
    "input_text",
    "label",
    "annotation_status",
    "annotator_id",
    "annotator_name",
    "annotator_confidence",
    "ai_suggested_label",
    "ai_confidence",
    "ai_agreement",
    "review_decision",
    "review_comment",
    "submitted_at",
)

APPROVED_ONLY_STATUS = ("approved",)


class ExportService:
    """Build labeled dataset exports for jobs and datasets."""

    @staticmethod
    def build_job_export(
        db: Session,
        job_id: int,
        include_unapproved: bool = False,
        actor: User | None = None,
    ) -> tuple[str, list[dict]]:
        """Build the export rows for one labeling job.

        Returns:
            A ``(filename, rows)`` tuple.

        Raises:
            NotFoundError: when the labeling job does not exist.
        """
        job = LabelingJobRepository.get_by_id(db, job_id)

        if job is None:
            raise NotFoundError("Labeling job not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and job.created_by != actor.id
        ):
            raise PermissionDeniedError("You do not own this labeling job.")

        dataset = DatasetRepository.get_by_id(db, job.dataset_id)

        rows = ExportService._rows_for_job(
            db,
            job,
            dataset,
            include_unapproved,
        )

        return (
            ExportService.build_filename(job.title),
            rows,
        )

    @staticmethod
    def build_dataset_export(
        db: Session,
        dataset_id: int,
        include_unapproved: bool = False,
        actor: User | None = None,
    ) -> tuple[str, list[dict]]:
        """Build the export rows for every job of a dataset.

        Raises:
            NotFoundError: when the dataset does not exist.
        """
        dataset = DatasetRepository.get_by_id(db, dataset_id)

        if dataset is None:
            raise NotFoundError("Dataset not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and dataset.owner_id not in (None, actor.id)
        ):
            raise PermissionDeniedError("You do not own this dataset.")

        jobs = LabelingJobRepository.get_by_dataset(db, dataset_id)

        rows: list[dict] = []

        for job in jobs:
            rows.extend(
                ExportService._rows_for_job(
                    db,
                    job,
                    dataset,
                    include_unapproved,
                )
            )

        return (
            ExportService.build_filename(dataset.title),
            rows,
        )

    @staticmethod
    def to_csv(rows: list[dict]) -> str:
        """Serialise export rows into CSV text."""
        buffer = StringIO()

        writer = csv.DictWriter(
            buffer,
            fieldnames=list(EXPORT_COLUMNS),
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)

        return buffer.getvalue()

    @staticmethod
    def build_filename(title: str) -> str:
        """Create a safe CSV file name from a dataset or job title."""
        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            str(title).strip().lower(),
        ).strip("-")

        return f"{(slug or 'export')}-annotations.csv"

    @staticmethod
    def _rows_for_job(
        db: Session,
        job,
        dataset,
        include_unapproved: bool,
    ) -> list[dict]:
        """Map the annotations of one job into export rows."""
        tasks = {
            task.id: task
            for task in AnnotationTaskRepository.get_by_job(
                db,
                job.id,
            )
        }

        users = {user.id: user for user in UserRepository.get_all(db)}

        rows: list[dict] = []

        for annotation in AnnotationRepository.get_by_job(db, job.id):
            if not include_unapproved and annotation.status not in APPROVED_ONLY_STATUS:
                continue

            task = tasks.get(annotation.task_id)

            if task is None:
                continue

            review = AnnotationReviewRepository.get_latest_by_annotation(
                db,
                annotation.id,
            )

            rows.append(
                {
                    "task_id": annotation.task_id,
                    "job_id": job.id,
                    "job_title": job.title,
                    "dataset_id": job.dataset_id,
                    "dataset_title": (
                        dataset.title if dataset is not None else "Unknown dataset"
                    ),
                    "input_text": task.input_text,
                    "label": annotation.label,
                    "annotation_status": annotation.status,
                    "annotator_id": annotation.annotator_id,
                    "annotator_name": (
                        users[annotation.annotator_id].name
                        if annotation.annotator_id in users
                        else f"User {annotation.annotator_id}"
                    ),
                    "annotator_confidence": (
                        annotation.confidence
                        if annotation.confidence is not None
                        else ""
                    ),
                    "ai_suggested_label": (annotation.ai_suggested_label or ""),
                    "ai_confidence": (
                        annotation.ai_confidence
                        if annotation.ai_confidence is not None
                        else ""
                    ),
                    "ai_agreement": (
                        ""
                        if not annotation.ai_suggested_label
                        else (
                            str(
                                annotation.label.strip().lower()
                                == annotation.ai_suggested_label.strip().lower()
                            )
                        )
                    ),
                    "review_decision": (review.decision if review is not None else ""),
                    "review_comment": (
                        (review.comment or "") if review is not None else ""
                    ),
                    "submitted_at": annotation.created_at.isoformat(
                        sep=" ",
                        timespec="seconds",
                    ),
                }
            )

        return rows
