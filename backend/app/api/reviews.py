"""Marketplace review endpoints for labeling jobs."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.core.database import get_db
from backend.app.core.errors import NotFoundError
from backend.app.core.roles import (
    ADMINISTRATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from backend.app.services.review_service import (
    ReviewService,
)

router = APIRouter(
    prefix="/api/reviews",
    tags=["Reviews"],
)


@router.post(
    "",
    response_model=APIResponse[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Rate a labeling job",
)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[ReviewResponse]:
    """Record a 1-5 star rating for a completed labeling job."""
    review = ReviewService.create_review(
        db=db,
        job_id=review_data.job_id,
        reviewer_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    return success_response(
        ReviewResponse.model_validate(review),
        "Review submitted successfully.",
    )


@router.get(
    "",
    response_model=APIResponse[list[ReviewResponse]],
    summary="List job reviews",
)
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[ReviewResponse]]:
    """Return every job review, newest first."""
    reviews = ReviewService.get_reviews(db)

    return success_response(
        [ReviewResponse.model_validate(review) for review in reviews],
        f"{len(reviews)} review(s) returned.",
    )


@router.get(
    "/{review_id}",
    response_model=APIResponse[ReviewResponse],
    summary="Retrieve one review",
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[ReviewResponse]:
    """Return a single review by identifier."""
    review = ReviewService.get_review(db, review_id)

    if review is None:
        raise NotFoundError("Review not found.")

    return success_response(
        ReviewResponse.model_validate(review),
        "Review returned successfully.",
    )


@router.get(
    "/job/{job_id}",
    response_model=APIResponse[list[ReviewResponse]],
    summary="List the reviews of a labeling job",
)
def get_reviews_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[ReviewResponse]]:
    """Return every review recorded for a job."""
    reviews = ReviewService.get_reviews_by_job(db, job_id)

    return success_response(
        [ReviewResponse.model_validate(review) for review in reviews],
        f"{len(reviews)} review(s) returned.",
    )


@router.put(
    "/{review_id}",
    response_model=APIResponse[ReviewResponse],
    summary="Update a review",
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[ReviewResponse]:
    """Update the rating or comment of an existing review."""
    review = ReviewService.update_review(
        db=db,
        review_id=review_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    return success_response(
        ReviewResponse.model_validate(review),
        "Review updated successfully.",
    )


@router.delete(
    "/{review_id}",
    response_model=APIResponse[None],
    summary="Delete a review",
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[None]:
    """Delete a marketplace review."""
    ReviewService.delete_review(db, review_id)

    return success_response(
        None,
        "Review deleted successfully.",
    )
