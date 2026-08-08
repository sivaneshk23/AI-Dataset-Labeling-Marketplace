-- ============================================================
-- AI DATASET LABELING MARKETPLACE
-- DATABASE SCHEMA - VERSION 1
-- ============================================================

-- USERS
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- DATASETS
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- LABELING JOBS
CREATE TABLE labeling_jobs (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_labeling_job_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES datasets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_labeling_job_creator
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- JOB ASSIGNMENTS
CREATE TABLE job_assignments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    worker_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'assigned',
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assignment_job
        FOREIGN KEY (job_id)
        REFERENCES labeling_jobs(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_worker
        FOREIGN KEY (worker_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- REVIEWS
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_job
        FOREIGN KEY (job_id)
        REFERENCES labeling_jobs(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_review_reviewer
        FOREIGN KEY (reviewer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_review_rating
        CHECK (rating BETWEEN 1 AND 5)
);
