"""Business rules for turning uploaded dataset records into tasks."""

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError, PermissionDeniedError
from backend.app.core.roles import ADMINISTRATOR
from backend.app.models.user import User
from backend.app.repositories.dataset_record_repository import DatasetRecordRepository
from backend.app.repositories.dataset_repository import DatasetRepository
from backend.app.services.annotation_task_service import AnnotationTaskService
from backend.app.services.labeling_job_service import LabelingJobService


class DatasetRecordService:
    """Read imported records and safely create annotation tasks from them."""

    @staticmethod
    def import_to_job(
        db: Session,
        dataset_id: int,
        job_id: int,
        actor: User,
        assigned_to: int | None = None,
        limit: int = 1000,
        offset: int = 0,
        skip_duplicates: bool = True,
    ) -> list:
        """Create tasks from uploaded records belonging to the target job."""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found.")
        if actor.role != ADMINISTRATOR and dataset.owner_id not in (None, actor.id):
            raise PermissionDeniedError("You do not own this dataset.")

        job = LabelingJobService.get_job(db, job_id)
        if job is None:
            raise NotFoundError("Labeling job not found.")
        if job.dataset_id != dataset_id:
            raise PermissionDeniedError(
                "The selected job does not belong to this dataset."
            )
        if actor.role != ADMINISTRATOR and job.created_by != actor.id:
            raise PermissionDeniedError("You do not own this labeling job.")

        records = DatasetRecordRepository.get_by_dataset(
            db, dataset_id, offset=max(0, offset), limit=min(max(1, limit), 1000)
        )
        return AnnotationTaskService.create_tasks_from_dataset_records(
            db=db,
            job_id=job_id,
            records=records,
            assigned_to=assigned_to,
        )
