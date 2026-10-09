"""Safe dataset-file parsing and import service.

The capstone intentionally supports a focused, auditable input contract rather
than pretending to understand every possible dataset format. CSV, JSON/JSONL,
and XLSX are supported. Imported rows are persisted as normalized dataset
records; annotation tasks are created later from those records.
"""

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.core.errors import ConflictError, ValidationError
from backend.app.core.time import utc_now
from backend.app.models.dataset import Dataset
from backend.app.models.dataset_record import DatasetRecord
from backend.app.repositories.dataset_record_repository import DatasetRecordRepository

ALLOWED_EXTENSIONS = {".csv", ".json", ".jsonl", ".xlsx"}
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_RECORDS = 10_000
MAX_TEXT_LENGTH = 5_000


@dataclass(frozen=True)
class ParsedRecord:
    """Normalized representation of one imported source row."""

    row_number: int
    input_text: str
    source_key: str | None
    metadata: dict


class DatasetImportService:
    """Parse and persist supported dataset files with bounded resource use."""

    @staticmethod
    async def import_file(
        db: Session,
        dataset: Dataset,
        upload: UploadFile,
        text_column: str | None = None,
        replace_existing: bool = False,
    ) -> int:
        """Import rows from an uploaded CSV, JSON, JSONL or XLSX file."""
        filename = Path(upload.filename or "").name
        suffix = Path(filename).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                "Unsupported dataset format. Use CSV, JSON, JSONL or XLSX."
            )

        content = await upload.read(MAX_FILE_BYTES + 1)
        if len(content) > MAX_FILE_BYTES:
            raise ValidationError("Dataset file exceeds the 25 MB upload limit.")
        if not content:
            raise ValidationError("The uploaded dataset file is empty.")

        records = DatasetImportService._parse(
            content,
            suffix,
            text_column=text_column,
        )

        if not records:
            raise ValidationError("The dataset contains no non-empty records.")
        if len(records) > MAX_RECORDS:
            raise ValidationError(
                f"Dataset contains more than the {MAX_RECORDS:,}-record limit."
            )

        if replace_existing:
            DatasetRecordRepository.delete_by_dataset(db, dataset.id)
        elif DatasetRecordRepository.count_by_dataset(db, dataset.id) > 0:
            raise ConflictError(
                "This dataset already contains imported records. Choose replace "
                "existing records explicitly to re-import the file."
            )

        db_records = [
            DatasetRecord(
                dataset_id=dataset.id,
                row_number=record.row_number,
                source_key=record.source_key,
                input_text=record.input_text,
                metadata_json=record.metadata,
            )
            for record in records
        ]
        DatasetRecordRepository.create_many(db, db_records)

        dataset.source_filename = filename
        dataset.source_format = suffix.lstrip(".")
        dataset.source_size_bytes = len(content)
        dataset.record_count = len(db_records)
        dataset.uploaded_at = utc_now()
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return len(db_records)

    @staticmethod
    def _parse(
        content: bytes, suffix: str, text_column: str | None
    ) -> list[ParsedRecord]:
        """Parse a supported file into normalized records."""
        try:
            if suffix == ".csv":
                return DatasetImportService._parse_csv(content, text_column)
            if suffix == ".jsonl":
                return DatasetImportService._parse_jsonl(content, text_column)
            if suffix == ".json":
                return DatasetImportService._parse_json(content, text_column)
            return DatasetImportService._parse_xlsx(content, text_column)
        except UnicodeDecodeError as error:
            raise ValidationError("Dataset text must be UTF-8 encoded.") from error
        except (json.JSONDecodeError, ValueError, KeyError) as error:
            raise ValidationError(f"Could not parse dataset: {error}") from error

    @staticmethod
    def _parse_csv(content: bytes, text_column: str | None) -> list[ParsedRecord]:
        """Parse a CSV with a header row."""
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise ValidationError("CSV must contain a header row.")
        return DatasetImportService._rows_from_dicts(
            reader,
            reader.fieldnames,
            text_column,
        )

    @staticmethod
    def _parse_jsonl(content: bytes, text_column: str | None) -> list[ParsedRecord]:
        """Parse newline-delimited JSON objects."""
        rows = []
        for line in content.decode("utf-8-sig").splitlines():
            if line.strip():
                value = json.loads(line)
                rows.append(value)
        return DatasetImportService._normalize_json_values(rows, text_column)

    @staticmethod
    def _parse_json(content: bytes, text_column: str | None) -> list[ParsedRecord]:
        """Parse a JSON array of objects/scalars."""
        payload = json.loads(content.decode("utf-8-sig"))
        if isinstance(payload, dict):
            for key in ("records", "data", "items", "rows"):
                if isinstance(payload.get(key), list):
                    payload = payload[key]
                    break
            else:
                payload = [payload]
        if not isinstance(payload, list):
            raise ValidationError("JSON dataset must contain an array of records.")
        return DatasetImportService._normalize_json_values(payload, text_column)

    @staticmethod
    def _parse_xlsx(content: bytes, text_column: str | None) -> list[ParsedRecord]:
        """Parse the first worksheet of an XLSX workbook in read-only mode."""
        try:
            from openpyxl import load_workbook
        except ImportError as error:  # pragma: no cover - dependency is pinned
            raise ValidationError(
                "XLSX support is not installed on the server."
            ) from error

        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        try:
            sheet = workbook.active
            rows = sheet.iter_rows(values_only=True)
            headers = [
                str(value).strip() if value is not None else ""
                for value in next(rows, ())
            ]
            if not any(headers):
                raise ValidationError("XLSX must contain a header row.")
            dictionaries = (
                {
                    headers[index]: value
                    for index, value in enumerate(row)
                    if index < len(headers) and headers[index]
                }
                for row in rows
            )
            return DatasetImportService._rows_from_dicts(
                dictionaries,
                headers,
                text_column,
            )
        finally:
            workbook.close()

    @staticmethod
    def _rows_from_dicts(rows, fields, text_column: str | None) -> list[ParsedRecord]:
        """Convert mapping rows to normalized records."""
        selected = DatasetImportService._select_text_column(fields, text_column)
        normalized: list[ParsedRecord] = []
        for row_number, row in enumerate(rows, start=1):
            if len(normalized) >= MAX_RECORDS + 1:
                break
            if not isinstance(row, dict):
                raise ValidationError("Every tabular record must be an object/row.")
            value = row.get(selected)
            text = DatasetImportService._coerce_text(value)
            if not text:
                continue
            normalized.append(
                ParsedRecord(
                    row_number=row_number,
                    input_text=text,
                    source_key=str(row.get("id") or row.get("key") or row_number),
                    metadata={
                        str(key): DatasetImportService._json_safe(value)
                        for key, value in row.items()
                        if key != selected
                    },
                )
            )
        return normalized

    @staticmethod
    def _normalize_json_values(
        values: list, text_column: str | None
    ) -> list[ParsedRecord]:
        """Convert JSON values to normalized records."""
        if not values:
            return []
        if all(isinstance(value, dict) for value in values):
            fields = list(dict.fromkeys(key for value in values for key in value))
            return DatasetImportService._rows_from_dicts(values, fields, text_column)

        if text_column:
            raise ValidationError(
                "text_column is only valid for object-based datasets."
            )

        result: list[ParsedRecord] = []
        for row_number, value in enumerate(values, start=1):
            text = DatasetImportService._coerce_text(value)
            if text:
                result.append(ParsedRecord(row_number, text, str(row_number), {}))
        return result

    @staticmethod
    def _select_text_column(fields, requested: str | None) -> str:
        """Select the requested text column or the first useful string field."""
        clean_fields = [str(field).strip() for field in fields if str(field).strip()]
        if requested:
            if requested not in clean_fields:
                raise ValidationError(
                    f"text_column '{requested}' was not found. "
                    f"Available columns: {', '.join(clean_fields)}"
                )
            return requested
        preferred = (
            "text",
            "input_text",
            "content",
            "review",
            "sentence",
            "comment",
            "description",
        )
        for field in preferred:
            for actual in clean_fields:
                if actual.lower() == field:
                    return actual
        return clean_fields[0]

    @staticmethod
    def _coerce_text(value) -> str:
        """Turn a scalar source value into bounded annotation text."""
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        else:
            text = str(value)
        cleaned = " ".join(text.split())
        return cleaned[:MAX_TEXT_LENGTH]

    @staticmethod
    def _json_safe(value):
        """Convert metadata values into JSON-serializable primitives."""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return str(value)
