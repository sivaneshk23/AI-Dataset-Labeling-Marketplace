from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.job_assignment import JobAssignment
from backend.app.models.labeling_job import LabelingJob


class LabelingJobRepository:
    """Repository for labeling job persistence."""

    @staticmethod
    def create(
        db: Session,
        job: LabelingJob,
    ) -> LabelingJob:
        """Persist and return a labeling job."""
        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_by_id(
        db: Session,
        job_id: int,
    ) -> LabelingJob | None:
        """Return a labeling job by identifier."""
        statement = select(LabelingJob).where(LabelingJob.id == job_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[LabelingJob]:
        """Return all labeling jobs ordered newest first."""
        statement = select(LabelingJob).order_by(LabelingJob.id.desc())

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_worker(db: Session, worker_id: int) -> list[LabelingJob]:
        """Return jobs assigned to one annotator."""
        statement = (
            select(LabelingJob)
            .join(JobAssignment, JobAssignment.job_id == LabelingJob.id)
            .where(JobAssignment.worker_id == worker_id)
            .order_by(LabelingJob.id.desc())
            .distinct()
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def get_by_dataset(
        db: Session,
        dataset_id: int,
    ) -> list[LabelingJob]:
        """Return jobs belonging to a dataset."""
        statement = select(LabelingJob).where(LabelingJob.dataset_id == dataset_id)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def update(
        db: Session,
        job: LabelingJob,
    ) -> LabelingJob:
        """Persist changes to a labeling job."""
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def delete(
        db: Session,
        job: LabelingJob,
    ) -> None:
        """Delete a labeling job."""
        db.delete(job)
        db.commit()
