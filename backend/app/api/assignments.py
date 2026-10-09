"""Job assignment endpoints."""

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
from backend.app.schemas.job_assignment import (
    JobAssignmentCreate,
    JobAssignmentResponse,
    JobAssignmentUpdate,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
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
    response_model=APIResponse[JobAssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Assign a labeling job to an annotator",
)
def create_assignment(
    assignment_data: JobAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[JobAssignmentResponse]:
    """Create a job assignment for an active annotator."""
    assignment = JobAssignmentService.create_assignment(
        db=db,
        job_id=assignment_data.job_id,
        worker_id=assignment_data.worker_id,
    )

    return success_response(
        JobAssignmentResponse.model_validate(assignment),
        "Assignment created successfully.",
    )


@router.get(
    "",
    response_model=APIResponse[list[JobAssignmentResponse]],
    summary="List job assignments",
)
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[JobAssignmentResponse]]:
    """Return every assignment for the management roles."""
    assignments = JobAssignmentService.get_assignments(db)

    return success_response(
        [
            JobAssignmentResponse.model_validate(assignment)
            for assignment in assignments
        ],
        f"{len(assignments)} assignment(s) returned.",
    )


@router.get(
    "/mine",
    response_model=APIResponse[list[JobAssignmentResponse]],
    summary="List the assignments of the authenticated annotator",
)
def get_my_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[JobAssignmentResponse]]:
    """Return the assignments belonging to the caller."""
    assignments = JobAssignmentService.get_assignments_for_worker(
        db,
        current_user.id,
    )

    return success_response(
        [
            JobAssignmentResponse.model_validate(assignment)
            for assignment in assignments
        ],
        f"{len(assignments)} assignment(s) returned.",
    )


@router.get(
    "/{assignment_id}",
    response_model=APIResponse[JobAssignmentResponse],
    summary="Retrieve one assignment",
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[JobAssignmentResponse]:
    """Return a single assignment by identifier."""
    assignment = JobAssignmentService.get_assignment(
        db,
        assignment_id,
    )

    if assignment is None:
        raise NotFoundError("Assignment not found.")

    return success_response(
        JobAssignmentResponse.model_validate(assignment),
        "Assignment returned successfully.",
    )


@router.get(
    "/job/{job_id}",
    response_model=APIResponse[list[JobAssignmentResponse]],
    summary="List the assignments of a labeling job",
)
def get_job_assignments(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[JobAssignmentResponse]]:
    """Return every assignment created for a job."""
    assignments = JobAssignmentService.get_assignments_by_job(
        db,
        job_id,
    )

    return success_response(
        [
            JobAssignmentResponse.model_validate(assignment)
            for assignment in assignments
        ],
        f"{len(assignments)} assignment(s) returned.",
    )


@router.put(
    "/{assignment_id}",
    response_model=APIResponse[JobAssignmentResponse],
    summary="Update the status of an assignment",
)
def update_assignment(
    assignment_id: int,
    assignment_data: JobAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[JobAssignmentResponse]:
    """Change the status of an existing assignment."""
    assignment = JobAssignmentService.update_assignment(
        db=db,
        assignment_id=assignment_id,
        status=assignment_data.status,
    )

    return success_response(
        JobAssignmentResponse.model_validate(assignment),
        "Assignment updated successfully.",
    )


@router.delete(
    "/{assignment_id}",
    response_model=APIResponse[None],
    summary="Delete an assignment",
)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[None]:
    """Remove an assignment from a labeling job."""
    JobAssignmentService.delete_assignment(db, assignment_id)

    return success_response(
        None,
        "Assignment deleted successfully.",
    )
