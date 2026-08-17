from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.core.database import get_db
from backend.app.models.user import User
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
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
    require_roles(
        "dataset_owner",
        "administrator",
    )
),
):

    try:
        return ReviewService.create_review(
            db=db,
            job_id=review_data.job_id,
            reviewer_id=current_user.id,
            rating=review_data.rating,
            comment=review_data.comment,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[ReviewResponse],
)
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return ReviewService.get_reviews(db)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    review = ReviewService.get_review(
        db,
        review_id,
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    return review


@router.get(
    "/job/{job_id}",
    response_model=list[ReviewResponse],
)
def get_reviews_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return ReviewService.get_reviews_by_job(
        db,
        job_id,
    )


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
    require_roles(
        "dataset_owner",
        "administrator",
    )
),
):

    try:
        return ReviewService.update_review(
            db=db,
            review_id=review_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
    require_roles(
        "dataset_owner",
        "administrator",
    )
),
):

    try:
        ReviewService.delete_review(
            db,
            review_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None