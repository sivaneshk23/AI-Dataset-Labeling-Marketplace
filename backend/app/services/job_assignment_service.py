"""Business logic for job level assignments."""

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError, ValidationError
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
    """CRUD operations for job assignments."""

    @staticmethod
    def create_assignment(
        db: Session,
        job_id: int,
        worker_id: int,
    ) -> JobAssignment:
        """Assign a labeling job to an annotator.

        Raises:
            NotFoundError: when the job or worker does not exist.
            ValidationError: when the worker account is inactive.
        """
        job = LabelingJobRepository.get_by_id(
            db,
            job_id,
        )

        if job is None:
            raise NotFoundError("Labeling job not found.")

        worker = UserRepository.get_by_id(
            db,
            worker_id,
        )

        if worker is None:
            raise NotFoundError("Worker not found.")

        if not worker.is_active:
            raise ValidationError("Worker is not active.")

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
        """Return one assignment or ``None``."""
        return JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

    @staticmethod
    def get_assignments(
        db: Session,
    ) -> list[JobAssignment]:
        """Return every assignment."""
        return JobAssignmentRepository.get_all(db)

    @staticmethod
    def get_assignments_for_worker(
        db: Session,
        worker_id: int,
    ) -> list[JobAssignment]:
        """Return the assignments belonging to one annotator."""
        return [
            assignment
            for assignment in JobAssignmentRepository.get_all(db)
            if assignment.worker_id == worker_id
        ]

    @staticmethod
    def get_assignments_by_job(
        db: Session,
        job_id: int,
    ) -> list[JobAssignment]:
        """Return every assignment created for a job."""
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
        """Update the status of an assignment.

        Raises:
            NotFoundError: when the assignment does not exist.
        """
        assignment = JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

        if assignment is None:
            raise NotFoundError("Assignment not found.")

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
        """Delete an assignment.

        Raises:
            NotFoundError: when the assignment does not exist.
        """
        assignment = JobAssignmentRepository.get_by_id(
            db,
            assignment_id,
        )

        if assignment is None:
            raise NotFoundError("Assignment not found.")

        JobAssignmentRepository.delete(
            db,
            assignment,
        )
