"""Data access layer for annotation quality reviews."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.annotation import Annotation
from backend.app.models.annotation_review import AnnotationReview
from backend.app.models.annotation_task import AnnotationTask


class AnnotationReviewRepository:
    """CRUD and aggregate queries for :class:`AnnotationReview`."""

    @staticmethod
    def create(
        db: Session,
        review: AnnotationReview,
    ) -> AnnotationReview:
        """Persist a new quality review decision."""
        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def get_by_id(
        db: Session,
        review_id: int,
    ) -> AnnotationReview | None:
        """Return one review by primary key."""
        statement = select(AnnotationReview).where(AnnotationReview.id == review_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[AnnotationReview]:
        """Return all review decisions, newest first."""
        statement = select(AnnotationReview).order_by(AnnotationReview.id.desc())

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_annotation(
        db: Session,
        annotation_id: int,
    ) -> list[AnnotationReview]:
        """Return the review history of one annotation."""
        statement = (
            select(AnnotationReview)
            .where(AnnotationReview.annotation_id == annotation_id)
            .order_by(AnnotationReview.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_latest_by_annotation(
        db: Session,
        annotation_id: int,
    ) -> AnnotationReview | None:
        """Return the most recent decision recorded for an annotation."""
        statement = (
            select(AnnotationReview)
            .where(AnnotationReview.annotation_id == annotation_id)
            .order_by(AnnotationReview.id.desc())
            .limit(1)
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[AnnotationReview]:
        """Return every review decision recorded for a labeling job."""
        statement = (
            select(AnnotationReview)
            .join(
                Annotation,
                AnnotationReview.annotation_id == Annotation.id,
            )
            .join(
                AnnotationTask,
                Annotation.task_id == AnnotationTask.id,
            )
            .where(AnnotationTask.job_id == job_id)
            .order_by(AnnotationReview.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_reviewer(
        db: Session,
        reviewer_id: int,
    ) -> list[AnnotationReview]:
        """Return every decision taken by one reviewer."""
        statement = (
            select(AnnotationReview)
            .where(AnnotationReview.reviewer_id == reviewer_id)
            .order_by(AnnotationReview.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def decision_counts(
        db: Session,
        job_id: int | None = None,
    ) -> dict[str, int]:
        """Return a ``{decision: count}`` mapping, optionally per job."""
        statement = select(
            AnnotationReview.decision,
            func.count(AnnotationReview.id),
        ).group_by(AnnotationReview.decision)

        if job_id is not None:
            statement = (
                statement.join(
                    Annotation,
                    AnnotationReview.annotation_id == Annotation.id,
                )
                .join(
                    AnnotationTask,
                    Annotation.task_id == AnnotationTask.id,
                )
                .where(AnnotationTask.job_id == job_id)
            )

        return {
            str(decision): int(count) for decision, count in db.execute(statement).all()
        }

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        """Return the total number of review decisions."""
        return int(db.scalar(select(func.count(AnnotationReview.id))) or 0)

    @staticmethod
    def update(
        db: Session,
        review: AnnotationReview,
    ) -> AnnotationReview:
        """Persist changes made to a tracked review instance."""
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def delete(
        db: Session,
        review: AnnotationReview,
    ) -> None:
        """Delete a review decision."""
        db.delete(review)
        db.commit()
