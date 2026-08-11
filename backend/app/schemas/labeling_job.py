from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LabelingJobBase(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str = Field(
        min_length=10,
    )

    status: str = Field(
        default="open",
        max_length=30,
    )


class LabelingJobCreate(LabelingJobBase):
    dataset_id: int


class LabelingJobUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        min_length=10,
    )

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class LabelingJobResponse(LabelingJobBase):
    id: int
    dataset_id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )