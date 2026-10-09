# Changelog

## 2026-10-09 — Final engineering hardening pass

### Added
- Production dataset upload pipeline for CSV, JSON, JSONL and XLSX.
- Persisted `dataset_records` source-row model with provenance metadata.
- Dataset ownership metadata and owner-scoped management.
- Labeling-job annotation type and configurable label vocabulary.
- Uploaded-record-to-task import with source-record identity preservation.
- Administrator user-management screen.
- Approved-data export screen with preview/download actions.
- As-built architecture, ER and module diagrams v2.
- OpenAPI contract v2 and API contract PDF v2.
- Backend and frontend GitHub Actions quality/deployment workflows.
- Dataset upload service tests.

### Hardened
- AI suggestions for annotators are tied to an assigned task.
- Owner/admin access checks cover dataset/job/export/review workflows.
- Legacy unsaved dataset ORM instances validate safely in response schemas.
- UTC timestamp defaults no longer use deprecated `datetime.utcnow()`.
- Uploads are bounded to 25 MB and 10,000 records.
- Manual task batches remain bounded while uploaded-record imports support controlled 1,000-record batches.

### Verification
- Backend automated suite: **214 passed, 0 failed** in the isolated verification environment.
- Frontend ESLint was clean before the dependency cache was removed for the clean-package build audit; final CI must rerun `npm ci`, `npm run lint` and `npm run build`.
