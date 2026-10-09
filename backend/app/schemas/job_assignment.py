from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAssignmentBase(BaseModel):
    """Shared assignment request fields."""

    job_id: int
    worker_id: int
    status: str = Field(
        default="assigned",
        max_length=30,
    )


class JobAssignmentCreate(JobAssignmentBase):
    """Payload for creating an assignment."""

    pass


class JobAssignmentUpdate(BaseModel):
    """Payload for updating an assignment."""

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class JobAssignmentResponse(JobAssignmentBase):
    """Assignment representation returned by the API."""

    id: int
    assigned_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
