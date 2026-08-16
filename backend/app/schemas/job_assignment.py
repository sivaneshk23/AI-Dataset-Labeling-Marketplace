from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAssignmentBase(BaseModel):
    job_id: int
    worker_id: int
    status: str = Field(
        default="assigned",
        max_length=30,
    )


class JobAssignmentCreate(JobAssignmentBase):
    pass


class JobAssignmentUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class JobAssignmentResponse(JobAssignmentBase):
    id: int
    assigned_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )