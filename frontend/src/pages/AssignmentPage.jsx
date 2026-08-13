import { useEffect, useState } from "react";

import AssignmentForm from "../components/AssignmentForm";
import AssignmentList from "../components/AssignmentList";

import {
    createAssignment,
    deleteAssignment,
    getAssignments,
    updateAssignment,
} from "../services/assignmentService";

const API_BASE_URL = "http://127.0.0.1:8000";

function getAuthHeaders() {
    const token = localStorage.getItem(
        "access_token"
    );

    if (!token) {
        throw new Error(
            "Authentication token not found."
        );
    }

    return {
        Authorization: `Bearer ${token}`,
    };
}

async function getJobs() {
    const response = await fetch(
        `${API_BASE_URL}/api/jobs`,
        {
            headers: getAuthHeaders(),
        }
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load jobs: ${response.status}`
        );
    }

    return response.json();
}

async function getUsers() {
    const response = await fetch(
        `${API_BASE_URL}/api/users`,
        {
            headers: getAuthHeaders(),
        }
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load users: ${response.status}`
        );
    }

    return response.json();
}

function AssignmentPage() {
    const [assignments, setAssignments] =
        useState([]);

    const [jobs, setJobs] =
        useState([]);

    const [users, setUsers] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [formLoading, setFormLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    async function loadData() {
        setLoading(true);
        setError("");

        try {
            const [
                assignmentData,
                jobData,
                userData,
            ] = await Promise.all([
                getAssignments(),
                getJobs(),
                getUsers(),
            ]);

            setAssignments(
                assignmentData
            );

            setJobs(jobData);
            setUsers(userData);
        } catch (loadError) {
            setError(
                loadError.message ||
                "Failed to load assignment data."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
    let cancelled = false;

    const run = async () => {
        if (cancelled) {
            return;
        }

        await loadData();
    };

    void run();

    return () => {
        cancelled = true;
    };
}, []);

    async function handleCreateAssignment(
        assignmentData
    ) {
        setFormLoading(true);
        setError("");

        try {
            await createAssignment(
                assignmentData.job_id,
                assignmentData.worker_id
            );

            await loadData();
        } catch (createError) {
            setError(
                createError.message ||
                "Failed to create assignment."
            );
        } finally {
            setFormLoading(false);
        }
    }

    async function handleUpdateAssignment(
        assignment
    ) {
        const newStatus =
            window.prompt(
                "Enter new status:",
                assignment.status
            );

        if (
            newStatus === null ||
            !newStatus.trim()
        ) {
            return;
        }

        setError("");

        try {
            await updateAssignment(
                assignment.id,
                newStatus.trim()
            );

            await loadData();
        } catch (updateError) {
            setError(
                updateError.message ||
                "Failed to update assignment."
            );
        }
    }

    async function handleDeleteAssignment(
        assignmentId
    ) {
        const confirmed =
            window.confirm(
                "Delete this assignment?"
            );

        if (!confirmed) {
            return;
        }

        setError("");

        try {
            await deleteAssignment(
                assignmentId
            );

            await loadData();
        } catch (deleteError) {
            setError(
                deleteError.message ||
                "Failed to delete assignment."
            );
        }
    }

    if (loading) {
        return (
            <main className="page">
                <p>Loading assignments...</p>
            </main>
        );
    }

    return (
        <main className="page">
            <div className="page-header">
                <div>
                    <h1>Job Assignments</h1>

                    <p>
                        Assign labeling jobs to
                        annotators and manage
                        their assignment status.
                    </p>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            <AssignmentForm
                jobs={jobs}
                users={users}
                onSubmit={
                    handleCreateAssignment
                }
                loading={formLoading}
            />

            <AssignmentList
                assignments={assignments}
                jobs={jobs}
                users={users}
                onUpdate={
                    handleUpdateAssignment
                }
                onDelete={
                    handleDeleteAssignment
                }
            />
        </main>
    );
}

export default AssignmentPage;