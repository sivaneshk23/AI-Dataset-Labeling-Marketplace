"""Dataset ORM model and schema tests."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.app.models.dataset import Dataset
from backend.app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
)


def test_dataset_table():
    """The datasets table exposes the expected columns."""
    table = Dataset.__table__

    expected = {
        "id",
        "owner_id",
        "source_filename",
        "source_format",
        "source_size_bytes",
        "record_count",
        "uploaded_at",
        "title",
        "description",
        "dataset_type",
        "created_at",
    }

    assert set(table.columns.keys()) == expected
    assert table.c.id.primary_key is True
    assert table.c.title.nullable is False


def test_create_schema():
    """A valid dataset payload is accepted."""
    dataset = DatasetCreate(
        title="Vehicle Images",
        description="Image dataset for object detection.",
        dataset_type="Computer Vision",
    )

    assert dataset.title == "Vehicle Images"
    assert dataset.dataset_type == "Computer Vision"


def test_create_schema_rejects_short_title():
    """Titles shorter than three characters are rejected."""
    with pytest.raises(ValidationError):
        DatasetCreate(
            title="ab",
            description="Image dataset for object detection.",
            dataset_type="Computer Vision",
        )


def test_response_schema():
    """The response schema validates ORM instances."""
    orm_dataset = Dataset(
        id=1,
        title="Vehicle Images",
        description="Image dataset",
        dataset_type="Computer Vision",
        created_at=datetime.now(UTC),
    )

    response = DatasetResponse.model_validate(orm_dataset)

    assert response.id == 1
    assert response.title == "Vehicle Images"
