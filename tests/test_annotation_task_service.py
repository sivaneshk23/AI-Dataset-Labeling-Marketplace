"""Unit tests for the annotation task workflow rules.

These tests exercise the state machine that protects labels once they have
been approved, plus the bulk import and assignment rules used by the task
management screen.
"""

import pytest

from backend.app.core.errors import (
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationError,
)
from backend.app.services.annotation_task_service import (
    MAX_BULK_ITEMS,
    AnnotationTaskService,
)

ITEMS = (
    "Refund request for the damaged order.",
    "Delivery driver left the parcel at the front door.",
)


class TestTaskCreation:
    """Rules applied when tasks are created."""

    def test_create_task_stores_a_pending_task(self, db_session, build_workflow):
        workflow = build_workflow(items=(), assign_to=None)

        task = AnnotationTaskService.create_task(
            db_session,
            workflow["job"].id,
            "  Refund request for a late delivery.  ",
        )

        assert task.id is not None
        assert task.status == "pending"
        assert task.assigned_to is None
        assert task.input_text == "Refund request for a late delivery."

    def test_create_task_rejects_an_empty_record(self, db_session, build_workflow):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(ValidationError, match=r"input_text must not be empty"):
            AnnotationTaskService.create_task(
                db_session,
                workflow["job"].id,
                "   ",
            )

    def test_create_task_requires_an_existing_job(self, db_session):
        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            AnnotationTaskService.create_task(
                db_session,
                999999,
                "Refund request.",
            )

    def test_closed_jobs_do_not_accept_new_tasks(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None, job_status="closed")

        with pytest.raises(InvalidStateError, match=r"no longer accepts new tasks"):
            AnnotationTaskService.create_task(
                db_session,
                workflow["job"].id,
                "Refund request.",
            )

    def test_tasks_can_only_be_assigned_to_active_annotators(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(
            ValidationError,
            match=r"Only users with the annotator role",
        ):
            AnnotationTaskService.create_task(
                db_session,
                workflow["job"].id,
                "Refund request.",
                assigned_to=accounts["dataset_owner"].id,
            )

        accounts["annotator"].is_active = False

        with pytest.raises(ValidationError, match=r"inactive"):
            AnnotationTaskService.create_task(
                db_session,
                workflow["job"].id,
                "Refund request.",
                assigned_to=accounts["annotator"].id,
            )

    def test_unknown_assignees_are_reported(self, db_session, build_workflow):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(NotFoundError, match=r"Annotator not found\."):
            AnnotationTaskService.create_task(
                db_session,
                workflow["job"].id,
                "Refund request.",
                assigned_to=999999,
            )


class TestBulkTaskCreation:
    """Bulk import rules used by the dataset owner screen."""

    def test_bulk_creation_skips_internal_and_known_duplicates(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(ITEMS[0],), assign_to=None)

        created = AnnotationTaskService.create_tasks_bulk(
            db_session,
            workflow["job"].id,
            [
                ITEMS[1],
                ITEMS[1].upper(),
                "   ",
                ITEMS[0],
            ],
            assigned_to=accounts["annotator"].id,
        )

        assert len(created) == 1
        assert created[0].input_text == ITEMS[1]
        assert created[0].assigned_to == accounts["annotator"].id

    def test_duplicates_can_be_imported_when_explicitly_allowed(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None)

        created = AnnotationTaskService.create_tasks_bulk(
            db_session,
            workflow["job"].id,
            [ITEMS[0], ITEMS[0]],
            skip_duplicates=False,
        )

        assert len(created) == 2

    def test_bulk_creation_validates_the_payload(self, db_session, build_workflow):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(ValidationError, match=r"At least one record is required"):
            AnnotationTaskService.create_tasks_bulk(
                db_session,
                workflow["job"].id,
                [],
            )

        with pytest.raises(ValidationError, match=r"maximum of 500"):
            AnnotationTaskService.create_tasks_bulk(
                db_session,
                workflow["job"].id,
                [f"Record {index}" for index in range(MAX_BULK_ITEMS + 1)],
            )

    def test_bulk_creation_rejects_a_payload_without_new_records(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(
            ValidationError,
            match=r"every item already exists in this job",
        ):
            AnnotationTaskService.create_tasks_bulk(
                db_session,
                workflow["job"].id,
                ["   ", " "],
            )

    def test_bulk_creation_validates_the_assignee(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None)

        with pytest.raises(ValidationError):
            AnnotationTaskService.create_tasks_bulk(
                db_session,
                workflow["job"].id,
                [ITEMS[0]],
                assigned_to=accounts["dataset_owner"].id,
            )


class TestTaskQueries:
    """Read helpers and their visibility rules."""

    def test_missing_tasks_return_none_or_raise(self, db_session):
        assert AnnotationTaskService.get_task(db_session, 999999) is None

        with pytest.raises(NotFoundError, match=r"Annotation task not found\."):
            AnnotationTaskService.require_task(db_session, 999999)

    def test_tasks_can_be_filtered_by_job(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to=None)

        assert len(AnnotationTaskService.get_tasks(db_session)) == 2
        assert len(AnnotationTaskService.get_tasks(db_session, workflow["job"].id)) == 2
        assert (
            len(
                AnnotationTaskService.get_tasks_for_job(
                    db_session,
                    workflow["job"].id,
                )
            )
            == 2
        )

        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            AnnotationTaskService.get_tasks_for_job(db_session, 999999)

    def test_viewers_only_see_tasks_they_may_work_on(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")

        mine = AnnotationTaskService.get_tasks_for_viewer(
            db_session,
            accounts["annotator"],
        )

        assert len(mine) == 2

        assert (
            AnnotationTaskService.get_tasks_for_viewer(
                db_session,
                accounts["second_annotator"],
            )
            == []
        )

        assert (
            len(
                AnnotationTaskService.get_tasks_for_viewer(
                    db_session,
                    accounts["dataset_owner"],
                    job_id=workflow["job"].id,
                )
            )
            == 2
        )


class TestTaskAssignmentAndStateMachine:
    """Assignment and manual status transition rules."""

    def test_assigning_a_pending_task_starts_the_work(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to=None)
        task = workflow["tasks"][0]

        updated = AnnotationTaskService.assign_task(
            db_session,
            task.id,
            accounts["annotator"].id,
        )

        assert updated.assigned_to == accounts["annotator"].id
        assert updated.status == "in_progress"

    def test_approved_tasks_cannot_be_reassigned(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")
        task = workflow["tasks"][0]
        task.status = "approved"
        db_session.flush()

        with pytest.raises(InvalidStateError, match=r"can no longer be reassigned"):
            AnnotationTaskService.assign_task(
                db_session,
                task.id,
                accounts["second_annotator"].id,
            )

    def test_assignment_validates_the_annotator(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to=None)

        with pytest.raises(ValidationError):
            AnnotationTaskService.assign_task(
                db_session,
                workflow["tasks"][0].id,
                accounts["dataset_owner"].id,
            )

        with pytest.raises(NotFoundError, match=r"Annotation task not found\."):
            AnnotationTaskService.assign_task(
                db_session,
                999999,
                accounts["annotator"].id,
            )

    def test_tasks_can_be_edited_before_approval(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to=None)
        task = workflow["tasks"][0]

        updated = AnnotationTaskService.update_task(
            db_session,
            task.id,
            input_text="  Refund request for a broken item.  ",
            assigned_to=accounts["annotator"].id,
            status="in_progress",
        )

        assert updated.input_text == "Refund request for a broken item."
        assert updated.assigned_to == accounts["annotator"].id
        assert updated.status == "in_progress"

        unchanged = AnnotationTaskService.update_task(
            db_session,
            task.id,
            status="in_progress",
        )

        assert unchanged.status == "in_progress"

    def test_task_updates_are_validated(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to=None)
        task = workflow["tasks"][0]

        with pytest.raises(ValidationError, match=r"input_text must not be empty"):
            AnnotationTaskService.update_task(db_session, task.id, input_text="  ")

        with pytest.raises(ValidationError):
            AnnotationTaskService.update_task(
                db_session,
                task.id,
                assigned_to=accounts["dataset_owner"].id,
            )

        with pytest.raises(InvalidStateError, match=r"cannot be moved to"):
            AnnotationTaskService.update_task(db_session, task.id, status="submitted")

        with pytest.raises(NotFoundError):
            AnnotationTaskService.update_task(db_session, 999999, status="in_progress")

    def test_review_decisions_move_the_task_to_the_matching_state(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")
        task = workflow["tasks"][0]

        AnnotationTaskService.mark_submitted(db_session, task)
        assert task.status == "submitted"

        AnnotationTaskService.apply_review_decision(db_session, task, "needs_revision")
        assert task.status == "in_progress"

        AnnotationTaskService.apply_review_decision(db_session, task, "rejected")
        assert task.status == "rejected"

        AnnotationTaskService.apply_review_decision(db_session, task, "approved")
        assert task.status == "approved"

        AnnotationTaskService.apply_review_decision(db_session, task, "unknown")
        assert task.status == "approved"


class TestJobCompletionAndCleanup:
    """Job closure rules plus task deletion and open-task listings."""

    def test_jobs_close_only_when_every_task_is_approved(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")
        first, second = workflow["tasks"]
        job_id = workflow["job"].id

        assert (
            AnnotationTaskService.complete_job_if_finished(db_session, job_id) is False
        )

        first.status = "approved"
        db_session.flush()

        assert (
            AnnotationTaskService.complete_job_if_finished(db_session, job_id) is False
        )

        second.status = "approved"
        db_session.flush()

        assert (
            AnnotationTaskService.complete_job_if_finished(db_session, job_id) is True
        )
        assert workflow["job"].status == "completed"

        assert (
            AnnotationTaskService.complete_job_if_finished(db_session, job_id) is False
        )

    def test_finished_job_check_handles_empty_and_missing_jobs(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=(), assign_to=None)

        assert (
            AnnotationTaskService.complete_job_if_finished(
                db_session,
                workflow["job"].id,
            )
            is False
        )
        assert (
            AnnotationTaskService.complete_job_if_finished(db_session, 999999) is False
        )

    def test_only_unapproved_tasks_can_be_deleted(
        self,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")
        deletable, approved = workflow["tasks"]

        AnnotationTaskService.delete_task(db_session, deletable.id)

        assert AnnotationTaskService.get_task(db_session, deletable.id) is None

        approved.status = "approved"
        db_session.flush()

        with pytest.raises(ConflictError, match=r"Approved tasks cannot be deleted"):
            AnnotationTaskService.delete_task(db_session, approved.id)

        with pytest.raises(NotFoundError):
            AnnotationTaskService.delete_task(db_session, 999999)

    def test_open_tasks_exclude_completed_work(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=ITEMS, assign_to="annotator")
        first, second = workflow["tasks"]
        first.status = "submitted"
        db_session.flush()

        open_tasks = AnnotationTaskService.get_open_tasks_for_annotator(
            db_session,
            accounts["annotator"].id,
        )

        assert [task.id for task in open_tasks] == [second.id]
