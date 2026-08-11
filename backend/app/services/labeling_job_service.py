from sqlalchemy.orm import Session

from backend.app.models.labeling_job import LabelingJob
from backend.app.repositories.labeling_job_repository import (
    LabelingJobRepository,
)
from backend.app.repositories.dataset_repository import (
    DatasetRepository,
)


class LabelingJobService:

    @staticmethod
    def create_job(
        db: Session,
        dataset_id: int,
        created_by: int,
        title: str,
        description: str,
        status: str = "open",
    ) -> LabelingJob:

        dataset = DatasetRepository.get_by_id(
            db,
            dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        job = LabelingJob(
            dataset_id=dataset_id,
            created_by=created_by,
            title=title,
            description=description,
            status=status,
        )

        return LabelingJobRepository.create(
            db,
            job,
        )

    @staticmethod
    def get_job(
        db: Session,
        job_id: int,
    ) -> LabelingJob | None:
        return LabelingJobRepository.get_by_id(
            db,
            job_id,
        )

    @staticmethod
    def get_jobs(
        db: Session,
    ) -> list[LabelingJob]:
        return LabelingJobRepository.get_all(db)

    @staticmethod
    def update_job(
        db: Session,
        job_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> LabelingJob:

        job = LabelingJobRepository.get_by_id(
            db,
            job_id,
        )

        if job is None:
            raise ValueError(
                "Labeling job not found."
            )

        if title is not None:
            job.title = title

        if description is not None:
            job.description = description

        if status is not None:
            job.status = status

        return LabelingJobRepository.update(
            db,
            job,
        )

    @staticmethod
    def delete_job(
        db: Session,
        job_id: int,
    ) -> None:

        job = LabelingJobRepository.get_by_id(
            db,
            job_id,
        )

        if job is None:
            raise ValueError(
                "Labeling job not found."
            )

        LabelingJobRepository.delete(
            db,
            job,
        )