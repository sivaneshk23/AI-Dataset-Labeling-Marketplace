"""Business logic and ownership checks for labeling jobs."""

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError, PermissionDeniedError
from backend.app.core.roles import ADMINISTRATOR, ANNOTATOR
from backend.app.models.labeling_job import LabelingJob
from backend.app.models.user import User
from backend.app.repositories.dataset_repository import DatasetRepository
from backend.app.repositories.labeling_job_repository import LabelingJobRepository


class LabelingJobService:
    """CRUD operations for annotation projects."""

    @staticmethod
    def create_job(
        db: Session,
        dataset_id: int,
        created_by: int,
        title: str,
        description: str,
        status: str = "open",
        annotation_type: str = "single_label_text",
        label_options: list[str] | None = None,
    ) -> LabelingJob:
        """Create a labeling job only under an existing dataset."""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found.")
        if dataset.owner_id not in (None, created_by) and created_by is not None:
            raise PermissionDeniedError("You do not own this dataset.")
        job = LabelingJob(
            dataset_id=dataset_id,
            created_by=created_by,
            title=title.strip(),
            description=description.strip(),
            status=status,
            annotation_type=annotation_type.strip(),
            label_options=label_options or [],
        )
        return LabelingJobRepository.create(db, job)

    @staticmethod
    def get_job(db: Session, job_id: int) -> LabelingJob | None:
        """Return one labeling job or None."""
        return LabelingJobRepository.get_by_id(db, job_id)

    @staticmethod
    def require_manage_access(db: Session, job_id: int, actor: User) -> LabelingJob:
        """Return a job when the actor may manage it."""
        job = LabelingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise NotFoundError("Labeling job not found.")
        if actor.role != ADMINISTRATOR and job.created_by != actor.id:
            raise PermissionDeniedError("You do not own this labeling job.")
        return job

    @staticmethod
    def get_jobs(
        db: Session, actor: User | None = None, status: str | None = None
    ) -> list[LabelingJob]:
        """Return jobs visible to the current role."""
        if actor is None or actor.role == ADMINISTRATOR:
            jobs = LabelingJobRepository.get_all(db)
        elif actor.role == ANNOTATOR:
            jobs = LabelingJobRepository.get_by_worker(db, actor.id)
        else:
            jobs = [
                job
                for job in LabelingJobRepository.get_all(db)
                if job.created_by == actor.id
            ]
        if status is not None:
            jobs = [job for job in jobs if job.status == status]
        return jobs

    @staticmethod
    def get_jobs_for_dataset(db: Session, dataset_id: int) -> list[LabelingJob]:
        """Return every labeling job created for a dataset."""
        return LabelingJobRepository.get_by_dataset(db, dataset_id)

    @staticmethod
    def update_job(
        db: Session,
        job_id: int,
        actor: User | None = None,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        annotation_type: str | None = None,
        label_options: list[str] | None = None,
    ) -> LabelingJob:
        """Update a job after enforcing ownership."""
        job = LabelingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise ValueError("Labeling job not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and job.created_by != actor.id
        ):
            raise PermissionDeniedError("You do not own this labeling job.")
        if title is not None:
            job.title = title.strip()
        if description is not None:
            job.description = description.strip()
        if status is not None:
            job.status = status.strip().lower()
        if annotation_type is not None:
            job.annotation_type = annotation_type.strip()
        if label_options is not None:
            job.label_options = label_options
        return LabelingJobRepository.update(db, job)

    @staticmethod
    def delete_job(db: Session, job_id: int, actor: User | None = None) -> None:
        """Delete a job and dependent workflow records."""
        job = LabelingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise ValueError("Labeling job not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and job.created_by != actor.id
        ):
            raise PermissionDeniedError("You do not own this labeling job.")
        LabelingJobRepository.delete(db, job)
