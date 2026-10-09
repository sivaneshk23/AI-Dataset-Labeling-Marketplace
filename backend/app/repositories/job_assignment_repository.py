from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.job_assignment import JobAssignment


class JobAssignmentRepository:
    """Repository for job-assignment persistence."""

    @staticmethod
    def create(
        db: Session,
        assignment: JobAssignment,
    ) -> JobAssignment:
        """Persist and return an assignment."""

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def get_by_id(
        db: Session,
        assignment_id: int,
    ) -> JobAssignment | None:
        """Return an assignment by identifier."""

        statement = select(JobAssignment).where(JobAssignment.id == assignment_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[JobAssignment]:
        """Return all assignments."""

        statement = select(JobAssignment).order_by(JobAssignment.id.desc())

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[JobAssignment]:
        """Return assignments belonging to a job."""

        statement = select(JobAssignment).where(JobAssignment.job_id == job_id)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def update(
        db: Session,
        assignment: JobAssignment,
    ) -> JobAssignment:
        """Persist changes to an assignment."""

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def delete(
        db: Session,
        assignment: JobAssignment,
    ) -> None:
        """Delete an assignment."""

        db.delete(assignment)
        db.commit()
