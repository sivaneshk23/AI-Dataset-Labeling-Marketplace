from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.review import Review


class ReviewRepository:

    @staticmethod
    def create(
        db: Session,
        review: Review,
    ) -> Review:
        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def get_by_id(
        db: Session,
        review_id: int,
    ) -> Review | None:

        statement = select(Review).where(
            Review.id == review_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Review]:

        statement = select(Review).order_by(
            Review.id.desc()
        )

        return list(
            db.execute(
                statement
            ).scalars().all()
        )

    @staticmethod
    def get_by_job(
        db: Session,
        job_id: int,
    ) -> list[Review]:

        statement = select(Review).where(
            Review.job_id == job_id
        ).order_by(
            Review.id.desc()
        )

        return list(
            db.execute(
                statement
            ).scalars().all()
        )

    @staticmethod
    def update(
        db: Session,
        review: Review,
    ) -> Review:

        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def delete(
        db: Session,
        review: Review,
    ) -> None:

        db.delete(review)
        db.commit()