-- ============================================================
-- MIGRATION 002 - ANNOTATION WORKFLOW AND AI ENHANCEMENT
-- ============================================================
-- Run this migration on an existing Version 1 database instead of recreating
-- the whole schema:
--
--   psql "$DATABASE_URL" -f database/migrations/002_annotation_workflow.sql
--
-- The migration is additive and safe to re-run: it only creates the tables and
-- columns that the as-built application needs, including the role column that
-- was introduced with Review-I authentication.
-- ============================================================

-- 1. Users gain a role column (Review-I authentication).
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'annotator';

-- 2. Annotation tasks.
CREATE TABLE IF NOT EXISTS annotation_tasks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    assigned_to INTEGER,
    input_text TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_annotation_task_job
        FOREIGN KEY (job_id)
        REFERENCES labeling_jobs(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_annotation_task_assignee
        FOREIGN KEY (assigned_to)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_annotation_task_status
        CHECK (status IN (
            'pending', 'in_progress', 'submitted', 'approved', 'rejected'
        ))
);

-- 3. Annotations (including the AI suggestion columns).
CREATE TABLE IF NOT EXISTS annotations (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    annotator_id INTEGER NOT NULL,
    label VARCHAR(120) NOT NULL,
    notes TEXT,
    confidence DOUBLE PRECISION,
    ai_suggested_label VARCHAR(120),
    ai_confidence DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL DEFAULT 'submitted',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_annotation_task
        FOREIGN KEY (task_id)
        REFERENCES annotation_tasks(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_annotation_annotator
        FOREIGN KEY (annotator_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_annotation_status
        CHECK (status IN (
            'submitted', 'approved', 'rejected', 'needs_revision'
        ))
);

ALTER TABLE annotations
    ADD COLUMN IF NOT EXISTS ai_suggested_label VARCHAR(120);

ALTER TABLE annotations
    ADD COLUMN IF NOT EXISTS ai_confidence DOUBLE PRECISION;

-- 4. Annotation quality reviews.
CREATE TABLE IF NOT EXISTS annotation_reviews (
    id SERIAL PRIMARY KEY,
    annotation_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    decision VARCHAR(30) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_annotation_review_annotation
        FOREIGN KEY (annotation_id)
        REFERENCES annotations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_annotation_review_reviewer
        FOREIGN KEY (reviewer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_annotation_review_decision
        CHECK (decision IN ('approved', 'rejected', 'needs_revision'))
);

-- 5. Indexes for the new access paths.
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_job
    ON annotation_tasks(job_id);
CREATE INDEX IF NOT EXISTS idx_annotation_tasks_assignee
    ON annotation_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_annotations_task
    ON annotations(task_id);
CREATE INDEX IF NOT EXISTS idx_annotations_annotator
    ON annotations(annotator_id);
CREATE INDEX IF NOT EXISTS idx_annotation_reviews_annotation
    ON annotation_reviews(annotation_id);
