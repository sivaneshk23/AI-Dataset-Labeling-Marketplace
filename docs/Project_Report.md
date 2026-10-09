# Project Report — AI Dataset Labeling Marketplace

**Programme:** Semester 5 · 60-Day Full Stack Development Capstone Project
**Track:** Python (FastAPI) + React + PostgreSQL
**Author:** Sivanesh K · **Repository:** [sivaneshk23/AI-Dataset-Labeling-Marketplace](https://github.com/sivaneshk23/AI-Dataset-Labeling-Marketplace)
**Report version:** v3 (final, Review-III) · **Date:** 2026-09-20

> Formatting note (capstone Section 12.3): the printed copy of this report uses a blank header,
> a centred page number in the footer, 11–12 pt body text in a single typeface, and numbered
> headings that match the table of contents below.

## Table of Contents

1. Introduction
2. Problem Statement
3. Objectives
4. Scope
5. System Design
6. Technology Stack
7. Implementation
8. AI Enhancement (Review-III)
9. Testing
10. CI/CD Pipeline
11. Deployment
12. Security Baseline
13. Results
14. Limitations and Future Work
15. Conclusion
16. References
Appendix A — API Endpoint Inventory
Appendix B — Database Schema Summary
Appendix C — Weekly Commit Tracker

## 1. Introduction

Data labeling is the step that turns raw records into training data, and it is still largely managed
through spreadsheets, chat threads and shared drives. This project delivers a web platform that
models the whole labeling lifecycle — datasets, projects (labeling jobs), records, assignments,
labels, quality review and export — as first-class database entities with role-based access control,
an auditable workflow and automated quality assistance.

The work follows the capstone brief's three phases: an MVP (Review-I), a feature-complete product
(Review-II), and one enhancement feature integrated into the same product (Review-III). This report
is the as-built description of the final system.

## 2. Problem Statement

Machine-learning teams need accurately labeled datasets, but coordinating annotation work across
owners, annotators and reviewers is error-prone:

- records are distributed manually, so ownership and progress are unclear;
- labels are typed by hand, producing inconsistent wording for the same concept;
- reviews have no quality signal, so doubtful labels reach the exported dataset;
- there is no single artefact that shows what was labeled, by whom and with which decision.

The full problem statement, acceptance criteria and out-of-scope list are in
[`Problem_Statement.md`](Problem_Statement.md).

## 3. Objectives

1. Provide secure authentication with at least two distinct roles and role-based permissions.
2. Manage the core entities of the labeling lifecycle through REST APIs and a React interface.
3. Enforce the workflow with server-side rules (assignment, status transitions, immutability of
   approved labels) instead of relying on the UI.
4. Export only approved labels, together with the provenance of every row.
5. Add an AI-assisted annotation and quality-control capability that degrades gracefully.
6. Automate lint, tests and deployment through GitHub Actions.

## 4. Scope

**In scope:** user management and authentication; datasets; labeling jobs; annotation tasks
(single and bulk import) and assignment; annotation submission, revision and withdrawal; quality
review decisions; progress analytics; CSV export; AI label suggestions and quality insights;
CI/CD and cloud deployment configuration.

**Out of scope:** automatic labeling of every data type; model training or fine-tuning;
image/audio record handling; payments between owners and annotators; enterprise-scale distributed
processing.


## 5. System Design

### 5.1 Architecture

The system is a layered monolith. Every request passes through the same five stages, which keeps
business rules out of the HTTP layer and database code out of the business layer:

```text
React SPA (browser)
   |  HTTPS + JSON, JWT bearer token
   v
API layer        (backend/app/api)          thin routers, request and response schemas only
   v
Service layer    (backend/app/services)     workflow rules, permissions, validation, AI orchestration
   v
Repository layer (backend/app/repositories) all SQLAlchemy queries
   v
ORM models       (backend/app/models)       SQLAlchemy declarative models
   v
PostgreSQL
```

Cross-cutting concerns live in `backend/app/core`: settings validation, database session factory,
password and JWT helpers, role definitions, domain errors mapped to HTTP status codes, logging
configuration, a sliding-window rate limiter and security headers.

### 5.2 Data model

Eight tables implement the problem statement's entities:

| Table | Purpose | Key relationships |
| --- | --- | --- |
| `users` | Accounts and roles (`dataset_owner`, `annotator`, `administrator`) | Referenced by datasets, jobs, tasks, annotations, reviews |
| `datasets` | A collection of records to label | 1 : N with `labeling_jobs` |
| `labeling_jobs` | An annotation project for one dataset | N : 1 `datasets`; 1 : N `annotation_tasks` |
| `job_assignments` | Which annotator works on which job | N : 1 `labeling_jobs`, `users` |
| `annotation_tasks` | One record to label plus its status | N : 1 `labeling_jobs`; 1 : N `annotations` |
| `annotations` | A submitted label (plus AI suggestion fields) | N : 1 `annotation_tasks`, `users` |
| `annotation_reviews` | Quality decision for an annotation | N : 1 `annotations`, `users` |
| `reviews` | Rating and feedback on a labeling job | N : 1 `labeling_jobs`, `users` |

Enforced integrity: unique user email; `CHECK` constraints on every status column; cascade delete
from a task to its annotations; approved annotations are immutable (service rule). The ER diagram is
committed as `docs/diagrams/ER_Diagram_v1.png` (source `.dbml`) with the as-built version in
`docs/diagrams/ER_Diagram_v2.md`.

### 5.3 Module design

| Module | Service responsibilities | API prefix |
| --- | --- | --- |
| Authentication | register, login, profile, password hashing, token issue and verification | `/api/auth` |
| Users | list, annotator list, role change, activation, deletion | `/api/users` |
| Datasets | CRUD with owner scoping | `/api/datasets` |
| Jobs | CRUD, status lifecycle, per-dataset listing | `/api/jobs` |
| Assignments | create, list, update, delete, "my assignments" | `/api/assignments` |
| Annotation tasks | create, bulk import with duplicate detection, assign, update, delete, my tasks | `/api/tasks` |
| Annotations | submit, revise, withdraw, history | `/api/annotations` |
| Annotation reviews | approve / reject / needs-revision with workflow propagation | `/api/annotation-reviews` |
| Job reviews | rating and feedback | `/api/reviews` |
| Analytics | platform summary, per-job progress | `/api/analytics` |
| Exports | CSV for a job or a whole dataset | `/api/exports` |
| AI enhancement | provider status, label suggestion, job insights, annotation quality | `/api/ai` |


## 6. Technology Stack

| Layer | Technology | Why |
| --- | --- | --- |
| Frontend | React 19, Vite, React Router, CSS design system | Component reuse, fast dev server, no build tooling overhead |
| Backend | Python 3.11+, FastAPI, Uvicorn | Auto-generated OpenAPI docs, Pydantic validation, async-ready |
| Auth | python-jose (JWT), passlib + bcrypt | Industry standard, stateless API authentication |
| ORM | SQLAlchemy 2.0 | Declarative models, parameterised queries (no raw SQL) |
| Database | PostgreSQL 15 (SQLite in tests) | Relational integrity for the workflow entities |
| Validation | Pydantic v2 | Server-side validation on every payload |
| Testing | pytest, pytest-cov, FastAPI TestClient | Unit tests plus full-stack API workflow tests |
| Linting | Ruff (lint + format), ESLint | Enforced in CI before tests |
| CI/CD | GitHub Actions | Lint, test, then deploy, gated on `main` |
| Hosting | Render (API + PostgreSQL), Vercel (SPA) | Free tiers, blueprint driven |
| AI | Gemini API (optional), offline similarity engine | External intelligence with a zero-dependency fallback |

## 7. Implementation

### 7.1 Authentication and access control

Passwords are hashed with bcrypt before storage; login verifies the hash and issues a JWT containing
the user id and email with a configurable expiry. `get_current_user` resolves the bearer token to a
database user and `require_roles(...)` builds role-specific dependencies. Three roles are defined:
`dataset_owner` (creates datasets, jobs, tasks, reviews and exports), `annotator` (sees only
assigned tasks and own annotations) and `administrator` (platform management, user administration).
Self-registration is limited to the two operational roles; administrator accounts are created by an
existing administrator.

### 7.2 Labeling workflow

1. The owner creates a **dataset**, then a **labeling job** for it.
2. Records are imported one by one or in bulk. Bulk import normalises whitespace, rejects blank
   rows, skips duplicates already present in the job and caps a single import at 500 records.
3. Tasks are assigned to active annotator accounts; a task moves from `pending` to `in_progress`.
4. The annotator submits a label with optional notes and confidence. The service validates
   ownership, task state and label quality, stores the AI suggestion alongside the label and moves
   the task to `submitted`.
5. The owner approves, rejects or requests a revision. The decision is recorded in
   `annotation_reviews`, the annotation status is updated, the task state changes accordingly and
   the job is closed automatically once every task is approved.
6. Approved labels are exported as CSV, per job or per dataset, including the AI suggestion,
   agreement flag and reviewer comment.

### 7.3 Frontend

Eleven pages cover the three roles: sign-in and registration, dashboards, dataset and job
management, assignment, task management, the annotation workspace, quality review, analytics and
profile. Fourteen reusable components (forms, lists, the annotation editor with history, the AI
quality panel, UI primitives) keep the pages thin. A single `apiClient` module attaches the JWT,
unwraps the `{ success, data, message }` envelope, converts failures into consistent error objects
and handles expired sessions.

## 8. AI Enhancement (Review-III)

The enhancement is documented in full in [`Enhancement_Proposal.md`](Enhancement_Proposal.md).
In summary:

| Component | Location | Behaviour |
| --- | --- | --- |
| Provider registry | `services/ai/__init__.py` | Chooses Gemini when a key is configured, otherwise the offline engine; caches the choice |
| Offline provider | `services/ai/local_provider.py` | Token-frequency cosine similarity against approved records plus lexical similarity to candidate labels |
| Gemini provider | `services/ai/gemini_provider.py` | JSON prompt with the job's labels and examples, parsed defensively |
| Quality engine | `services/ai/quality.py` | Pure rule engine: label quality, confidence threshold, AI agreement, distribution dominance, repetition; scores 0 to 100 with severity-tagged flags |
| Orchestration | `services/ai_service.py` | Suggestion, candidate labels, training examples, evaluation, repetition detection, job insights and recommendations |
| UI | workspace, quality review, analytics | Suggestion panel, quality score and flags, AI coverage and agreement tiles |

Failure behaviour: any provider exception is logged and the offline engine answers instead, so the
labeling workflow never blocks. Nothing is auto-approved — a human reviewer always decides.

## 9. Testing

| Suite | Scope | Result |
| --- | --- | --- |
| Model and schema tests | ORM structure, Pydantic validation | Pass |
| Service unit tests | user, dataset, job, assignment, review, annotation, task, annotation review, export, analytics, AI | Pass |
| Provider tests | offline provider, quality engine, Gemini parsing | Pass |
| API workflow tests | end-to-end request chains through `TestClient` on an in-memory database | Pass |
| Security, config and middleware tests | rate limiter, security headers, CORS, settings validation | Pass |

- Total: **211 passing tests, 0 failures** (`pytest -q`).
- Coverage: **94% overall**; the business-logic (service) layer that the brief requires to reach 40%
  is covered as follows: `annotation_service` 98%, `annotation_task_service` 99%,
  `annotation_review_service` 98%, `export_service` 98%, `ai_service` 91%, `local_provider` 97%,
  `quality` 98%, `gemini_provider` 88%, `analytics_service` 100%, `review_service` 100%,
  `dataset_service` 100%, `job_assignment_service` 95%, `labeling_job_service` 98%,
  `user_service` 61%.
- At least one test class exists for every major module, as required for Review-II.
