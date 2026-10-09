"""Unit tests for the labeled dataset export service.

The export is the last step of the business workflow, so the tests verify
what a dataset owner actually receives: approved rows only by default, the
AI agreement columns and a CSV that opens in Excel.
"""

import pytest

from backend.app.core.errors import NotFoundError
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)
from backend.app.services.annotation_service import AnnotationService
from backend.app.services.export_service import (
    EXPORT_COLUMNS,
    ExportService,
)

APPROVED_ITEM = "Refund request for the damaged order."
PENDING_ITEM = "Delivery driver left the parcel at the front door."


def _labelled_workflow(db_session, accounts, build_workflow, items):
    """Submit one annotation per task and return the workflow."""
    workflow = build_workflow(items=items)

    for task in workflow["tasks"]:
        AnnotationService.submit_annotation(
            db_session,
            task.id,
            accounts["annotator"],
            "refund request",
            confidence=0.7,
        )

    return workflow


class TestJobExport:
    """Row building for a single labeling job."""

    def test_only_approved_annotations_are_exported_by_default(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM, PENDING_ITEM),
        )

        approved_annotation = AnnotationService.get_annotations_for_task(
            db_session,
            workflow["tasks"][0].id,
        )[0]

        AnnotationReviewService.submit_review(
            db_session,
            approved_annotation.id,
            accounts["dataset_owner"],
            "approved",
            comment="Correct label.",
        )

        filename, rows = ExportService.build_job_export(
            db_session,
            workflow["job"].id,
        )

        assert filename == "intent-classification-round-1-annotations.csv"
        assert len(rows) == 1

        row = rows[0]

        assert row["dataset_title"] == "Customer Support Tickets"
        assert row["job_title"] == "Intent Classification Round 1"
        assert row["input_text"] == APPROVED_ITEM
        assert row["label"] == "refund request"
        assert row["annotation_status"] == "approved"
        assert row["annotator_name"] == "Annotator User"
        assert row["annotation_status"] == "approved"
        assert row["review_decision"] == "approved"
        assert row["review_comment"] == "Correct label."
        assert row["annotator_confidence"] == 0.7
        assert row["ai_agreement"] in {"True", "False", ""}
        assert set(row) == set(EXPORT_COLUMNS)

    def test_unapproved_annotations_can_be_included_on_request(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM, PENDING_ITEM),
        )

        _filename, rows = ExportService.build_job_export(
            db_session,
            workflow["job"].id,
            include_unapproved=True,
        )

        assert len(rows) == 2
        assert {row["annotation_status"] for row in rows} == {"submitted"}
        assert {row["review_decision"] for row in rows} == {""}

    def test_ai_agreement_is_reported_when_a_suggestion_exists(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM,),
        )

        annotation = AnnotationService.get_annotations_for_task(
            db_session,
            workflow["tasks"][0].id,
        )[0]
        annotation.ai_suggested_label = "refund request"
        annotation.ai_confidence = 0.66
        db_session.flush()

        _filename, rows = ExportService.build_job_export(
            db_session,
            workflow["job"].id,
            include_unapproved=True,
        )

        assert rows[0]["ai_agreement"] == "True"
        assert rows[0]["ai_confidence"] == 0.66

    def test_missing_jobs_are_reported(self, db_session):
        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            ExportService.build_job_export(db_session, 999999)


class TestDatasetExport:
    """Row building for every job of a dataset."""

    def test_dataset_export_combines_all_jobs(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM, PENDING_ITEM),
        )

        _filename, rows = ExportService.build_dataset_export(
            db_session,
            workflow["dataset"].id,
            include_unapproved=True,
        )

        assert len(rows) == 2
        assert {row["job_id"] for row in rows} == {workflow["job"].id}
        assert {row["dataset_id"] for row in rows} == {workflow["dataset"].id}

        filename, _rows = ExportService.build_dataset_export(
            db_session,
            workflow["dataset"].id,
        )

        assert filename == "customer-support-tickets-annotations.csv"

    def test_missing_datasets_are_reported(self, db_session):
        with pytest.raises(NotFoundError, match=r"Dataset not found\."):
            ExportService.build_dataset_export(db_session, 999999)


class TestExportSerialisation:
    """CSV serialisation and file naming."""

    def test_csv_contains_a_header_and_one_row_per_annotation(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM,),
        )

        _filename, rows = ExportService.build_job_export(
            db_session,
            workflow["job"].id,
            include_unapproved=True,
        )

        csv_text = ExportService.to_csv(rows)
        lines = csv_text.strip().splitlines()

        assert lines[0] == ",".join(EXPORT_COLUMNS)
        assert len(lines) == 2
        assert "refund request" in lines[1]
        assert csv_text.endswith("\r\n")

    def test_csv_quotes_delimiters_inside_labels(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled_workflow(
            db_session,
            accounts,
            build_workflow,
            (APPROVED_ITEM,),
        )

        annotation = AnnotationService.get_annotations_for_task(
            db_session,
            workflow["tasks"][0].id,
        )[0]
        annotation.label = "refund, escalated"
        db_session.flush()

        _filename, rows = ExportService.build_job_export(
            db_session,
            workflow["job"].id,
            include_unapproved=True,
        )

        assert '"refund, escalated"' in ExportService.to_csv(rows)

    def test_empty_exports_still_produce_a_header(self, db_session):
        assert ExportService.to_csv([]).strip() == ",".join(EXPORT_COLUMNS)

    @pytest.mark.parametrize(
        ("title", "expected"),
        [
            ("Customer Support Tickets", "customer-support-tickets-annotations.csv"),
            (
                "  Intent Classification Round 1  ",
                "intent-classification-round-1-annotations.csv",
            ),
            ("Refunds (2026) / Q3", "refunds-2026-q3-annotations.csv"),
            ("", "export-annotations.csv"),
            ("---", "export-annotations.csv"),
        ],
    )
    def test_file_names_are_slugified(self, title, expected):
        assert ExportService.build_filename(title) == expected
