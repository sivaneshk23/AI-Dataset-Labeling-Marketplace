from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAssignmentCreate(BaseModel):
    job_id: int
    worker_id: int


class JobAssignmentUpdate(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=30,
    )


class JobAssignmentResponse(BaseModel):
    id: int
    job_id: int
    worker_id: int
    status: str
    assigned_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )