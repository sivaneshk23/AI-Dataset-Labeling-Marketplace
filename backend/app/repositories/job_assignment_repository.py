from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.job_assignment import JobAssignment


class JobAssignmentRepository:

    @staticmethod
    def create(
        db: Session,
        assignment: JobAssignment,
    ) -> JobAssignment:

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def get_by_id(
        db: Session,
        assignment_id: int,
    ) -> JobAssignment | None:

        statement = select(JobAssignment).where(
            JobAssignment.id == assignment_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[JobAssignment]:

        statement = select(
            JobAssignment
        ).order_by(
            JobAssignment.id.desc()
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[JobAssignment]:

        statement = select(
            JobAssignment
        ).where(
            JobAssignment.job_id == job_id
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def update(
        db: Session,
        assignment: JobAssignment,
    ) -> JobAssignment:

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def delete(
        db: Session,
        assignment: JobAssignment,
    ) -> None:

        db.delete(assignment)
        db.commit()