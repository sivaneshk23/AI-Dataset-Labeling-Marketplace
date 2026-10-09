# Feature Specification — As Built

## 1. Identity and access

- Secure registration for annotators and dataset owners.
- Administrator accounts controlled by an existing administrator.
- JWT authentication and bcrypt password hashing.
- Server-side role checks.

## 2. Dataset management

- Dataset metadata CRUD.
- Owner isolation.
- Upload CSV, JSON, JSONL and XLSX.
- Automatic text-column detection or explicit `text_column` selection.
- 25 MB maximum upload size.
- 10,000 record maximum per upload.
- Source filename, format, size, row count and timestamp retained.

## 3. Annotation project configuration

- Labeling job CRUD.
- Single-label text workflow.
- Configurable allowed-label vocabulary.
- Job status lifecycle.

## 4. Task distribution

- Single task creation.
- Manual bulk creation.
- Uploaded dataset-record import.
- Source-record identity preserved so duplicate source rows are not silently collapsed.
- Annotator assignment.
- Task state transitions.

## 5. Human annotation

- Annotator-only submission endpoint.
- Assignment enforcement.
- Label, confidence and notes.
- Revision/withdrawal rules.

## 6. AI enhancement

- Offline token-frequency/cosine nearest-neighbour suggestion engine.
- Optional Gemini provider.
- Provider fallback.
- Job-specific candidate labels and labeled examples.
- Confidence and alternatives.
- Human-in-the-loop decision model.

## 7. Quality control

- AI quality score.
- Confidence checks.
- AI/human disagreement flagging.
- Rare/dominant label distribution flags.
- Repetition checks.
- Reviewer recommendation.
- Human approve/reject/needs-revision decision.

## 8. Analytics and export

- Task and annotation progress.
- AI coverage and agreement.
- Reviewer statistics.
- Approved-only CSV export.
- JSON preview.
- AI provenance columns.
