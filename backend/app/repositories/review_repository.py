"""Data access layer for marketplace reviews of labeling jobs."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.review import Review


class ReviewRepository:
    """CRUD and aggregate queries for :class:`Review`."""

    @staticmethod
    def create(
        db: Session,
        review: Review,
    ) -> Review:
        """Persist a new job review."""
        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def get_by_id(
        db: Session,
        review_id: int,
    ) -> Review | None:
        """Return one review by primary key."""
        statement = select(Review).where(Review.id == review_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Review]:
        """Return every review, newest first."""
        statement = select(Review).order_by(Review.id.desc())

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[Review]:
        """Return every review recorded for a labeling job."""
        statement = (
            select(Review).where(Review.job_id == job_id).order_by(Review.id.desc())
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        """Return the total number of job reviews."""
        return int(db.scalar(select(func.count(Review.id))) or 0)

    @staticmethod
    def update(
        db: Session,
        review: Review,
    ) -> Review:
        """Persist changes made to a tracked review instance."""
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def delete(
        db: Session,
        review: Review,
    ) -> None:
        """Delete a job review."""
        db.delete(review)
        db.commit()
