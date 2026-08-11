from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.labeling_job import (
    LabelingJobCreate,
    LabelingJobResponse,
    LabelingJobUpdate,
)
from backend.app.services.labeling_job_service import (
    LabelingJobService,
)


router = APIRouter(
    prefix="/api/jobs",
    tags=["Labeling Jobs"],
)


@router.post(
    "",
    response_model=LabelingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: LabelingJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return LabelingJobService.create_job(
            db=db,
            dataset_id=job_data.dataset_id,
            created_by=current_user.id,
            title=job_data.title,
            description=job_data.description,
            status=job_data.status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[LabelingJobResponse],
)
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return LabelingJobService.get_jobs(db)


@router.get(
    "/{job_id}",
    response_model=LabelingJobResponse,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    job = LabelingJobService.get_job(
        db,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Labeling job not found.",
        )

    return job


@router.put(
    "/{job_id}",
    response_model=LabelingJobResponse,
)
def update_job(
    job_id: int,
    job_data: LabelingJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return LabelingJobService.update_job(
            db=db,
            job_id=job_id,
            title=job_data.title,
            description=job_data.description,
            status=job_data.status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        LabelingJobService.delete_job(
            db,
            job_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None