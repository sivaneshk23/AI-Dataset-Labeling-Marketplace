-- AI Dataset Labeling Marketplace — PostgreSQL 15+ schema (as-built)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'annotator',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    source_filename VARCHAR(255),
    source_format VARCHAR(20),
    source_size_bytes INTEGER,
    record_count INTEGER NOT NULL DEFAULT 0,
    uploaded_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS labeling_jobs (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    annotation_type VARCHAR(40) NOT NULL DEFAULT 'single_label_text',
    label_options JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_assignments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES labeling_jobs(id) ON DELETE CASCADE,
    worker_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'assigned',
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS annotation_tasks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES labeling_jobs(id) ON DELETE CASCADE,
    dataset_record_id INTEGER REFERENCES dataset_records(id) ON DELETE SET NULL,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    input_text TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_annotation_task_status CHECK (status IN ('pending','in_progress','submitted','approved','rejected'))
);

CREATE TABLE IF NOT EXISTS annotations (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES annotation_tasks(id) ON DELETE CASCADE,
    annotator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    label VARCHAR(120) NOT NULL,
    notes TEXT,
    confidence DOUBLE PRECISION,
    ai_suggested_label VARCHAR(120),
    ai_confidence DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_annotation_status CHECK (status IN ('submitted','approved','rejected','needs_revision'))
);

CREATE TABLE IF NOT EXISTS annotation_reviews (
    id SERIAL PRIMARY KEY,
    annotation_id INTEGER NOT NULL REFERENCES annotations(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    decision VARCHAR(30) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_annotation_review_decision CHECK (decision IN ('approved','rejected','needs_revision'))
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES labeling_jobs(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
);

CREATE INDEX IF NOT EXISTS idx_datasets_owner ON datasets(owner_id);
CREATE INDEX IF NOT EXISTS idx_labeling_jobs_dataset ON labeling_jobs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_labeling_jobs_creator ON labeling_jobs(created_by);
CREATE INDEX IF NOT EXISTS idx_job_assignments_job ON job_assignments(job_id);
CREATE INDEX IF NOT EXISTS idx_job_assignments_worker ON job_assignments(worker_id);
CREATE INDEX IF NOT EXISTS idx_dataset_records_dataset ON dataset_records(dataset_id, row_number);
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_job ON annotation_tasks(job_id);
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_assignee ON annotation_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_dataset_record ON annotation_tasks(dataset_record_id);
CREATE INDEX IF NOT EXISTS idx_annotations_task ON annotations(task_id);
CREATE INDEX IF NOT EXISTS idx_annotations_annotator ON annotations(annotator_id);
CREATE INDEX IF NOT EXISTS idx_annotation_reviews_annotation ON annotation_reviews(annotation_id);
CREATE INDEX IF NOT EXISTS idx_reviews_job ON reviews(job_id);
