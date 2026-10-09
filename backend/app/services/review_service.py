"""Business rules for marketplace job reviews."""

from sqlalchemy.orm import Session

from backend.app.models.review import Review
from backend.app.repositories.labeling_job_repository import LabelingJobRepository
from backend.app.repositories.review_repository import ReviewRepository


class ReviewService:
    """Business rules for marketplace job reviews."""

    @staticmethod
    def create_review(
        db: Session,
        job_id: int,
        reviewer_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        """Create a rating for a completed labeling job."""
        job = LabelingJobRepository.get_by_id(db, job_id)
        if job is None:
            raise ValueError("Labeling job not found.")
        review = Review(
            job_id=job_id, reviewer_id=reviewer_id, rating=rating, comment=comment
        )
        return ReviewRepository.create(db, review)

    @staticmethod
    def get_review(db: Session, review_id: int) -> Review | None:
        """Return one marketplace review."""
        return ReviewRepository.get_by_id(db, review_id)

    @staticmethod
    def get_reviews(db: Session) -> list[Review]:
        """Return all marketplace reviews."""
        return ReviewRepository.get_all(db)

    @staticmethod
    def get_reviews_by_job(db: Session, job_id: int) -> list[Review]:
        """Return reviews for one labeling job."""
        return ReviewRepository.get_by_job(db, job_id)

    @staticmethod
    def update_review(
        db: Session,
        review_id: int,
        rating: int | None = None,
        comment: str | None = None,
    ) -> Review:
        """Update an existing marketplace review."""
        review = ReviewRepository.get_by_id(db, review_id)
        if review is None:
            raise ValueError("Review not found.")
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        return ReviewRepository.update(db, review)

    @staticmethod
    def delete_review(db: Session, review_id: int) -> None:
        """Delete a marketplace review."""
        review = ReviewRepository.get_by_id(db, review_id)
        if review is None:
            raise ValueError("Review not found.")
        ReviewRepository.delete(db, review)
