"""Data access layer for submitted annotations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.annotation import Annotation
from backend.app.models.annotation_task import AnnotationTask


class AnnotationRepository:
    """CRUD and aggregate queries for :class:`Annotation`."""

    @staticmethod
    def create(
        db: Session,
        annotation: Annotation,
    ) -> Annotation:
        """Persist a newly submitted annotation."""
        db.add(annotation)
        db.commit()
        db.refresh(annotation)

        return annotation

    @staticmethod
    def get_by_id(
        db: Session,
        annotation_id: int,
    ) -> Annotation | None:
        """Return one annotation by primary key."""
        statement = select(Annotation).where(Annotation.id == annotation_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Annotation]:
        """Return all annotations ordered by newest first."""
        statement = select(Annotation).order_by(Annotation.id.desc())

        if offset:
            statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_task(
        db: Session,
        task_id: int,
    ) -> list[Annotation]:
        """Return every annotation attempt recorded for a task."""
        statement = (
            select(Annotation)
            .where(Annotation.task_id == task_id)
            .order_by(Annotation.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_latest_by_task(
        db: Session,
        task_id: int,
    ) -> Annotation | None:
        """Return the most recent annotation submitted for a task."""
        statement = (
            select(Annotation)
            .where(Annotation.task_id == task_id)
            .order_by(Annotation.id.desc())
            .limit(1)
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_annotator(
        db: Session,
        annotator_id: int,
    ) -> list[Annotation]:
        """Return all annotations submitted by one annotator."""
        statement = (
            select(Annotation)
            .where(Annotation.annotator_id == annotator_id)
            .order_by(Annotation.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
        status: str | None = None,
    ) -> list[Annotation]:
        """Return annotations of a job, optionally filtered by status."""
        statement = (
            select(Annotation)
            .join(
                AnnotationTask,
                Annotation.task_id == AnnotationTask.id,
            )
            .where(AnnotationTask.job_id == job_id)
            .order_by(Annotation.id)
        )

        if status is not None:
            statement = statement.where(Annotation.status == status)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def status_counts(
        db: Session,
        job_id: int | None = None,
    ) -> dict[str, int]:
        """Return a ``{status: count}`` mapping, optionally per job."""
        statement = select(
            Annotation.status,
            func.count(Annotation.id),
        ).group_by(Annotation.status)

        if job_id is not None:
            statement = statement.join(
                AnnotationTask,
                Annotation.task_id == AnnotationTask.id,
            ).where(AnnotationTask.job_id == job_id)

        return {
            str(status): int(count) for status, count in db.execute(statement).all()
        }

    @staticmethod
    def label_distribution(
        db: Session,
        job_id: int,
        statuses: tuple[str, ...] | None = None,
    ) -> list[tuple[str, int]]:
        """Return ``(label, count)`` pairs for a job, most frequent first."""
        statement = (
            select(
                Annotation.label,
                func.count(Annotation.id).label("total"),
            )
            .join(
                AnnotationTask,
                Annotation.task_id == AnnotationTask.id,
            )
            .where(AnnotationTask.job_id == job_id)
            .group_by(Annotation.label)
            .order_by(func.count(Annotation.id).desc())
        )

        if statuses:
            statement = statement.where(Annotation.status.in_(statuses))

        return [
            (str(label), int(total)) for label, total in db.execute(statement).all()
        ]

    @staticmethod
    def count_by_job(
        db: Session,
        job_id: int,
        status: str | None = None,
    ) -> int:
        """Return the annotation count of a job."""
        statement = (
            select(func.count(Annotation.id))
            .join(
                AnnotationTask,
                Annotation.task_id == AnnotationTask.id,
            )
            .where(AnnotationTask.job_id == job_id)
        )

        if status is not None:
            statement = statement.where(Annotation.status == status)

        return int(db.scalar(statement) or 0)

    @staticmethod
    def count_by_annotator(
        db: Session,
        annotator_id: int,
    ) -> int:
        """Return how many annotations one annotator has submitted."""
        statement = select(func.count(Annotation.id)).where(
            Annotation.annotator_id == annotator_id
        )

        return int(db.scalar(statement) or 0)

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        """Return the total number of annotations."""
        return int(db.scalar(select(func.count(Annotation.id))) or 0)

    @staticmethod
    def update(
        db: Session,
        annotation: Annotation,
    ) -> Annotation:
        """Persist changes made to a tracked annotation instance."""
        db.commit()
        db.refresh(annotation)

        return annotation

    @staticmethod
    def delete(
        db: Session,
        annotation: Annotation,
    ) -> None:
        """Delete an annotation."""
        db.delete(annotation)
        db.commit()
