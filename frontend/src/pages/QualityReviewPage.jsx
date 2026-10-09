/**
 * Annotation quality review screen (dataset owner / administrator).
 *
 * Reviewers work through the annotations that are still `submitted`: they see
 * the AI quality report, record a decision with a comment, and the backend
 * propagates that decision to the annotation, the task and the labeling job.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import QualityReviewPanel from "../components/QualityReviewPanel";
import {
    EmptyState,
    ErrorBanner,
    LoadingState,
    PageHeader,
    StatCard,
    SuccessBanner,
} from "../components/ui";
import { getAnnotationQuality } from "../services/aiService";
import {
    createAnnotationReview,
    getAnnotationReviews,
} from "../services/annotationReviewService";
import { getAnnotations } from "../services/annotationService";
import { getTasks } from "../services/annotationTaskService";
import { getAssignableAnnotators } from "../services/assignmentService";
import { getJobs } from "../services/jobService";
import { errorMessage, formatDateTime, indexById, jobTitle } from "../utils/format";


function QualityReviewPage() {
    const [annotations, setAnnotations] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [annotators, setAnnotators] = useState([]);
    const [reviews, setReviews] = useState([]);

    const [selectedId, setSelectedId] = useState(null);
    const [qualityReport, setQualityReport] = useState(null);

    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");


    const loadData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const [
                annotationData,
                taskData,
                jobData,
                annotatorData,
                reviewData,
            ] = await Promise.all([
                getAnnotations(),
                getTasks(),
                getJobs(),
                getAssignableAnnotators(),
                getAnnotationReviews(),
            ]);

            setAnnotations(annotationData);
            setTasks(taskData);
            setJobs(jobData);
            setAnnotators(annotatorData);
            setReviews(reviewData);
        } catch (requestError) {
            setError(
                errorMessage(
                    requestError,
                    "Unable to load the quality review workspace."
                )
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


    const tasksById = useMemo(() => indexById(tasks), [tasks]);
    const jobsById = useMemo(() => indexById(jobs), [jobs]);
    const annotatorsById = useMemo(() => indexById(annotators), [annotators]);

    const pending = useMemo(
        () => annotations.filter((annotation) => annotation.status === "submitted"),
        [annotations]
    );

    const selected =
        pending.find((annotation) => annotation.id === selectedId) || pending[0] || null;

    const selectedReviews = useMemo(
        () =>
            selected
                ? reviews
                      .filter((review) => review.annotation_id === selected.id)
                      .sort((first, second) => second.id - first.id)
                : [],
        [reviews, selected]
    );

    const counts = useMemo(
        () => ({
            pending: pending.length,
            approved: annotations.filter(
                (annotation) => annotation.status === "approved"
            ).length,
            rejected: annotations.filter(
                (annotation) => annotation.status === "rejected"
            ).length,
            revisions: annotations.filter(
                (annotation) => annotation.status === "needs_revision"
            ).length,
        }),
        [annotations, pending]
    );


    function annotatorName(annotation) {
        const annotator = annotatorsById.get(annotation.annotator_id);

        return annotator ? annotator.name : `User #${annotation.annotator_id}`;
    }


    async function handleDecision(payload) {
        setBusy(true);
        setError("");
        setNotice("");

        try {
            await createAnnotationReview(payload);
            setQualityReport(null);
            setSelectedId(null);
            await loadData();
            setNotice("Review decision recorded successfully.");
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to record the decision.")
            );
        } finally {
            setBusy(false);
        }
    }


    async function handleQualityCheck(annotationId) {
        setError("");
        setQualityReport(null);

        try {
            setQualityReport(await getAnnotationQuality(annotationId));
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to score this annotation.")
            );
        }
    }


    return (
        <section className="page">
            <PageHeader
                eyebrow="Quality control"
                title="Annotation review"
                description="Approve, reject or send annotations back with AI quality support."
                actions={
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={loadData}
                    >
                        Refresh
                    </button>
                }
            />

            <ErrorBanner message={error} />

            <SuccessBanner message={notice} />

            <div className="stat-grid stat-grid-compact">
                <StatCard
                    label="Awaiting review"
                    value={counts.pending}
                    tone="warning"
                />

                <StatCard
                    label="Approved"
                    value={counts.approved}
                    tone="positive"
                />

                <StatCard label="Rejected" value={counts.rejected} />

                <StatCard label="Needs revision" value={counts.revisions} />
            </div>

            {loading && annotations.length === 0 ? (
                <LoadingState message="Loading the review queue..." />
            ) : pending.length === 0 ? (
                <div className="content-card">
                    <EmptyState
                        title="Nothing waiting for review"
                        description="Every submitted annotation has been reviewed already."
                    />
                </div>
            ) : (
                <div className="workspace-layout">
                    <div className="workspace-side">
                        <div className="content-card queue-card">
                            <div className="section-heading">
                                <h2>Review queue</h2>

                                <span className="count-badge">
                                    {pending.length}
                                </span>
                            </div>

                            <div className="queue-list">
                                {pending.map((annotation) => (
                                    <button
                                        key={annotation.id}
                                        type="button"
                                        className={
                                            selected?.id === annotation.id
                                                ? "queue-item active"
                                                : "queue-item"
                                        }
                                        onClick={() => {
                                            setSelectedId(annotation.id);
                                            setQualityReport(null);
                                            setNotice("");
                                        }}
                                    >
                                        <span className="queue-title">
                                            {annotation.label}
                                        </span>

                                        <span className="queue-subtitle">
                                            {annotatorName(annotation)} ·{" "}
                                            {jobTitle(
                                                jobsById,
                                                tasksById.get(annotation.task_id)
                                                    ?.job_id
                                            )}
                                        </span>

                                        <span className="queue-text">
                                            {tasksById.get(annotation.task_id)
                                                ?.input_text || "—"}
                                        </span>

                                        <span className="queue-meta">
                                            {formatDateTime(
                                                annotation.created_at
                                            )}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="workspace-main">
                        {selected ? (
                            <QualityReviewPanel
                                annotation={selected}
                                task={tasksById.get(selected.task_id) || null}
                                jobTitle={jobTitle(
                                    jobsById,
                                    tasksById.get(selected.task_id)?.job_id
                                )}
                                annotatorName={annotatorName(selected)}
                                reviews={selectedReviews}
                                qualityReport={qualityReport}
                                busy={busy}
                                onDecision={handleDecision}
                                onRequestQuality={handleQualityCheck}
                            />
                        ) : (
                            <div className="content-card">
                                <EmptyState title="Select an annotation" />
                            </div>
                        )}
                    </div>
                </div>
            )}
        </section>
    );
}


export default QualityReviewPage;
