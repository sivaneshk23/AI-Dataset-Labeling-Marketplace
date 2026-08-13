from sqlalchemy.orm import Session

from backend.app.models.job_assignment import JobAssignment
from backend.app.repositories.job_assignment_repository import (
    JobAssignmentRepository,
)
from backend.app.repositories.labeling_job_repository import (
    LabelingJobRepository,
)
from backend.app.repositories.user_repository import (
    UserRepository,
)


class JobAssignmentService:

    @staticmethod
    def create_assignment(
        db: Session,
        job_id: int,
        worker_id: int,
    ) -> JobAssignment:

        job = LabelingJobRepository.get_by_id(
            db,
            job_id,
        )

        if job is None:
            raise ValueError(
                "Labeling job not found."
            )

        worker = UserRepository.get_by_id(
            db,
            worker_id,
        )

        if worker is None:
            raise ValueError(
                "Worker not found."
            )

        if not worker.is_active:
            raise ValueError(
                "Worker is not active."
            )

        assignment = JobAssignment(
            job_id=job_id,
            worker_id=worker_id,
            status="assigned",
        )

        return JobAssignmentRepository.create(
            db,
            assignment,
        )

    @staticmethod
    def get_assignment(
        db: Session,
        assignment_id: int,
    ) -> JobAssignment | None:

        return JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

    @staticmethod
    def get_assignments(
        db: Session,
    ) -> list[JobAssignment]:

        return JobAssignmentRepository.get_all(db)

    @staticmethod
    def get_assignments_by_job(
        db: Session,
        job_id: int,
    ) -> list[JobAssignment]:

        return JobAssignmentRepository.get_by_job(
            db,
            job_id,
        )

    @staticmethod
    def update_assignment(
        db: Session,
        assignment_id: int,
        status: str,
    ) -> JobAssignment:

        assignment = JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

        if assignment is None:
            raise ValueError(
                "Assignment not found."
            )

        assignment.status = status

        return JobAssignmentRepository.update(
            db,
            assignment,
        )

    @staticmethod
    def delete_assignment(
        db: Session,
        assignment_id: int,
    ) -> None:

        assignment = JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

        if assignment is None:
            raise ValueError(
                "Assignment not found."
            )

        JobAssignmentRepository.delete(
            db,
            assignment,
        )