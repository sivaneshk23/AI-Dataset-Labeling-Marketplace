from datetime import datetime

from backend.app.models.job_assignment import JobAssignment
from backend.app.schemas.job_assignment import (
    JobAssignmentCreate,
    JobAssignmentResponse,
)


def test_assignment_table():

    table = JobAssignment.__table__

    expected = {
        "id",
        "job_id",
        "worker_id",
        "status",
        "assigned_at",
    }

    assert set(table.columns.keys()) == expected


def test_assignment_create_schema():

    assignment = JobAssignmentCreate(
        job_id=1,
        worker_id=2,
        status="assigned",
    )

    assert assignment.job_id == 1
    assert assignment.worker_id == 2
    assert assignment.status == "assigned"


def test_assignment_response_schema():

    assignment = JobAssignment(
        id=1,
        job_id=2,
        worker_id=3,
        status="assigned",
        assigned_at=datetime.now(),
    )

    response = JobAssignmentResponse.model_validate(
        assignment
    )

    assert response.id == 1