"""Annotation quality review endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.core.database import get_db
from backend.app.core.roles import (
    ADMINISTRATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.annotation_review import (
    AnnotationReviewCreate,
    AnnotationReviewResponse,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)

router = APIRouter(
    prefix="/api/annotation-reviews",
    tags=["Annotation Reviews"],
)


@router.post(
    "",
    response_model=APIResponse[AnnotationReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Approve, reject or request revision of an annotation",
)
def create_annotation_review(
    payload: AnnotationReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[AnnotationReviewResponse]:
    """Record a quality decision and advance the annotation workflow."""
    review = AnnotationReviewService.submit_review(
        db=db,
        annotation_id=payload.annotation_id,
        reviewer=current_user,
        decision=payload.decision,
        comment=payload.comment,
    )

    return success_response(
        AnnotationReviewResponse.model_validate(review),
        f"Annotation {payload.decision.replace('_', ' ')} successfully.",
    )


@router.get(
    "",
    response_model=APIResponse[list[AnnotationReviewResponse]],
    summary="List every quality review",
)
def get_annotation_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[AnnotationReviewResponse]]:
    """Return the complete review history."""
    reviews = AnnotationReviewService.get_reviews_for_viewer(db, current_user)

    return success_response(
        [AnnotationReviewResponse.model_validate(review) for review in reviews],
        f"{len(reviews)} review(s) returned.",
    )


@router.get(
    "/annotation/{annotation_id}",
    response_model=APIResponse[list[AnnotationReviewResponse]],
    summary="List the review history of an annotation",
)
def get_reviews_for_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[AnnotationReviewResponse]]:
    """Return every decision recorded for one annotation."""
    reviews = AnnotationReviewService.get_reviews_for_annotation(
        db,
        annotation_id,
    )

    return success_response(
        [AnnotationReviewResponse.model_validate(review) for review in reviews],
        f"{len(reviews)} review(s) returned.",
    )


@router.get(
    "/job/{job_id}",
    response_model=APIResponse[list[AnnotationReviewResponse]],
    summary="List the reviews of a labeling job",
)
def get_reviews_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[AnnotationReviewResponse]]:
    """Return every review recorded for a labeling job."""
    reviews = AnnotationReviewService.get_reviews_for_job(
        db,
        job_id,
    )

    return success_response(
        [AnnotationReviewResponse.model_validate(review) for review in reviews],
        f"{len(reviews)} review(s) returned.",
    )


@router.get(
    "/{review_id}",
    response_model=APIResponse[AnnotationReviewResponse],
    summary="Retrieve one quality review",
)
def get_annotation_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[AnnotationReviewResponse]:
    """Return a single quality review."""
    review = AnnotationReviewService.require_review(
        db,
        review_id,
    )

    return success_response(
        AnnotationReviewResponse.model_validate(review),
        "Review returned successfully.",
    )


@router.delete(
    "/{review_id}",
    response_model=APIResponse[None],
    summary="Delete a quality review (administrator only)",
)
def delete_annotation_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMINISTRATOR)),
) -> APIResponse[None]:
    """Remove a review decision recorded by mistake."""
    AnnotationReviewService.delete_review(db, review_id)

    return success_response(
        None,
        "Review deleted successfully.",
    )
