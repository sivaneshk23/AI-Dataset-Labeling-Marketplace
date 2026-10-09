/**
 * Annotator workspace.
 *
 * The queue on the left lists the tasks assigned to the signed-in annotator,
 * the editor on the right performs the annotation with AI pre-labelling, and
 * the history panel shows every submission plus an on-demand AI quality check.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import AnnotationEditor from "../components/AnnotationEditor";
import AnnotationHistory from "../components/AnnotationHistory";
import {
    EmptyState,
    ErrorBanner,
    LoadingState,
    PageHeader,
    StatCard,
    StatusBadge,
    SuccessBanner,
} from "../components/ui";
import {
    deleteAnnotation,
    getAnnotations,
    submitAnnotation,
} from "../services/annotationService";
import { getTasks } from "../services/annotationTaskService";
import { getAnnotationQuality, suggestLabel } from "../services/aiService";
import { getJobs } from "../services/jobService";
import { errorMessage, indexById, jobTitle } from "../utils/format";


function AnnotationWorkspacePage() {
    const [tasks, setTasks] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [annotations, setAnnotations] = useState([]);

    const [selectedTaskId, setSelectedTaskId] = useState(null);
    const [suggestion, setSuggestion] = useState(null);
    const [qualityReport, setQualityReport] = useState(null);

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");


    const loadData = useCallback(async (keepSelection = true) => {
        setLoading(true);
        setError("");

        try {
            const [taskData, jobData, annotationData] = await Promise.all([
                getTasks(),
                getJobs(),
                getAnnotations(),
            ]);

            setTasks(taskData);
            setJobs(jobData);
            setAnnotations(annotationData);

            if (!keepSelection) {
                setSelectedTaskId(null);
            }
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to load your work queue.")
            );
        } finally {
            setLoading(false);
        }
    }, []);


    useEffect(() => {
        let cancelled = false;

        async function load() {
            if (cancelled) {
                return;
            }

            await loadData();
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [loadData]);


    const selectedTask =
        tasks.find((task) => task.id === selectedTaskId) || null;


    const taskAnnotations = useMemo(
        () =>
            annotations
                .filter((annotation) => annotation.task_id === selectedTaskId)
                .sort((first, second) => second.id - first.id),
        [annotations, selectedTaskId]
    );


    const labelSuggestions = useMemo(() => {
        if (!selectedTask) {
            return [];
        }

        const labels = annotations
            .filter((annotation) => {
                const task = tasks.find((item) => item.id === annotation.task_id);

                return task && task.job_id === selectedTask.job_id;
            })
            .map((annotation) => annotation.label);

        return [...new Set(labels)].slice(0, 25);
    }, [annotations, selectedTask, tasks]);


    const counts = useMemo(
        () => ({
            assigned: tasks.length,
            submitted: tasks.filter((task) => task.status === "submitted").length,
            approved: tasks.filter((task) => task.status === "approved").length,
            rejected: tasks.filter((task) => task.status === "rejected").length,
        }),
        [tasks]
    );


    function handleSelectTask(taskId) {
        setSelectedTaskId(taskId);
        setSuggestion(null);
        setQualityReport(null);
        setNotice("");
        setError("");
    }


    async function handleRequestSuggestion() {
        if (!selectedTask) {
            return;
        }

        setError("");
        setNotice("");

        try {
            const result = await suggestLabel(
                selectedTask.job_id,
                selectedTask.input_text,
                labelSuggestions,
                selectedTask.id
            );

            setSuggestion(result);

            if (!result.label) {
                setNotice(result.rationale);
            }
        } catch (requestError) {
            setError(
                errorMessage(
                    requestError,
                    "The AI assistant is unavailable right now."
                )
            );
        }
    }


    async function handleSubmit(annotationPayload) {
        setSubmitting(true);
        setError("");
        setNotice("");

        try {
            await submitAnnotation(annotationPayload);
            setSuggestion(null);
            setQualityReport(null);
            await loadData();
            setNotice("Annotation submitted successfully.");
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to submit the annotation.")
            );
        } finally {
            setSubmitting(false);
        }
    }


    async function handleWithdraw(annotationId) {
        const confirmed = window.confirm(
            "Withdraw this annotation so you can submit a corrected label?"
        );

        if (!confirmed) {
            return;
        }

        setError("");
        setNotice("");

        try {
            await deleteAnnotation(annotationId);
            setQualityReport(null);
            await loadData();
            setNotice("Annotation withdrawn.");
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to withdraw the annotation.")
            );
        }
    }


    async function handleQualityCheck(annotationId) {
        setError("");
        setQualityReport(null);

        try {
            const report = await getAnnotationQuality(annotationId);

            setQualityReport(report);
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to score this annotation.")
            );
        }
    }


    const jobsById = indexById(jobs);


    return (
        <section className="page">
            <PageHeader
                eyebrow="Annotator workspace"
                title="My labeling queue"
                description="Label the records assigned to you, with AI pre-labelling assistance and quality feedback."
                actions={
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={() => loadData()}
                    >
                        Refresh
                    </button>
                }
            />

            <ErrorBanner message={error} />

            <SuccessBanner message={notice} />

            <div className="stat-grid stat-grid-compact">
                <StatCard label="Assigned" value={counts.assigned} />

                <StatCard label="Submitted" value={counts.submitted} />

                <StatCard
                    label="Approved"
                    value={counts.approved}
                    tone="positive"
                />

                <StatCard
                    label="Sent back"
                    value={counts.rejected}
                    tone="warning"
                />
            </div>

            {loading && tasks.length === 0 ? (
                <LoadingState message="Loading your work queue..." />
            ) : tasks.length === 0 ? (
                <div className="content-card">
                    <EmptyState
                        title="No tasks assigned to you yet"
                        description="A dataset owner has to assign annotation tasks before you can start labeling."
                    />
                </div>
            ) : (
                <div className="workspace-layout">
                    <div className="workspace-side">
                        <div className="content-card queue-card">
                            <div className="section-heading">
                                <h2>Work queue</h2>

                                <span className="count-badge">
                                    {tasks.length}
                                </span>
                            </div>

                            <div className="queue-list">
                                {tasks.map((task) => (
                                    <button
                                        key={task.id}
                                        type="button"
                                        className={
                                            selectedTaskId === task.id
                                                ? "queue-item active"
                                                : "queue-item"
                                        }
                                        onClick={() => handleSelectTask(task.id)}
                                    >
                                        <span className="queue-title">
                                            Task #{task.id}
                                        </span>

                                        <span className="queue-subtitle">
                                            {jobTitle(jobsById, task.job_id)}
                                        </span>

                                        <span className="queue-text">
                                            {task.input_text}
                                        </span>

                                        <StatusBadge status={task.status} />
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="workspace-main">
                        {selectedTask ? (
                            <>
                                <AnnotationEditor
                                    key={selectedTask.id}
                                    task={selectedTask}
                                    annotations={taskAnnotations}
                                    labelSuggestions={labelSuggestions}
                                    suggestion={suggestion}
                                    submitting={submitting}
                                    onRequestSuggestion={handleRequestSuggestion}
                                    onSubmit={handleSubmit}
                                    onClearSuggestion={() => setSuggestion(null)}
                                />

                                <AnnotationHistory
                                    key={`history-${selectedTask.id}`}
                                    annotations={taskAnnotations}
                                    qualityReport={qualityReport}
                                    busy={submitting}
                                    onWithdraw={handleWithdraw}
                                    onRequestQuality={handleQualityCheck}
                                />
                            </>
                        ) : (
                            <div className="content-card">
                                <EmptyState
                                    title="Select a task"
                                    description="Pick a record from the queue to start annotating."
                                />
                            </div>
                        )}
                    </div>
                </div>
            )}
        </section>
    );
}


export default AnnotationWorkspacePage;
