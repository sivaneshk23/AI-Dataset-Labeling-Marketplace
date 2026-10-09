"""Progress tracking and analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import (
    JobProgressResponse,
    PlatformSummaryResponse,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


@router.get(
    "/summary",
    response_model=APIResponse[PlatformSummaryResponse],
    summary="Platform wide workload and quality summary",
)
def get_platform_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[PlatformSummaryResponse]:
    """Return the numbers shown on the dashboard."""
    summary = AnalyticsService.platform_summary(db)

    return success_response(
        PlatformSummaryResponse.model_validate(summary),
        "Platform summary returned successfully.",
    )


@router.get(
    "/jobs/{job_id}/progress",
    response_model=APIResponse[JobProgressResponse],
    summary="Progress snapshot of one labeling job",
)
def get_job_progress(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[JobProgressResponse]:
    """Return completion, approval and AI agreement metrics for a job."""
    progress = AnalyticsService.job_progress(db, job_id)

    return success_response(
        JobProgressResponse.model_validate(progress),
        "Job progress returned successfully.",
    )
