"""Annotation submission endpoints.

Access control is enforced in the service layer: annotators submit and revise
their own labels, reviewers may revise any label, and approved labels become
immutable so the exported dataset stays consistent.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.annotation import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationUpdate,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.services.annotation_service import (
    AnnotationService,
)

router = APIRouter(
    prefix="/api/annotations",
    tags=["Annotations"],
)


@router.post(
    "",
    response_model=APIResponse[AnnotationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a label for an annotation task",
)
def submit_annotation(
    payload: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[AnnotationResponse]:
    """Submit an annotation, storing the AI suggestion for agreement metrics."""
    annotation = AnnotationService.submit_annotation(
        db=db,
        task_id=payload.task_id,
        annotator=current_user,
        label=payload.label,
        notes=payload.notes,
        confidence=payload.confidence,
    )

    return success_response(
        AnnotationResponse.model_validate(annotation),
        "Annotation submitted successfully.",
    )


@router.get(
    "",
    response_model=APIResponse[list[AnnotationResponse]],
    summary="List annotations",
)
def get_annotations(
    job_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationResponse]]:
    """Return every annotation visible to the authenticated role."""
    annotations = AnnotationService.get_annotations_for_viewer(
        db,
        current_user,
        job_id=job_id,
    )

    return success_response(
        [AnnotationResponse.model_validate(annotation) for annotation in annotations],
        f"{len(annotations)} annotation(s) returned.",
    )


@router.get(
    "/task/{task_id}",
    response_model=APIResponse[list[AnnotationResponse]],
    summary="List the annotation history of a task",
)
def get_annotations_for_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationResponse]]:
    """Return every annotation attempt recorded for a task."""
    annotations = AnnotationService.get_annotations_for_task(
        db,
        task_id,
    )

    return success_response(
        [AnnotationResponse.model_validate(annotation) for annotation in annotations],
        f"{len(annotations)} annotation(s) returned.",
    )


@router.get(
    "/job/{job_id}",
    response_model=APIResponse[list[AnnotationResponse]],
    summary="List the annotations of a labeling job",
)
def get_annotations_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationResponse]]:
    """Return every annotation submitted for a job."""
    annotations = AnnotationService.get_annotations_for_job(
        db,
        job_id,
    )

    return success_response(
        [AnnotationResponse.model_validate(annotation) for annotation in annotations],
        f"{len(annotations)} annotation(s) returned.",
    )


@router.get(
    "/{annotation_id}",
    response_model=APIResponse[AnnotationResponse],
    summary="Retrieve one annotation",
)
def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[AnnotationResponse]:
    """Return a single annotation by identifier."""
    annotation = AnnotationService.require_annotation(
        db,
        annotation_id,
    )

    return success_response(
        AnnotationResponse.model_validate(annotation),
        "Annotation returned successfully.",
    )


@router.put(
    "/{annotation_id}",
    response_model=APIResponse[AnnotationResponse],
    summary="Revise a submitted annotation",
)
def update_annotation(
    annotation_id: int,
    payload: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[AnnotationResponse]:
    """Revise a label that has not been approved yet."""
    annotation = AnnotationService.update_annotation(
        db=db,
        annotation_id=annotation_id,
        current_user=current_user,
        label=payload.label,
        notes=payload.notes,
        confidence=payload.confidence,
    )

    return success_response(
        AnnotationResponse.model_validate(annotation),
        "Annotation updated successfully.",
    )


@router.delete(
    "/{annotation_id}",
    response_model=APIResponse[None],
    summary="Withdraw a submitted annotation",
)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[None]:
    """Withdraw an annotation that has not been approved."""
    AnnotationService.delete_annotation(
        db,
        annotation_id,
        current_user,
    )

    return success_response(
        None,
        "Annotation deleted successfully.",
    )
