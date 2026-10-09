from unittest.mock import MagicMock

import pytest

from backend.app.models.job_assignment import JobAssignment
from backend.app.services.job_assignment_service import (
    JobAssignmentService,
)


def test_create_assignment(monkeypatch):
    db = MagicMock()

    job = MagicMock()
    worker = MagicMock()
    worker.is_active = True

    created_assignment = JobAssignment(
        id=1,
        job_id=10,
        worker_id=20,
        status="assigned",
    )

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=job),
    )

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.UserRepository.get_by_id",
        MagicMock(return_value=worker),
    )

    create_mock = MagicMock(return_value=created_assignment)

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.create",
        create_mock,
    )

    result = JobAssignmentService.create_assignment(
        db=db,
        job_id=10,
        worker_id=20,
    )

    assert result is created_assignment

    created_object = create_mock.call_args.args[1]

    assert created_object.job_id == 10
    assert created_object.worker_id == 20
    assert created_object.status == "assigned"


def test_create_assignment_job_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Labeling job not found\.",
    ):
        JobAssignmentService.create_assignment(
            db=db,
            job_id=999999,
            worker_id=20,
        )


def test_create_assignment_worker_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=MagicMock()),
    )

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.UserRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Worker not found\.",
    ):
        JobAssignmentService.create_assignment(
            db=db,
            job_id=10,
            worker_id=999999,
        )


def test_create_assignment_worker_inactive(monkeypatch):
    db = MagicMock()

    worker = MagicMock()
    worker.is_active = False

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=MagicMock()),
    )

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.UserRepository.get_by_id",
        MagicMock(return_value=worker),
    )

    with pytest.raises(
        ValueError,
        match=r"Worker is not active\.",
    ):
        JobAssignmentService.create_assignment(
            db=db,
            job_id=10,
            worker_id=20,
        )


def test_get_assignment(monkeypatch):
    db = MagicMock()

    assignment = MagicMock(spec=JobAssignment)

    get_mock = MagicMock(return_value=assignment)

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_by_id",
        get_mock,
    )

    result = JobAssignmentService.get_assignment(
        db,
        1,
    )

    assert result is assignment

    get_mock.assert_called_once_with(
        db,
        1,
    )


def test_get_assignments(monkeypatch):
    db = MagicMock()

    assignments = [
        MagicMock(spec=JobAssignment),
        MagicMock(spec=JobAssignment),
    ]

    get_all_mock = MagicMock(return_value=assignments)

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_all",
        get_all_mock,
    )

    result = JobAssignmentService.get_assignments(db)

    assert result == assignments

    get_all_mock.assert_called_once_with(
        db,
    )


def test_update_assignment(monkeypatch):
    db = MagicMock()

    assignment = JobAssignment(
        id=1,
        job_id=10,
        worker_id=20,
        status="assigned",
    )

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_by_id",
        MagicMock(return_value=assignment),
    )

    update_mock = MagicMock(return_value=assignment)

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.update",
        update_mock,
    )

    result = JobAssignmentService.update_assignment(
        db=db,
        assignment_id=1,
        status="completed",
    )

    assert result is assignment
    assert assignment.status == "completed"

    update_mock.assert_called_once_with(
        db,
        assignment,
    )


def test_update_assignment_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Assignment not found\.",
    ):
        JobAssignmentService.update_assignment(
            db=db,
            assignment_id=999999,
            status="completed",
        )


def test_delete_assignment(monkeypatch):
    db = MagicMock()

    assignment = MagicMock(spec=JobAssignment)

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_by_id",
        MagicMock(return_value=assignment),
    )

    delete_mock = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.delete",
        delete_mock,
    )

    result = JobAssignmentService.delete_assignment(
        db,
        1,
    )

    assert result is None

    delete_mock.assert_called_once_with(
        db,
        assignment,
    )


def test_delete_assignment_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.job_assignment_service.JobAssignmentRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Assignment not found\.",
    ):
        JobAssignmentService.delete_assignment(
            db,
            999999,
        )
