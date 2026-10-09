"""Tests for the production dataset upload and import workflow."""

import asyncio
import io

import pytest
from fastapi import UploadFile
from openpyxl import Workbook

from backend.app.models.dataset import Dataset
from backend.app.services.dataset_import_service import DatasetImportService


def make_upload(filename: str, content: bytes) -> UploadFile:
    """Build an in-memory upload identical to FastAPI's file object."""
    return UploadFile(filename=filename, file=io.BytesIO(content))


def test_csv_import_persists_normalized_records(db_session):
    """CSV upload stores each non-empty source row with metadata."""
    dataset = Dataset(
        title="Support Tickets",
        description="Customer support records for intent classification.",
        dataset_type="Natural Language Processing",
        owner_id=1,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    count = asyncio.run(
        DatasetImportService.import_file(
            db_session,
            dataset,
            make_upload(
                "tickets.csv",
                (
                    b"id,text,priority\n"
                    b"1,Refund requested,high\n"
                    b"2,,low\n"
                    b"3,Delivery late,medium\n"
                ),
            ),
        )
    )

    assert count == 2
    assert dataset.record_count == 2
    assert dataset.source_filename == "tickets.csv"
    assert dataset.source_format == "csv"


def test_json_import_honours_text_column(db_session):
    """JSON object arrays use the explicitly selected text field."""
    dataset = Dataset(
        title="Reviews",
        description="Customer reviews for sentiment labeling.",
        dataset_type="Natural Language Processing",
        owner_id=1,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    count = asyncio.run(
        DatasetImportService.import_file(
            db_session,
            dataset,
            make_upload(
                "reviews.json",
                (
                    b'[{"review":"Great phone","label":"positive"},'
                    b'{"review":"Poor battery","label":"negative"}]'
                ),
            ),
            text_column="review",
        )
    )

    assert count == 2
    assert dataset.record_count == 2


def test_import_requires_explicit_replace_for_existing_records(db_session):
    """A second upload is rejected unless replacement is explicit."""
    dataset = Dataset(
        title="Tickets",
        description="Ticket records for labeling.",
        dataset_type="NLP",
        owner_id=1,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    upload = make_upload("tickets.csv", b"text\nhello\n")
    asyncio.run(DatasetImportService.import_file(db_session, dataset, upload))

    with pytest.raises(ValueError, match="already contains imported records"):
        asyncio.run(
            DatasetImportService.import_file(
                db_session,
                dataset,
                make_upload("tickets.csv", b"text\nworld\n"),
            )
        )


def test_xlsx_import_uses_first_worksheet(db_session):
    """XLSX uploads are read in streaming mode from the first worksheet."""
    dataset = Dataset(
        title="Image Notes",
        description="Text notes associated with image records.",
        dataset_type="Multimodal",
        owner_id=1,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["record_id", "text"])
    sheet.append(["a1", "Object is visible"])
    sheet.append(["a2", "Object is hidden"])
    buffer = io.BytesIO()
    workbook.save(buffer)

    count = asyncio.run(
        DatasetImportService.import_file(
            db_session,
            dataset,
            make_upload("notes.xlsx", buffer.getvalue()),
            text_column="text",
        )
    )

    assert count == 2
    assert dataset.source_format == "xlsx"
