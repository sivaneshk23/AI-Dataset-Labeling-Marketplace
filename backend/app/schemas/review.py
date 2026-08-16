from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    job_id: int

    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewResponse(BaseModel):
    id: int
    job_id: int
    reviewer_id: int
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )