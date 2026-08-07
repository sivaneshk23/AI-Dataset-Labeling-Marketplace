from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class DatasetBase(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150
    )

    description: str = Field(
        min_length=10
    )

    dataset_type: str


class DatasetCreate(DatasetBase):
    pass


class DatasetResponse(DatasetBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )