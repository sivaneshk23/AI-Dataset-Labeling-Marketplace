"""Dataset export endpoints.

Export endpoints are the documented exception to the JSON envelope: requesting
``format=csv`` streams a file download, while ``format=json`` returns the
standard envelope with the same rows.
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.core.database import get_db
from backend.app.core.roles import (
    ADMINISTRATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.response import success_response
from backend.app.services.export_service import ExportService

router = APIRouter(
    prefix="/api/exports",
    tags=["Exports"],
)


@router.get(
    "/jobs/{job_id}",
    summary="Export the labeled records of a labeling job",
    response_model=None,
)
def export_job(
    job_id: int,
    export_format: str = Query(
        default="csv",
        alias="format",
        pattern="^(csv|json)$",
    ),
    include_unapproved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
):
    """Download the approved labels of a job as CSV or JSON."""
    filename, rows = ExportService.build_job_export(
        db,
        job_id,
        include_unapproved=include_unapproved,
        actor=current_user,
    )

    if export_format == "json":
        return success_response(
            rows,
            f"{len(rows)} labeled record(s) exported.",
        )

    return _csv_response(filename, rows)


@router.get(
    "/datasets/{dataset_id}",
    summary="Export the labeled records of every job in a dataset",
    response_model=None,
)
def export_dataset(
    dataset_id: int,
    export_format: str = Query(
        default="csv",
        alias="format",
        pattern="^(csv|json)$",
    ),
    include_unapproved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
):
    """Download the approved labels of a whole dataset."""
    filename, rows = ExportService.build_dataset_export(
        db,
        dataset_id,
        include_unapproved=include_unapproved,
        actor=current_user,
    )

    if export_format == "json":
        return success_response(
            rows,
            f"{len(rows)} labeled record(s) exported.",
        )

    return _csv_response(filename, rows)


def _csv_response(
    filename: str,
    rows: list[dict],
) -> StreamingResponse:
    """Wrap CSV text into a downloadable response."""
    csv_text = ExportService.to_csv(rows)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }

    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv",
        headers=headers,
    )


__all__ = ["router"]
