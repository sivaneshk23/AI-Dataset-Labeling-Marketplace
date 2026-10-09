"""Annotation task endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.core.database import get_db
from backend.app.core.roles import (
    ADMINISTRATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.annotation_task import (
    AnnotationTaskAssign,
    AnnotationTaskBulkCreate,
    AnnotationTaskCreate,
    AnnotationTaskResponse,
    AnnotationTaskUpdate,
    DatasetImportRequest,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.services.annotation_task_service import (
    AnnotationTaskService,
)
from backend.app.services.dataset_record_service import DatasetRecordService

router = APIRouter(
    prefix="/api/tasks",
    tags=["Annotation Tasks"],
)


@router.post(
    "",
    response_model=APIResponse[AnnotationTaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create an annotation task inside a labeling job",
)
def create_task(
    task_data: AnnotationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[AnnotationTaskResponse]:
    """Create a single unit of annotation work."""
    task = AnnotationTaskService.create_task(
        db=db,
        job_id=task_data.job_id,
        input_text=task_data.input_text,
        assigned_to=task_data.assigned_to,
    )

    return success_response(
        AnnotationTaskResponse.model_validate(task),
        "Annotation task created successfully.",
    )


@router.post(
    "/bulk",
    response_model=APIResponse[list[AnnotationTaskResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Create several annotation tasks at once",
)
def create_tasks_bulk(
    payload: AnnotationTaskBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[AnnotationTaskResponse]]:
    """Create a batch of tasks from a list of records."""
    tasks = AnnotationTaskService.create_tasks_bulk(
        db=db,
        job_id=payload.job_id,
        items=payload.items,
        assigned_to=payload.assigned_to,
        skip_duplicates=payload.skip_duplicates,
    )

    return success_response(
        [AnnotationTaskResponse.model_validate(task) for task in tasks],
        f"{len(tasks)} annotation task(s) created successfully.",
    )


@router.post(
    "/import-dataset",
    response_model=APIResponse[list[AnnotationTaskResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Create tasks from uploaded dataset records",
)
def import_dataset_records(
    payload: DatasetImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DATASET_OWNER, ADMINISTRATOR)),
) -> APIResponse[list[AnnotationTaskResponse]]:
    """Turn persisted upload records into annotation tasks."""
    tasks = DatasetRecordService.import_to_job(
        db=db,
        dataset_id=payload.dataset_id,
        job_id=payload.job_id,
        actor=current_user,
        assigned_to=payload.assigned_to,
        offset=payload.offset,
        limit=payload.limit,
        skip_duplicates=payload.skip_duplicates,
    )
    return success_response(
        [AnnotationTaskResponse.model_validate(task) for task in tasks],
        f"{len(tasks)} annotation task(s) created from the uploaded dataset.",
    )


@router.get(
    "",
    response_model=APIResponse[list[AnnotationTaskResponse]],
    summary="List annotation tasks",
)
def get_tasks(
    job_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationTaskResponse]]:
    """Return the tasks visible to the authenticated role."""
    tasks = AnnotationTaskService.get_tasks_for_viewer(
        db,
        current_user,
        job_id=job_id,
    )

    return success_response(
        [AnnotationTaskResponse.model_validate(task) for task in tasks],
        f"{len(tasks)} annotation task(s) returned.",
    )


@router.get(
    "/mine",
    response_model=APIResponse[list[AnnotationTaskResponse]],
    summary="List the tasks assigned to the authenticated annotator",
)
def get_my_tasks(
    only_open: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationTaskResponse]]:
    """Return the annotation workspace of the caller."""
    if only_open:
        tasks = AnnotationTaskService.get_open_tasks_for_annotator(
            db,
            current_user.id,
        )
    else:
        tasks = AnnotationTaskService.get_tasks_for_viewer(
            db,
            current_user,
        )

    return success_response(
        [AnnotationTaskResponse.model_validate(task) for task in tasks],
        f"{len(tasks)} annotation task(s) returned.",
    )


@router.get(
    "/job/{job_id}",
    response_model=APIResponse[list[AnnotationTaskResponse]],
    summary="List the tasks of a labeling job",
)
def get_tasks_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[AnnotationTaskResponse]]:
    """Return the workload of a specific labeling job."""
    tasks = AnnotationTaskService.get_tasks_for_viewer(
        db,
        current_user,
        job_id=job_id,
    )

    return success_response(
        [AnnotationTaskResponse.model_validate(task) for task in tasks],
        f"{len(tasks)} annotation task(s) returned.",
    )


@router.get(
    "/{task_id}",
    response_model=APIResponse[AnnotationTaskResponse],
    summary="Retrieve one annotation task",
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[AnnotationTaskResponse]:
    """Return a single annotation task."""
    task = AnnotationTaskService.require_task(db, task_id)

    return success_response(
        AnnotationTaskResponse.model_validate(task),
        "Annotation task returned successfully.",
    )


@router.put(
    "/{task_id}",
    response_model=APIResponse[AnnotationTaskResponse],
    summary="Update an annotation task",
)
def update_task(
    task_id: int,
    task_data: AnnotationTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[AnnotationTaskResponse]:
    """Update the record, assignment or status of a task."""
    task = AnnotationTaskService.update_task(
        db=db,
        task_id=task_id,
        input_text=task_data.input_text,
        status=task_data.status,
        assigned_to=task_data.assigned_to,
    )

    return success_response(
        AnnotationTaskResponse.model_validate(task),
        "Annotation task updated successfully.",
    )


@router.post(
    "/{task_id}/assign",
    response_model=APIResponse[AnnotationTaskResponse],
    summary="Assign an annotation task to an annotator",
)
def assign_task(
    task_id: int,
    payload: AnnotationTaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[AnnotationTaskResponse]:
    """Hand a task over to an annotator."""
    task = AnnotationTaskService.assign_task(
        db,
        task_id,
        payload.assigned_to,
    )

    return success_response(
        AnnotationTaskResponse.model_validate(task),
        "Annotation task assigned successfully.",
    )


@router.delete(
    "/{task_id}",
    response_model=APIResponse[None],
    summary="Delete an annotation task",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[None]:
    """Delete a task that has not been approved."""
    AnnotationTaskService.delete_task(db, task_id)

    return success_response(
        None,
        "Annotation task deleted successfully.",
    )
