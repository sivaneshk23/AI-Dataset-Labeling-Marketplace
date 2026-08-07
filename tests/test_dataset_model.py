from datetime import datetime

from backend.app.models.dataset import Dataset
from backend.app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse
)


def test_dataset_table():

    table = Dataset.__table__

    expected = {
        "id",
        "title",
        "description",
        "dataset_type",
        "created_at"
    }

    assert set(table.columns.keys()) == expected


def test_create_schema():

    dataset = DatasetCreate(
        title="Vehicle Images",
        description="Image dataset for object detection.",
        dataset_type="Computer Vision"
    )

    assert dataset.title == "Vehicle Images"


def test_response_schema():

    orm_dataset = Dataset(
        id=1,
        title="Vehicle Images",
        description="Image dataset",
        dataset_type="Computer Vision",
        created_at=datetime.now()
    )

    response = DatasetResponse.model_validate(
        orm_dataset
    )

    assert response.id == 1


if __name__ == "__main__":

    tests = [
        test_dataset_table,
        test_create_schema,
        test_response_schema
    ]

    passed = 0

    print("\n===== DATASET MODEL TESTS =====\n")

    for test in tests:

        try:
            test()

            print(
                f"{test.__name__}: PASS"
            )

            passed += 1

        except Exception as error:

            print(
                f"{test.__name__}: FAIL"
            )

            print(error)

    print(
        f"\nResult: {passed}/{len(tests)} tests passed."
    )