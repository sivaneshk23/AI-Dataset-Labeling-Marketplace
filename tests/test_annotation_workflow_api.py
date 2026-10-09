"""End-to-end API workflow tests for the annotation platform.

These tests drive the whole stack the way a reviewer does - HTTP request ->
thin router -> service -> repository -> ORM -> database -> back to the client -
using the in-memory SQLite session from ``tests/conftest.py``. They complement
the service level unit tests by proving that the modules talk to each other:

1. authentication and role based permissions,
2. dataset and labeling job lifecycle,
3. annotation task creation, bulk import and assignment,
4. annotator submission, quality review and the resulting status changes,
5. analytics, dataset export and the AI enhancement endpoints.

Everything asserted here is a requirement from the capstone brief (Review-II
functionality checklist, Section 9.1) or from ``docs/Problem_Statement.md``.
"""

import pytest

pytestmark = pytest.mark.integration

DATASETS = "/api/datasets"
JOBS = "/api/jobs"
TASKS = "/api/tasks"
ASSIGNMENTS = "/api/assignments"
ANNOTATIONS = "/api/annotations"
ANNOTATION_REVIEWS = "/api/annotation-reviews"
REVIEWS = "/api/reviews"
ANALYTICS = "/api/analytics"
EXPORTS = "/api/exports"
AI = "/api/ai"

RECORDS = (
    "Delivery driver left the parcel at the front door.",
    "The invoice total does not match the purchase order.",
    "Customer asked for a refund because the item arrived damaged.",
)


def payload(response):
    """Return the `data` field of a successful response envelope.

    Args:
        response: A ``TestClient`` response object.

    Returns:
        The unwrapped ``data`` value.
    """
    body = response.json()

    assert body["success"] is True, body

    return body["data"]


def create_dataset(client, headers, title="Customer Support Tickets"):
    """Create a dataset through the API and return it."""
    response = client.post(
        DATASETS,
        headers=headers,
        json={
            "title": title,
            "description": "Support conversations labelled by intent.",
            "dataset_type": "Natural Language Processing",
        },
    )

    assert response.status_code == 201, response.text

    return payload(response)


def create_job(client, headers, dataset_id, title="Intent Classification Round 1"):
    """Create a labeling job through the API and return it."""
    response = client.post(
        JOBS,
        headers=headers,
        json={
            "title": title,
            "description": "Label each ticket with its primary intent.",
            "status": "open",
            "dataset_id": dataset_id,
        },
    )

    assert response.status_code == 201, response.text

    return payload(response)


def create_task(client, headers, job_id, input_text=RECORDS[0], assigned_to=None):
    """Create a single annotation task through the API and return it."""
    response = client.post(
        TASKS,
        headers=headers,
        json={
            "job_id": job_id,
            "input_text": input_text,
            "assigned_to": assigned_to,
        },
    )

    assert response.status_code == 201, response.text

    return payload(response)


@pytest.fixture()
def dataset(client, auth):
    """Persist a dataset owned by the dataset owner account."""
    return create_dataset(client, auth["dataset_owner"])


@pytest.fixture()
def job(client, auth, dataset):
    """Persist a labeling job that belongs to the dataset fixture."""
    return create_job(client, auth["dataset_owner"], dataset["id"])


@pytest.fixture()
def task(client, auth, accounts, job):
    """Persist an annotation task assigned to the first annotator."""
    return create_task(
        client,
        auth["dataset_owner"],
        job["id"],
        assigned_to=accounts["annotator"].id,
    )


class TestAuthentication:
    """Registration, login and role based access control."""

    def test_health_and_root_endpoints_report_service_status(self, client):
        """Both liveness endpoints answer without authentication."""
        for path in ("/health", "/api/health"):
            response = client.get(path)

            assert response.status_code == 200
            assert response.json()["data"]["status"] == "healthy"

        root = client.get("/")

        assert root.status_code == 200
        assert payload(root)["docs"] == "/docs"

    def test_register_login_and_read_current_account(self, client):
        """A new annotator can register, log in and read their own profile."""
        registration = client.post(
            "/api/auth/register",
            json={
                "name": "New Annotator",
                "email": "new.annotator@marketplace.dev",
                "password": "Password123",
                "role": "annotator",
            },
        )

        assert registration.status_code == 201, registration.text

        created = payload(registration)

        assert created["role"] == "annotator"
        assert "hashed_password" not in created

        login = client.post(
            "/api/auth/login",
            json={
                "email": "new.annotator@marketplace.dev",
                "password": "Password123",
            },
        )

        assert login.status_code == 200, login.text

        token = payload(login)["access_token"]

        me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert me.status_code == 200
        assert payload(me)["email"] == "new.annotator@marketplace.dev"

    def test_login_rejects_wrong_password(self, client, accounts):
        """An invalid credential pair never returns a token."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": accounts["annotator"].email,
                "password": "definitely-wrong",
            },
        )

        assert response.status_code == 401
        assert response.json()["success"] is False

    def test_protected_endpoint_requires_a_token(self, client):
        """Anonymous calls to a protected route are rejected."""
        assert client.get(DATASETS).status_code == 401

    def test_annotator_cannot_manage_datasets(self, client, auth):
        """Role based permissions stop annotators from managing datasets."""
        response = client.post(
            DATASETS,
            headers=auth["annotator"],
            json={
                "title": "Not allowed",
                "description": "Annotators may not create datasets.",
                "dataset_type": "Text Classification",
            },
        )

        assert response.status_code == 403
        assert response.json()["success"] is False

    def test_admin_directory_lists_annotators(self, client, auth):
        """The annotator directory feeds every assignment screen."""
        response = client.get(
            "/api/users/annotators",
            headers=auth["dataset_owner"],
        )

        assert response.status_code == 200

        emails = {user["email"] for user in payload(response)}

        assert "annotator@marketplace.dev" in emails
        assert "admin@marketplace.dev" not in emails


class TestDatasetLifecycle:
    """Create, read, update and delete datasets."""

    def test_dataset_crud_round_trip(self, client, auth):
        """Every dataset CRUD operation persists and reads back."""
        headers = auth["dataset_owner"]

        created = create_dataset(client, headers, title="Product Reviews")

        listed = client.get(DATASETS, headers=headers)

        assert created["id"] in {item["id"] for item in payload(listed)}

        fetched = client.get(f"{DATASETS}/{created['id']}", headers=headers)

        assert payload(fetched)["title"] == "Product Reviews"

        updated = client.put(
            f"{DATASETS}/{created['id']}",
            headers=headers,
            json={
                "title": "Product Reviews v2",
                "description": "Reviews annotated with sentiment.",
                "dataset_type": "Text Classification",
            },
        )

        assert payload(updated)["title"] == "Product Reviews v2"

        deleted = client.delete(f"{DATASETS}/{created['id']}", headers=headers)

        assert deleted.status_code == 200

        missing = client.get(f"{DATASETS}/{created['id']}", headers=headers)

        assert missing.status_code == 404

    def test_dataset_upload_and_task_import_workflow(self, client, auth):
        """Uploaded CSV rows persist and can become annotation tasks."""
        headers = auth["dataset_owner"]
        dataset = create_dataset(client, headers, title="Uploaded Reviews")
        job = create_job(client, headers, dataset["id"], title="Uploaded Review Labels")

        upload = client.post(
            f"{DATASETS}/{dataset['id']}/upload",
            headers=headers,
            files={
                "file": (
                    "reviews.csv",
                    b"id,text\n1,Great product\n2,Great product\n3,Bad delivery\n",
                    "text/csv",
                )
            },
            data={"text_column": "text"},
        )

        assert upload.status_code == 201, upload.text
        assert payload(upload)["records_imported"] == 3

        imported = client.post(
            "/api/tasks/import-dataset",
            headers=headers,
            json={"dataset_id": dataset["id"], "job_id": job["id"], "limit": 1000},
        )

        assert imported.status_code == 201, imported.text
        tasks = payload(imported)
        assert len(tasks) == 3
        assert all(task["dataset_record_id"] for task in tasks)

    def test_dataset_validation_returns_field_details(self, client, auth):
        """Invalid input yields the 422 envelope with per-field messages."""
        response = client.post(
            DATASETS,
            headers=auth["dataset_owner"],
            json={"title": "x", "description": "", "dataset_type": ""},
        )

        assert response.status_code == 422

        body = response.json()

        assert body["success"] is False
        assert body["data"]


class TestJobTaskAndAssignmentWorkflow:
    """Labeling jobs, annotation tasks and job assignments."""

    def test_job_crud_and_status_filter(self, client, auth, dataset):
        """Jobs can be created, filtered, updated and deleted."""
        headers = auth["dataset_owner"]

        job = create_job(client, headers, dataset["id"], title="Sentiment Round 1")

        filtered = client.get(f"{JOBS}?status_filter=open", headers=headers)

        assert job["id"] in {item["id"] for item in payload(filtered)}

        for_job = client.get(f"{JOBS}/{job['id']}", headers=headers)

        assert payload(for_job)["dataset_id"] == dataset["id"]

        updated = client.put(
            f"{JOBS}/{job['id']}",
            headers=headers,
            json={
                "title": "Sentiment Round 1 (paused)",
                "description": "Paused while the label guide is rewritten.",
                "status": "paused",
            },
        )

        assert payload(updated)["status"] == "paused"

        deleted = client.delete(f"{JOBS}/{job['id']}", headers=headers)

        assert deleted.status_code == 200

    def test_bulk_import_skips_duplicate_records(self, client, auth, job):
        """The bulk importer stores new records and ignores duplicates."""
        headers = auth["dataset_owner"]

        request = {
            "job_id": job["id"],
            "assigned_to": None,
            "items": list(RECORDS),
            "skip_duplicates": True,
        }

        first = client.post(f"{TASKS}/bulk", headers=headers, json=request)

        assert first.status_code == 201

        imported = payload(first)

        assert len(imported) == len(RECORDS)

        # Re-importing the same records is rejected with a readable reason
        # instead of silently creating duplicates.
        second = client.post(f"{TASKS}/bulk", headers=headers, json=request)

        assert second.status_code == 400
        assert "already exists" in second.json()["message"]

        empty = client.post(
            f"{TASKS}/bulk",
            headers=headers,
            json={**request, "items": ["   "]},
        )

        assert empty.status_code == 400

    def test_task_assignment_and_annotator_visibility(
        self,
        client,
        auth,
        accounts,
        job,
    ):
        """A task can be handed over and then shows up for that annotator."""
        headers = auth["dataset_owner"]

        created = create_task(client, headers, job["id"])

        assert created["status"] == "pending"

        assigned = client.post(
            f"{TASKS}/{created['id']}/assign",
            headers=headers,
            json={"assigned_to": accounts["annotator"].id},
        )

        assert payload(assigned)["assigned_to"] == accounts["annotator"].id

        mine = client.get(f"{TASKS}/mine", headers=auth["annotator"])

        assert created["id"] in {item["id"] for item in payload(mine)}

        updated = client.put(
            f"{TASKS}/{created['id']}",
            headers=headers,
            json={"status": "in_progress", "assigned_to": None, "input_text": None},
        )

        assert payload(updated)["status"] == "in_progress"

        job_tasks = client.get(f"{TASKS}/job/{job['id']}", headers=headers)

        assert payload(job_tasks)

        removed = client.delete(f"{TASKS}/{created['id']}", headers=headers)

        assert removed.status_code == 200

    def test_assignment_lifecycle(self, client, auth, accounts, job):
        """Job assignments can be created, listed, updated and deleted."""
        headers = auth["dataset_owner"]

        created = client.post(
            ASSIGNMENTS,
            headers=headers,
            json={
                "job_id": job["id"],
                "worker_id": accounts["annotator"].id,
                "status": "assigned",
            },
        )

        assert created.status_code == 201, created.text

        assignment = payload(created)

        listed = client.get(ASSIGNMENTS, headers=headers)

        assert assignment["id"] in {item["id"] for item in payload(listed)}

        by_job = client.get(f"{ASSIGNMENTS}/job/{job['id']}", headers=headers)

        assert payload(by_job)

        mine = client.get(f"{ASSIGNMENTS}/mine", headers=auth["annotator"])

        assert assignment["id"] in {item["id"] for item in payload(mine)}

        fetched = client.get(f"{ASSIGNMENTS}/{assignment['id']}", headers=headers)

        assert payload(fetched)["status"] == "assigned"

        updated = client.put(
            f"{ASSIGNMENTS}/{assignment['id']}",
            headers=headers,
            json={"status": "completed"},
        )

        assert payload(updated)["status"] == "completed"

        removed = client.delete(f"{ASSIGNMENTS}/{assignment['id']}", headers=headers)

        assert removed.status_code == 200


class TestAnnotationAndQualityReviewWorkflow:
    """Annotator submission, revision, quality review and status propagation."""

    def test_annotation_is_approved_through_quality_review(
        self,
        client,
        auth,
        task,
        job,
    ):
        """A submitted label is reviewed and then becomes exportable."""
        submission = client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={
                "task_id": task["id"],
                "label": "delivery",
                "notes": "Parcel was left at the front door.",
                "confidence": 0.9,
            },
        )

        assert submission.status_code == 201, submission.text

        annotation = payload(submission)

        assert annotation["status"] == "submitted"

        # The AI enhancement runs inside the submission flow and records the
        # suggestion (empty until the job has examples or candidate labels).
        assert "ai_suggested_label" in annotation

        by_job = client.get(f"{ANNOTATIONS}/job/{job['id']}", headers=auth["annotator"])

        assert annotation["id"] in {item["id"] for item in payload(by_job)}

        by_task = client.get(
            f"{ANNOTATIONS}/task/{task['id']}",
            headers=auth["dataset_owner"],
        )

        assert payload(by_task)

        listing = client.get(ANNOTATIONS, headers=auth["dataset_owner"])

        assert annotation["id"] in {item["id"] for item in payload(listing)}

        revised = client.put(
            f"{ANNOTATIONS}/{annotation['id']}",
            headers=auth["annotator"],
            json={
                "label": "delivery_confirmed",
                "notes": "Confirmed by the driver.",
                "confidence": 0.95,
            },
        )

        assert payload(revised)["label"] == "delivery_confirmed"

        review = client.post(
            ANNOTATION_REVIEWS,
            headers=auth["dataset_owner"],
            json={
                "annotation_id": annotation["id"],
                "decision": "approved",
                "comment": "Matches the labelling guide.",
            },
        )

        assert review.status_code == 201, review.text

        decision = payload(review)

        fetched = client.get(
            f"{ANNOTATIONS}/{annotation['id']}",
            headers=auth["dataset_owner"],
        )

        assert payload(fetched)["status"] == "approved"

        task_after = client.get(f"{TASKS}/{task['id']}", headers=auth["dataset_owner"])

        assert payload(task_after)["status"] == "approved"

        history = client.get(
            f"{ANNOTATION_REVIEWS}/annotation/{annotation['id']}",
            headers=auth["dataset_owner"],
        )

        assert payload(history)[0]["decision"] == "approved"

        assert (
            payload(
                client.get(
                    f"{ANNOTATION_REVIEWS}/{decision['id']}",
                    headers=auth["dataset_owner"],
                )
            )["comment"]
            == "Matches the labelling guide."
        )

        assert payload(
            client.get(
                f"{ANNOTATION_REVIEWS}/job/{job['id']}",
                headers=auth["dataset_owner"],
            )
        )

        assert payload(client.get(ANNOTATION_REVIEWS, headers=auth["dataset_owner"]))

        # Only the management roles may read the review queue.
        assert (
            client.get(ANNOTATION_REVIEWS, headers=auth["annotator"]).status_code == 403
        )

        # An approved label is immutable and is reviewed only once.
        assert (
            client.put(
                f"{ANNOTATIONS}/{annotation['id']}",
                headers=auth["annotator"],
                json={"label": "changed", "notes": None, "confidence": None},
            ).status_code
            == 409
        )

        assert (
            client.post(
                ANNOTATION_REVIEWS,
                headers=auth["dataset_owner"],
                json={"annotation_id": annotation["id"], "decision": "rejected"},
            ).status_code
            == 409
        )

    def test_rework_loop_and_withdrawal(self, client, auth, accounts, job):
        """A rejected label can be corrected, and a draft can be withdrawn."""
        headers = auth["dataset_owner"]

        rework_task = create_task(
            client,
            headers,
            job["id"],
            input_text=RECORDS[1],
            assigned_to=accounts["second_annotator"].id,
        )

        submission = client.post(
            ANNOTATIONS,
            headers=auth["second_annotator"],
            json={"task_id": rework_task["id"], "label": "wrong label"},
        )

        assert submission.status_code == 201

        annotation = payload(submission)

        sent_back = client.post(
            ANNOTATION_REVIEWS,
            headers=headers,
            json={
                "annotation_id": annotation["id"],
                "decision": "needs_revision",
                "comment": "Please use one of the guide labels.",
            },
        )

        assert sent_back.status_code == 201

        current = client.get(
            f"{ANNOTATIONS}/{annotation['id']}",
            headers=headers,
        )

        assert payload(current)["status"] == "needs_revision"

        # The annotator corrects the label, which puts it back in the queue.
        corrected = client.put(
            f"{ANNOTATIONS}/{annotation['id']}",
            headers=auth["second_annotator"],
            json={"label": "invoice_mismatch"},
        )

        assert payload(corrected)["status"] == "submitted"

        # Another annotator may not touch somebody else's label.
        assert (
            client.delete(
                f"{ANNOTATIONS}/{annotation['id']}",
                headers=auth["annotator"],
            ).status_code
            == 403
        )

        withdrawn = client.delete(
            f"{ANNOTATIONS}/{annotation['id']}",
            headers=auth["second_annotator"],
        )

        assert withdrawn.status_code == 200

        assert (
            client.get(f"{ANNOTATIONS}/{annotation['id']}", headers=headers).status_code
            == 404
        )

    def test_annotation_submission_validates_task_and_label(
        self,
        client,
        auth,
        accounts,
        job,
    ):
        """Invalid or unauthorised submissions produce the right errors."""
        headers = auth["dataset_owner"]

        task = create_task(
            client,
            headers,
            job["id"],
            input_text=RECORDS[2],
            assigned_to=accounts["annotator"].id,
        )

        # A task assigned to another annotator is protected.
        assert (
            client.post(
                ANNOTATIONS,
                headers=auth["second_annotator"],
                json={"task_id": task["id"], "label": "delivery"},
            ).status_code
            == 403
        )

        # A dataset owner is not an annotator and may not submit labels.
        assert (
            client.post(
                ANNOTATIONS,
                headers=headers,
                json={"task_id": task["id"], "label": "delivery"},
            ).status_code
            == 403
        )

        # An unknown task cannot be labelled.
        assert (
            client.post(
                ANNOTATIONS,
                headers=auth["annotator"],
                json={"task_id": 999_999, "label": "delivery"},
            ).status_code
            == 404
        )


class TestAnalyticsAndExport:
    """Progress tracking and the labeled dataset download."""

    def approve_one_annotation(self, client, auth, task):
        """Submit and approve a single label, returning the annotation id."""
        submission = client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={"task_id": task["id"], "label": "delivery"},
        )

        annotation = payload(submission)

        client.post(
            ANNOTATION_REVIEWS,
            headers=auth["dataset_owner"],
            json={"annotation_id": annotation["id"], "decision": "approved"},
        )

        return annotation

    def test_job_progress_and_platform_summary(
        self,
        client,
        auth,
        task,
        job,
        dataset,
    ):
        """Analytics reflect the work that was actually persisted."""
        self.approve_one_annotation(client, auth, task)

        progress = client.get(
            f"{ANALYTICS}/jobs/{job['id']}/progress",
            headers=auth["dataset_owner"],
        )

        assert progress.status_code == 200, progress.text

        snapshot = payload(progress)

        assert snapshot["job_id"] == job["id"]
        assert snapshot["total_tasks"] >= 1
        assert snapshot["approved_tasks"] >= 1
        assert snapshot["completion_percentage"] is not None
        assert snapshot["assigned_annotators"] >= 1

        summary = client.get(f"{ANALYTICS}/summary", headers=auth["administrator"])

        assert summary.status_code == 200, summary.text

        platform = payload(summary)

        assert platform["total_users"] >= 4
        assert platform["total_datasets"] >= 1
        assert platform["total_tasks"] >= 1
        assert platform["annotation_completion_percentage"] is not None

        # Every authenticated role may read the platform summary because it
        # powers the dashboard landing page.
        assert (
            client.get(f"{ANALYTICS}/summary", headers=auth["annotator"]).status_code
            == 200
        )

    def test_exports_are_downloadable_as_csv_and_json(
        self,
        client,
        auth,
        task,
        job,
        dataset,
    ):
        """Approved labels are exported; pending work is opt-in."""
        self.approve_one_annotation(client, auth, task)

        pending_task = create_task(
            client,
            auth["dataset_owner"],
            job["id"],
            input_text=RECORDS[1],
        )

        client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={"task_id": pending_task["id"], "label": "pending"},
        )

        csv_export = client.get(
            f"{EXPORTS}/jobs/{job['id']}",
            headers=auth["dataset_owner"],
        )

        assert csv_export.status_code == 200, csv_export.text
        assert "text/csv" in csv_export.headers["content-type"]

        lines = csv_export.text.strip().splitlines()

        assert len(lines) == 2
        assert "delivery" in csv_export.text
        assert "pending" not in csv_export.text
        assert (
            "attachment"
            in csv_export.headers.get(
                "content-disposition",
                "",
            ).lower()
        )

        with_pending = client.get(
            f"{EXPORTS}/jobs/{job['id']}?include_unapproved=true",
            headers=auth["dataset_owner"],
        )

        assert "pending" in with_pending.text

        json_export = client.get(
            f"{EXPORTS}/jobs/{job['id']}?format=json",
            headers=auth["dataset_owner"],
        )

        assert json_export.status_code == 200

        rows = json_export.json()["data"]

        assert rows[0]["label"] == "delivery"
        assert rows[0]["task_id"] == task["id"]
        assert rows[0]["annotation_status"] == "approved"

        dataset_export = client.get(
            f"{EXPORTS}/datasets/{dataset['id']}?format=json",
            headers=auth["dataset_owner"],
        )

        assert dataset_export.status_code == 200
        assert dataset_export.json()["data"]

        missing_job = client.get(
            f"{EXPORTS}/jobs/999999",
            headers=auth["dataset_owner"],
        )

        assert missing_job.status_code == 404

        missing_dataset = client.get(
            f"{EXPORTS}/datasets/999999",
            headers=auth["dataset_owner"],
        )

        assert missing_dataset.status_code == 404


class TestJobRatingReviews:
    """The marketplace rating attached to a labeling job."""

    def test_review_crud_for_a_job(self, client, auth, job):
        """A rating can be recorded, listed, updated and deleted."""
        headers = auth["dataset_owner"]

        created = client.post(
            REVIEWS,
            headers=headers,
            json={
                "job_id": job["id"],
                "rating": 5,
                "comment": "Labels were consistent and fast to review.",
            },
        )

        assert created.status_code == 201, created.text

        review = payload(created)

        for_job = client.get(f"{REVIEWS}/job/{job['id']}", headers=headers)

        assert review["id"] in {item["id"] for item in payload(for_job)}

        listed = client.get(REVIEWS, headers=headers)

        assert review["id"] in {item["id"] for item in payload(listed)}

        fetched = client.get(f"{REVIEWS}/{review['id']}", headers=headers)

        assert payload(fetched)["rating"] == 5

        updated = client.put(
            f"{REVIEWS}/{review['id']}",
            headers=headers,
            json={"rating": 4, "comment": "Good, with a few label disputes."},
        )

        assert payload(updated)["rating"] == 4

        removed = client.delete(f"{REVIEWS}/{review['id']}", headers=headers)

        assert removed.status_code == 200

        assert (
            client.get(f"{REVIEWS}/{review['id']}", headers=headers).status_code == 404
        )


class TestAIEnhancement:
    """The Day 42-59 AI assisted annotation and quality enhancement."""

    def test_provider_status_is_reported(self, client, auth):
        """The status endpoint tells reviewers which engine is active."""
        response = client.get(f"{AI}/status", headers=auth["annotator"])

        assert response.status_code == 200, response.text

        status = payload(response)

        # "local-similarity" is the always-available offline engine; the
        # optional Gemini provider reports a Gemini model name instead.
        assert status["provider"]
        assert status["provider"].startswith(("local", "gemini"))
        assert 0 < status["minimum_confidence"] <= 1
        assert isinstance(status["external_provider_enabled"], bool)

    def test_label_suggestion_uses_candidate_labels(self, client, auth, task, job):
        """A suggestion is drawn from the label set supplied by the owner."""
        response = client.post(
            f"{AI}/jobs/{job['id']}/suggest",
            headers=auth["annotator"],
            json={
                "task_id": task["id"],
                "input_text": RECORDS[2],
                "candidate_labels": ["delivery", "billing", "refund"],
            },
        )

        assert response.status_code == 200, response.text

        suggestion = payload(response)

        assert suggestion["label"] in {"delivery", "billing", "refund"}
        assert 0 <= suggestion["confidence"] <= 1
        assert suggestion["provider"]
        assert suggestion["rationale"]
        assert isinstance(suggestion["alternatives"], list)

        missing_job = client.post(
            f"{AI}/jobs/999999/suggest",
            headers=auth["annotator"],
            json={"input_text": RECORDS[0], "candidate_labels": ["delivery"]},
        )

        assert missing_job.status_code == 404

    def test_suggestion_prefers_labels_learned_from_approved_work(
        self,
        client,
        auth,
        task,
        job,
    ):
        """Once labels exist, the engine proposes them without being told."""
        submission = client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={"task_id": task["id"], "label": "refund_request", "notes": "refund"},
        )

        annotation = payload(submission)

        client.post(
            ANNOTATION_REVIEWS,
            headers=auth["dataset_owner"],
            json={"annotation_id": annotation["id"], "decision": "approved"},
        )

        response = client.post(
            f"{AI}/jobs/{job['id']}/suggest",
            headers=auth["annotator"],
            json={
                "task_id": task["id"],
                "input_text": RECORDS[2],
                "candidate_labels": [],
            },
        )

        assert response.status_code == 200, response.text

        assert payload(response)["label"] == "refund_request"

    def test_job_insights_summarise_annotation_quality(
        self,
        client,
        auth,
        task,
        job,
    ):
        """Insights aggregate distribution, agreement and flags for a job."""
        submission = client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={
                "task_id": task["id"],
                "label": "delivery",
                "notes": "Left at the door.",
                "confidence": 0.4,
            },
        )

        client.post(
            ANNOTATION_REVIEWS,
            headers=auth["dataset_owner"],
            json={"annotation_id": payload(submission)["id"], "decision": "approved"},
        )

        response = client.get(
            f"{AI}/jobs/{job['id']}/insights",
            headers=auth["dataset_owner"],
        )

        assert response.status_code == 200, response.text

        insights = payload(response)

        assert insights["job_id"] == job["id"]
        assert insights["total_annotations"] >= 1
        assert insights["labelled_tasks"] >= 1
        assert insights["label_distribution"]
        assert insights["label_distribution"][0]["share"] is not None
        assert insights["annotator_stats"]
        assert isinstance(insights["recommendations"], list)
        assert insights["provider"]

        # Annotators may not read the quality dashboard.
        assert (
            client.get(
                f"{AI}/jobs/{job['id']}/insights",
                headers=auth["annotator"],
            ).status_code
            == 403
        )

        assert (
            client.get(
                f"{AI}/jobs/999999/insights", headers=auth["dataset_owner"]
            ).status_code
            == 404
        )

    def test_annotation_quality_report_is_generated(self, client, auth, task, job):
        """Every submitted label can be scored by the quality engine."""
        submission = client.post(
            ANNOTATIONS,
            headers=auth["annotator"],
            json={
                "task_id": task["id"],
                "label": "delivery",
                "notes": "Driver left it at the front door.",
                "confidence": 0.9,
            },
        )

        annotation = payload(submission)

        response = client.get(
            f"{AI}/annotations/{annotation['id']}/quality",
            headers=auth["dataset_owner"],
        )

        assert response.status_code == 200, response.text

        report = payload(response)

        assert report["annotation_id"] == annotation["id"]
        assert report["task_id"] == task["id"]
        assert 0 <= report["quality_score"] <= 100
        assert report["recommendation"]
        assert isinstance(report["flags"], list)
        assert report["provider"]

        assert (
            client.get(
                f"{AI}/annotations/999999/quality",
                headers=auth["dataset_owner"],
            ).status_code
            == 404
        )
