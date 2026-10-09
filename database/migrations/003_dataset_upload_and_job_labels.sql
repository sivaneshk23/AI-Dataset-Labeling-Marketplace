-- Migration 003: dataset ownership, persisted upload records and label requirements.
-- Apply this migration to an existing PostgreSQL deployment before using the
-- upload workflow. Fresh databases are created from database/schema.sql.

ALTER TABLE datasets ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS source_filename VARCHAR(255);
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS source_format VARCHAR(20);
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS source_size_bytes INTEGER;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS record_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_datasets_owner ON datasets(owner_id);

ALTER TABLE labeling_jobs ADD COLUMN IF NOT EXISTS annotation_type VARCHAR(40) NOT NULL DEFAULT 'single_label_text';
ALTER TABLE labeling_jobs ADD COLUMN IF NOT EXISTS label_options JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE TABLE IF NOT EXISTS dataset_records (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL,
    source_key VARCHAR(255),
    input_text TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dataset_record_row UNIQUE (dataset_id, row_number)
);
CREATE INDEX IF NOT EXISTS idx_dataset_records_dataset ON dataset_records(dataset_id, row_number);
ALTER TABLE annotation_tasks ADD COLUMN IF NOT EXISTS dataset_record_id INTEGER REFERENCES dataset_records(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_dataset_record ON annotation_tasks(dataset_record_id);
