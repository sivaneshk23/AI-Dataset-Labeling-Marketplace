from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.labeling_job import LabelingJob


class LabelingJobRepository:

    @staticmethod
    def create(
        db: Session,
        job: LabelingJob,
    ) -> LabelingJob:
        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_by_id(
        db: Session,
        job_id: int,
    ) -> LabelingJob | None:
        statement = select(LabelingJob).where(
            LabelingJob.id == job_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[LabelingJob]:
        statement = select(LabelingJob).order_by(
            LabelingJob.id.desc()
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def get_by_dataset(
        db: Session,
        dataset_id: int,
    ) -> list[LabelingJob]:
        statement = select(LabelingJob).where(
            LabelingJob.dataset_id == dataset_id
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def update(
        db: Session,
        job: LabelingJob,
    ) -> LabelingJob:
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def delete(
        db: Session,
        job: LabelingJob,
    ) -> None:
        db.delete(job)
        db.commit()