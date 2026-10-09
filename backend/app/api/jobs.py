"""Labeling job endpoints."""

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
from backend.app.schemas.labeling_job import (
    LabelingJobCreate,
    LabelingJobResponse,
    LabelingJobUpdate,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
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
    response_model=APIResponse[LabelingJobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a labeling job for a dataset",
)
def create_job(
    job_data: LabelingJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[LabelingJobResponse]:
    """Create an annotation project on top of an existing dataset."""
    job = LabelingJobService.create_job(
        db=db,
        dataset_id=job_data.dataset_id,
        created_by=current_user.id,
        title=job_data.title,
        description=job_data.description,
        status=job_data.status,
        annotation_type=job_data.annotation_type,
        label_options=job_data.label_options,
    )

    return success_response(
        LabelingJobResponse.model_validate(job),
        "Labeling job created successfully.",
    )


@router.get(
    "",
    response_model=APIResponse[list[LabelingJobResponse]],
    summary="List labeling jobs",
)
def get_jobs(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[LabelingJobResponse]]:
    """Return every labeling job, optionally filtered by status."""
    jobs = LabelingJobService.get_jobs(
        db,
        actor=current_user,
        status=status_filter,
    )

    return success_response(
        [LabelingJobResponse.model_validate(job) for job in jobs],
        f"{len(jobs)} labeling job(s) returned.",
    )


@router.get(
    "/{job_id}",
    response_model=APIResponse[LabelingJobResponse],
    summary="Retrieve one labeling job",
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[LabelingJobResponse]:
    """Return a single labeling job by identifier."""
    job = LabelingJobService.get_job(db, job_id)

    if job is None:
        raise NotFoundError("Labeling job not found.")
    if current_user.role != ADMINISTRATOR and job.created_by != current_user.id:
        raise NotFoundError("Labeling job not found.")

    return success_response(
        LabelingJobResponse.model_validate(job),
        "Labeling job returned successfully.",
    )


@router.put(
    "/{job_id}",
    response_model=APIResponse[LabelingJobResponse],
    summary="Update a labeling job",
)
def update_job(
    job_id: int,
    job_data: LabelingJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[LabelingJobResponse]:
    """Update the title, description or status of a job."""
    job = LabelingJobService.update_job(
        db=db,
        job_id=job_id,
        title=job_data.title,
        description=job_data.description,
        status=job_data.status,
        annotation_type=job_data.annotation_type,
        label_options=job_data.label_options,
    )

    return success_response(
        LabelingJobResponse.model_validate(job),
        "Labeling job updated successfully.",
    )


@router.delete(
    "/{job_id}",
    response_model=APIResponse[None],
    summary="Delete a labeling job",
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[None]:
    """Delete a labeling job and its dependent work items."""
    LabelingJobService.delete_job(db, job_id, current_user)

    return success_response(
        None,
        "Labeling job deleted successfully.",
    )
