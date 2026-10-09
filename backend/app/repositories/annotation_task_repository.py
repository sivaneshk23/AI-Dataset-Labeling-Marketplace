"""Data access layer for annotation tasks."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.annotation_task import AnnotationTask


class AnnotationTaskRepository:
    """CRUD and aggregate queries for :class:`AnnotationTask`."""

    @staticmethod
    def create(
        db: Session,
        task: AnnotationTask,
    ) -> AnnotationTask:
        """Persist a new annotation task."""
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def create_many(
        db: Session,
        tasks: list[AnnotationTask],
    ) -> list[AnnotationTask]:
        """Persist a batch of annotation tasks in a single transaction."""
        db.add_all(tasks)
        db.commit()

        for task in tasks:
            db.refresh(task)

        return tasks

    @staticmethod
    def get_by_id(
        db: Session,
        task_id: int,
    ) -> AnnotationTask | None:
        """Return one task by primary key."""
        statement = select(AnnotationTask).where(AnnotationTask.id == task_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        job_id: int | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[AnnotationTask]:
        """Return tasks ordered by newest first with optional pagination."""
        statement = select(AnnotationTask).order_by(AnnotationTask.id.desc())

        if job_id is not None:
            statement = statement.where(AnnotationTask.job_id == job_id)

        if offset:
            statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[AnnotationTask]:
        """Return every task that belongs to a labeling job."""
        statement = (
            select(AnnotationTask)
            .where(AnnotationTask.job_id == job_id)
            .order_by(AnnotationTask.id)
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_assignee(
        db: Session,
        user_id: int,
        statuses: tuple[str, ...] | None = None,
    ) -> list[AnnotationTask]:
        """Return tasks assigned to one annotator."""
        statement = select(AnnotationTask).where(AnnotationTask.assigned_to == user_id)

        if statuses:
            statement = statement.where(AnnotationTask.status.in_(statuses))

        statement = statement.order_by(AnnotationTask.id)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def count_by_job(
        db: Session,
        job_id: int,
    ) -> int:
        """Return the number of tasks created for a job."""
        statement = select(func.count(AnnotationTask.id)).where(
            AnnotationTask.job_id == job_id
        )

        return int(db.scalar(statement) or 0)

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        """Return the total number of annotation tasks."""
        return int(db.scalar(select(func.count(AnnotationTask.id))) or 0)

    @staticmethod
    def status_counts(
        db: Session,
        job_id: int | None = None,
    ) -> dict[str, int]:
        """Return a ``{status: count}`` mapping, optionally per job."""
        statement = select(
            AnnotationTask.status,
            func.count(AnnotationTask.id),
        ).group_by(AnnotationTask.status)

        if job_id is not None:
            statement = statement.where(AnnotationTask.job_id == job_id)

        return {
            str(status): int(count) for status, count in db.execute(statement).all()
        }

    @staticmethod
    def update(
        db: Session,
        task: AnnotationTask,
    ) -> AnnotationTask:
        """Persist changes made to a tracked task instance."""
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def delete(
        db: Session,
        task: AnnotationTask,
    ) -> None:
        """Delete an annotation task."""
        db.delete(task)
        db.commit()
