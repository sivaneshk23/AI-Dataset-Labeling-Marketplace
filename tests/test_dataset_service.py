from unittest.mock import MagicMock

import pytest

from backend.app.models.dataset import Dataset
from backend.app.services.dataset_service import DatasetService


def test_create_dataset(monkeypatch):
    db = MagicMock()

    created_dataset = Dataset(
        id=1,
        title="Test Dataset",
        description="Dataset for service testing.",
        dataset_type="Computer Vision",
    )

    create_mock = MagicMock(return_value=created_dataset)

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.create",
        create_mock,
    )

    result = DatasetService.create_dataset(
        db=db,
        title="Test Dataset",
        description="Dataset for service testing.",
        dataset_type="Computer Vision",
    )

    assert result is created_dataset
    create_mock.assert_called_once()

    created_object = create_mock.call_args.args[1]

    assert created_object.title == "Test Dataset"
    assert created_object.description == "Dataset for service testing."
    assert created_object.dataset_type == "Computer Vision"


def test_get_dataset(monkeypatch):
    db = MagicMock()

    dataset = MagicMock(spec=Dataset)

    get_mock = MagicMock(return_value=dataset)

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_by_id",
        get_mock,
    )

    result = DatasetService.get_dataset(
        db,
        1,
    )

    assert result is dataset

    get_mock.assert_called_once_with(
        db,
        1,
    )


def test_get_datasets(monkeypatch):
    db = MagicMock()

    datasets = [
        MagicMock(spec=Dataset),
        MagicMock(spec=Dataset),
    ]

    get_all_mock = MagicMock(return_value=datasets)

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_all",
        get_all_mock,
    )

    result = DatasetService.get_datasets(db)

    assert result == datasets

    get_all_mock.assert_called_once_with(
        db,
    )


def test_update_dataset(monkeypatch):
    db = MagicMock()

    dataset = Dataset(
        id=1,
        title="Old Dataset",
        description="Old description.",
        dataset_type="Computer Vision",
    )

    get_mock = MagicMock(return_value=dataset)

    update_mock = MagicMock(return_value=dataset)

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_by_id",
        get_mock,
    )

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.update",
        update_mock,
    )

    result = DatasetService.update_dataset(
        db=db,
        dataset_id=1,
        title="Updated Dataset",
        description="Updated description.",
        dataset_type="Natural Language Processing",
    )

    assert result is dataset
    assert dataset.title == "Updated Dataset"
    assert dataset.description == "Updated description."
    assert dataset.dataset_type == "Natural Language Processing"

    get_mock.assert_called_once_with(
        db,
        1,
    )

    update_mock.assert_called_once_with(
        db,
        dataset,
    )


def test_update_dataset_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Dataset not found\.",
    ):
        DatasetService.update_dataset(
            db=db,
            dataset_id=999999,
            title="Updated Dataset",
        )


def test_delete_dataset(monkeypatch):
    db = MagicMock()

    dataset = MagicMock(spec=Dataset)

    get_mock = MagicMock(return_value=dataset)

    delete_mock = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_by_id",
        get_mock,
    )

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.delete",
        delete_mock,
    )

    result = DatasetService.delete_dataset(
        db,
        1,
    )

    assert result is None

    get_mock.assert_called_once_with(
        db,
        1,
    )

    delete_mock.assert_called_once_with(
        db,
        dataset,
    )


def test_delete_dataset_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.dataset_service.DatasetRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Dataset not found\.",
    ):
        DatasetService.delete_dataset(
            db,
            999999,
        )
