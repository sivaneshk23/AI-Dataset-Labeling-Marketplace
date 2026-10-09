"""Validation schemas for progress tracking and platform analytics."""

from pydantic import BaseModel, Field


class JobProgressResponse(BaseModel):
    """Progress snapshot of a single labeling job."""

    job_id: int
    job_title: str
    job_status: str
    dataset_id: int
    dataset_title: str

    total_tasks: int = Field(ge=0)
    tasks_by_status: dict[str, int]
    open_tasks: int = Field(ge=0)
    submitted_tasks: int = Field(ge=0)
    approved_tasks: int = Field(ge=0)
    rejected_tasks: int = Field(ge=0)

    total_annotations: int = Field(ge=0)
    annotations_by_status: dict[str, int]
    pending_reviews: int = Field(ge=0)

    completion_percentage: float = Field(ge=0, le=100)
    approval_rate: float = Field(ge=0, le=100)
    average_confidence: float | None = None
    average_rating: float | None = None
    assigned_annotators: int = Field(ge=0)

    ai_suggestions_used: int = Field(ge=0)
    ai_agreement_rate: float | None = None


class PlatformSummaryResponse(BaseModel):
    """Aggregated platform statistics used by the dashboard."""

    total_users: int = Field(ge=0)
    users_by_role: dict[str, int]

    total_datasets: int = Field(ge=0)
    total_jobs: int = Field(ge=0)
    jobs_by_status: dict[str, int]
    active_jobs: int = Field(ge=0)
    completed_jobs: int = Field(ge=0)

    total_tasks: int = Field(ge=0)
    tasks_by_status: dict[str, int]
    open_tasks: int = Field(ge=0)

    total_annotations: int = Field(ge=0)
    annotations_by_status: dict[str, int]
    pending_reviews: int = Field(ge=0)

    total_reviews: int = Field(ge=0)
    review_decisions: dict[str, int]

    annotation_completion_percentage: float = Field(ge=0, le=100)
    ai_suggestions_used: int = Field(ge=0)
    ai_agreement_rate: float | None = None
