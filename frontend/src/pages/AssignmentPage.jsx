import { useCallback, useEffect, useState } from "react";

import AssignmentForm from "../components/AssignmentForm";
import AssignmentList from "../components/AssignmentList";
import {
    createAssignment,
    deleteAssignment,
    getAssignableAnnotators,
    getAssignments,
    getMyAssignments,
    updateAssignment,
} from "../services/assignmentService";
import { getJobs } from "../services/jobService";

function AssignmentPage({ currentUser }) {
    const isAnnotator = currentUser?.role === "annotator";
    const [assignments, setAssignments] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [formLoading, setFormLoading] = useState(false);
    const [error, setError] = useState("");

    const loadData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            if (isAnnotator) {
                setAssignments(await getMyAssignments());
                setJobs([]);
                setUsers([]);
                return;
            }

            const [assignmentData, jobData, userData] = await Promise.all([
                getAssignments(),
                getJobs(),
                getAssignableAnnotators(),
            ]);

            setAssignments(assignmentData);
            setJobs(jobData);
            setUsers(userData);
        } catch (loadError) {
            setError(
                loadError.message || "Failed to load assignment data."
            );
        } finally {
            setLoading(false);
        }
    }, [isAnnotator]);

    useEffect(() => {
        let cancelled = false;

        async function load() {
            if (!cancelled) {
                await loadData();
            }
        }

        void load();

        return () => {
            cancelled = true;
        };
    }, [loadData]);

    async function handleCreateAssignment(assignmentData) {
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
                createError.message || "Failed to create assignment."
            );
        } finally {
            setFormLoading(false);
        }
    }

    async function handleUpdateAssignment(assignment) {
        const newStatus = window.prompt(
            "Enter new status:",
            assignment.status
        );

        if (!newStatus?.trim()) {
            return;
        }

        setError("");

        try {
            await updateAssignment(assignment.id, newStatus.trim());
            await loadData();
        } catch (updateError) {
            setError(
                updateError.message || "Failed to update assignment."
            );
        }
    }

    async function handleDeleteAssignment(assignmentId) {
        if (!window.confirm("Delete this assignment?")) {
            return;
        }

        setError("");

        try {
            await deleteAssignment(assignmentId);
            await loadData();
        } catch (deleteError) {
            setError(
                deleteError.message || "Failed to delete assignment."
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
                    <h1>{isAnnotator ? "My Assignments" : "Job Assignments"}</h1>
                    <p>
                        {isAnnotator
                            ? "Review the labeling jobs assigned to your account."
                            : "Assign labeling jobs to annotators and manage their assignment status."}
                    </p>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            {!isAnnotator && (
                <AssignmentForm
                    jobs={jobs}
                    users={users}
                    onSubmit={handleCreateAssignment}
                    loading={formLoading}
                />
            )}

            <AssignmentList
                assignments={assignments}
                jobs={jobs}
                users={users}
                readOnly={isAnnotator}
                onUpdate={handleUpdateAssignment}
                onDelete={handleDeleteAssignment}
            />
        </main>
    );
}

export default AssignmentPage;
