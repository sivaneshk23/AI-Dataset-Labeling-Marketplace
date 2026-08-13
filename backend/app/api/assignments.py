from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.job_assignment import (
    JobAssignmentCreate,
    JobAssignmentResponse,
    JobAssignmentUpdate,
)
from backend.app.services.job_assignment_service import (
    JobAssignmentService,
)


router = APIRouter(
    prefix="/api/assignments",
    tags=["Job Assignments"],
)


@router.post(
    "",
    response_model=JobAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment(
    assignment_data: JobAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return JobAssignmentService.create_assignment(
            db=db,
            job_id=assignment_data.job_id,
            worker_id=assignment_data.worker_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[JobAssignmentResponse],
)
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return JobAssignmentService.get_assignments(db)


@router.get(
    "/{assignment_id}",
    response_model=JobAssignmentResponse,
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = JobAssignmentService.get_assignment(
        db,
        assignment_id,
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found.",
        )

    return assignment


@router.get(
    "/job/{job_id}",
    response_model=list[JobAssignmentResponse],
)
def get_job_assignments(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return JobAssignmentService.get_assignments_by_job(
        db,
        job_id,
    )


@router.put(
    "/{assignment_id}",
    response_model=JobAssignmentResponse,
)
def update_assignment(
    assignment_id: int,
    assignment_data: JobAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return JobAssignmentService.update_assignment(
            db=db,
            assignment_id=assignment_id,
            status=assignment_data.status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        JobAssignmentService.delete_assignment(
            db,
            assignment_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None