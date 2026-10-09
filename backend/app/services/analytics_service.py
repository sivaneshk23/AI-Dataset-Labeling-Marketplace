"""Progress tracking and platform analytics.

These aggregates power the dashboard, the per-job progress view and the
documentation screenshots used at Review-II.
"""

from collections import Counter

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.core.text import labels_match
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
from backend.app.repositories.review_repository import (
    ReviewRepository,
)
from backend.app.repositories.user_repository import UserRepository

TASK_APPROVED = "approved"
ANNOTATION_APPROVED = "approved"
ANNOTATION_SUBMITTED = "submitted"


class AnalyticsService:
    """Aggregated progress and workload statistics."""

    @staticmethod
    def job_progress(
        db: Session,
        job_id: int,
    ) -> dict:
        """Return a progress snapshot for one labeling job.

        Raises:
            NotFoundError: when the labeling job does not exist.
        """
        job = LabelingJobRepository.get_by_id(db, job_id)

        if job is None:
            raise NotFoundError("Labeling job not found.")

        dataset = DatasetRepository.get_by_id(
            db,
            job.dataset_id,
        )

        tasks = AnnotationTaskRepository.get_by_job(db, job_id)
        task_counts = AnnotationTaskRepository.status_counts(
            db,
            job_id,
        )
        annotations = AnnotationRepository.get_by_job(db, job_id)
        annotation_counts = AnnotationRepository.status_counts(
            db,
            job_id,
        )

        total_tasks = len(tasks)
        approved_tasks = task_counts.get(TASK_APPROVED, 0)
        submitted_tasks = task_counts.get("submitted", 0)
        rejected_tasks = task_counts.get("rejected", 0)
        open_tasks = max(
            0,
            total_tasks - approved_tasks - submitted_tasks,
        )

        total_annotations = len(annotations)
        pending_reviews = annotation_counts.get(
            ANNOTATION_SUBMITTED,
            0,
        )

        confidences = [
            annotation.confidence
            for annotation in annotations
            if annotation.confidence is not None
        ]

        ai_suggestions = [
            annotation for annotation in annotations if annotation.ai_suggested_label
        ]
        ai_agreements = sum(
            1
            for annotation in ai_suggestions
            if labels_match(
                annotation.label,
                annotation.ai_suggested_label,
            )
        )

        ratings = [
            review.rating
            for review in ReviewRepository.get_by_job(db, job_id)
            if review.rating is not None
        ]

        return {
            "job_id": job.id,
            "job_title": job.title,
            "job_status": job.status,
            "dataset_id": job.dataset_id,
            "dataset_title": (
                dataset.title if dataset is not None else "Unknown dataset"
            ),
            "total_tasks": total_tasks,
            "tasks_by_status": task_counts,
            "open_tasks": open_tasks,
            "submitted_tasks": submitted_tasks,
            "approved_tasks": approved_tasks,
            "rejected_tasks": rejected_tasks,
            "total_annotations": total_annotations,
            "annotations_by_status": annotation_counts,
            "pending_reviews": pending_reviews,
            "completion_percentage": AnalyticsService._percentage(
                approved_tasks,
                total_tasks,
            ),
            "approval_rate": AnalyticsService._percentage(
                annotation_counts.get(ANNOTATION_APPROVED, 0),
                total_annotations,
            ),
            "average_confidence": (
                round(sum(confidences) / len(confidences), 4) if confidences else None
            ),
            "average_rating": (
                round(sum(ratings) / len(ratings), 2) if ratings else None
            ),
            "assigned_annotators": len(
                {task.assigned_to for task in tasks if task.assigned_to is not None}
            ),
            "ai_suggestions_used": len(ai_suggestions),
            "ai_agreement_rate": (
                AnalyticsService._percentage(
                    ai_agreements,
                    len(ai_suggestions),
                )
                if ai_suggestions
                else None
            ),
        }

    @staticmethod
    def platform_summary(
        db: Session,
    ) -> dict:
        """Return platform wide statistics for the dashboard."""
        users = UserRepository.get_all(db)
        roles = Counter(user.role for user in users)

        datasets = DatasetRepository.get_all(db)
        jobs = LabelingJobRepository.get_all(db)
        job_statuses = Counter(job.status for job in jobs)

        task_counts = AnnotationTaskRepository.status_counts(db)
        annotation_counts = AnnotationRepository.status_counts(db)

        annotations = AnnotationRepository.get_all(db)

        ai_suggestions = [
            annotation for annotation in annotations if annotation.ai_suggested_label
        ]
        ai_agreements = sum(
            1
            for annotation in ai_suggestions
            if labels_match(
                annotation.label,
                annotation.ai_suggested_label,
            )
        )

        total_tasks = sum(task_counts.values())
        total_annotations = sum(annotation_counts.values())

        return {
            "total_users": len(users),
            "users_by_role": dict(roles),
            "total_datasets": len(datasets),
            "total_jobs": len(jobs),
            "jobs_by_status": dict(job_statuses),
            "active_jobs": sum(
                1
                for job in jobs
                if job.status not in {"completed", "closed", "archived"}
            ),
            "completed_jobs": job_statuses.get("completed", 0),
            "total_tasks": total_tasks,
            "tasks_by_status": task_counts,
            "open_tasks": max(
                0,
                total_tasks - task_counts.get(TASK_APPROVED, 0),
            ),
            "total_annotations": total_annotations,
            "annotations_by_status": annotation_counts,
            "pending_reviews": annotation_counts.get(
                ANNOTATION_SUBMITTED,
                0,
            ),
            "total_reviews": ReviewRepository.count_all(db),
            "review_decisions": AnnotationReviewRepository.decision_counts(db),
            "annotation_completion_percentage": (
                AnalyticsService._percentage(
                    task_counts.get(TASK_APPROVED, 0),
                    total_tasks,
                )
            ),
            "ai_suggestions_used": len(ai_suggestions),
            "ai_agreement_rate": (
                AnalyticsService._percentage(
                    ai_agreements,
                    len(ai_suggestions),
                )
                if ai_suggestions
                else None
            ),
        }

    @staticmethod
    def _percentage(
        part: int,
        whole: int,
    ) -> float:
        """Return ``part`` as a rounded percentage of ``whole``."""
        if whole <= 0:
            return 0.0

        return round(part / whole * 100, 2)
