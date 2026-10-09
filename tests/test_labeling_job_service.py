from unittest.mock import MagicMock

import pytest

from backend.app.models.labeling_job import LabelingJob
from backend.app.services.labeling_job_service import (
    LabelingJobService,
)


def test_create_job(monkeypatch):
    db = MagicMock()

    dataset = MagicMock()
    dataset.owner_id = 5
    created_job = LabelingJob(
        id=1,
        dataset_id=10,
        created_by=5,
        title="Test Labeling Job",
        description="Job for service testing.",
        status="open",
    )

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.DatasetRepository.get_by_id",
        MagicMock(return_value=dataset),
    )

    create_mock = MagicMock(return_value=created_job)

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.create",
        create_mock,
    )

    result = LabelingJobService.create_job(
        db=db,
        dataset_id=10,
        created_by=5,
        title="Test Labeling Job",
        description="Job for service testing.",
        status="open",
    )

    assert result is created_job

    created_object = create_mock.call_args.args[1]

    assert created_object.dataset_id == 10
    assert created_object.created_by == 5
    assert created_object.title == "Test Labeling Job"
    assert created_object.description == "Job for service testing."
    assert created_object.status == "open"


def test_create_job_dataset_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.DatasetRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Dataset not found\.",
    ):
        LabelingJobService.create_job(
            db=db,
            dataset_id=999999,
            created_by=5,
            title="Test Job",
            description="Testing invalid dataset.",
        )


def test_get_job(monkeypatch):
    db = MagicMock()

    job = MagicMock(spec=LabelingJob)

    get_mock = MagicMock(return_value=job)

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_by_id",
        get_mock,
    )

    result = LabelingJobService.get_job(
        db,
        1,
    )

    assert result is job

    get_mock.assert_called_once_with(
        db,
        1,
    )


def test_get_jobs(monkeypatch):
    db = MagicMock()

    jobs = [
        MagicMock(spec=LabelingJob),
        MagicMock(spec=LabelingJob),
    ]

    get_all_mock = MagicMock(return_value=jobs)

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_all",
        get_all_mock,
    )

    result = LabelingJobService.get_jobs(db)

    assert result == jobs

    get_all_mock.assert_called_once_with(
        db,
    )


def test_update_job(monkeypatch):
    db = MagicMock()

    job = LabelingJob(
        id=1,
        dataset_id=10,
        created_by=5,
        title="Old Job",
        description="Old description.",
        status="open",
    )

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=job),
    )

    update_mock = MagicMock(return_value=job)

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.update",
        update_mock,
    )

    result = LabelingJobService.update_job(
        db=db,
        job_id=1,
        title="Updated Job",
        description="Updated description.",
        status="completed",
    )

    assert result is job
    assert job.title == "Updated Job"
    assert job.description == "Updated description."
    assert job.status == "completed"

    update_mock.assert_called_once_with(
        db,
        job,
    )


def test_update_job_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Labeling job not found\.",
    ):
        LabelingJobService.update_job(
            db=db,
            job_id=999999,
            title="Updated Job",
        )


def test_delete_job(monkeypatch):
    db = MagicMock()

    job = MagicMock(spec=LabelingJob)

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=job),
    )

    delete_mock = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.delete",
        delete_mock,
    )

    result = LabelingJobService.delete_job(
        db,
        1,
    )

    assert result is None

    delete_mock.assert_called_once_with(
        db,
        job,
    )


def test_delete_job_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.labeling_job_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Labeling job not found\.",
    ):
        LabelingJobService.delete_job(
            db,
            999999,
        )
