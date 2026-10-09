/**
 * Progress tracking and AI insight screen.
 *
 * Every role can see the platform summary and the progress of a labeling job;
 * the AI insight tab (agreement, duplicates and flagged records) is reserved
 * for the management roles because the endpoint enforces that permission.
 */

import { useCallback, useEffect, useState } from "react";

import {
    EmptyState,
    ErrorBanner,
    LoadingState,
    PageHeader,
    ProgressBar,
    StatCard,
} from "../components/ui";
import { getJobInsights } from "../services/aiService";
import { getJobProgress, getPlatformSummary } from "../services/analyticsService";
import { getJobs } from "../services/jobService";
import { errorMessage, formatPercent, formatRatio, humanise } from "../utils/format";


function AnalyticsPage({ currentUser }) {
    const [summary, setSummary] = useState(null);
    const [jobs, setJobs] = useState([]);
    const [jobId, setJobId] = useState("");
    const [progress, setProgress] = useState(null);
    const [insights, setInsights] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [insightsError, setInsightsError] = useState("");


    const canSeeInsights = currentUser?.role !== "annotator";


    const loadSummary = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const [summaryData, jobData] = await Promise.all([
                getPlatformSummary(),
                getJobs(),
            ]);

            setSummary(summaryData);
            setJobs(jobData);

            if (jobData.length > 0) {
                setJobId((current) => current || String(jobData[0].id));
            }
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to load platform analytics.")
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

            await loadSummary();
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [loadSummary]);


    const loadJobMetrics = useCallback(async () => {
        if (!jobId) {
            setProgress(null);
            setInsights(null);

            return;
        }

        setError("");
        setInsightsError("");

        try {
            setProgress(await getJobProgress(jobId));
        } catch (requestError) {
            setProgress(null);
            setError(
                errorMessage(requestError, "Unable to load the job progress.")
            );
        }

        if (!canSeeInsights) {
            return;
        }

        try {
            setInsights(await getJobInsights(jobId));
        } catch (requestError) {
            setInsights(null);
            setInsightsError(
                errorMessage(requestError, "Unable to load the AI insights.")
            );
        }
    }, [canSeeInsights, jobId]);


    useEffect(() => {
        let cancelled = false;

        async function load() {
            if (cancelled) {
                return;
            }

            await loadJobMetrics();
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [loadJobMetrics]);


    function handleRefresh() {
        loadSummary();
        loadJobMetrics();
    }


    return (
        <section className="page">
            <PageHeader
                eyebrow="Progress tracking"
                title="Analytics and AI insights"
                description="Workload, completion and annotation quality across the marketplace."
                actions={
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={handleRefresh}
                    >
                        Refresh
                    </button>
                }
            />

            <ErrorBanner message={error} />

            {loading && !summary ? (
                <LoadingState message="Loading analytics..." />
            ) : (
                <>
                    <div className="stat-grid">
                        <StatCard
                            label="Users"
                            value={summary?.total_users ?? 0}
                            hint={`${summary?.users_by_role?.annotator ?? 0} annotator(s)`}
                        />

                        <StatCard
                            label="Datasets"
                            value={summary?.total_datasets ?? 0}
                            hint="Registered sources"
                        />

                        <StatCard
                            label="Labeling jobs"
                            value={summary?.total_jobs ?? 0}
                            hint={`${summary?.completed_jobs ?? 0} completed`}
                        />

                        <StatCard
                            label="Annotations"
                            value={summary?.total_annotations ?? 0}
                            hint={`${summary?.open_tasks ?? 0} tasks still open`}
                        />

                        <StatCard
                            label="Reviews"
                            value={summary?.total_reviews ?? 0}
                            hint={`${summary?.pending_reviews ?? 0} pending`}
                        />

                        <StatCard
                            label="Completion"
                            value={formatPercent(
                                summary?.annotation_completion_percentage
                            )}
                            hint="Approved annotations"
                            tone="positive"
                        />
                    </div>

                    <div className="content-card">
                        <div className="section-heading">
                            <div>
                                <h2>Job progress</h2>

                                <p>Drill into one annotation project.</p>
                            </div>

                            <label className="inline-field">
                                Labeling job

                                <select
                                    value={jobId}
                                    onChange={(event) =>
                                        setJobId(event.target.value)
                                    }
                                >
                                    <option value="">Select a job</option>

                                    {jobs.map((job) => (
                                        <option key={job.id} value={job.id}>
                                            {job.title}
                                        </option>
                                    ))}
                                </select>
                            </label>
                        </div>

                        {!progress ? (
                            <EmptyState
                                title="No job selected"
                                description="Create a labeling job to unlock progress metrics."
                            />
                        ) : (
                            <>
                                <ProgressBar
                                    value={progress.completion_percentage}
                                    label="Tasks approved"
                                />

                                <div className="detail-grid">
                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Total tasks
                                        </span>

                                        <strong>{progress.total_tasks}</strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Open tasks
                                        </span>

                                        <strong>{progress.open_tasks}</strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Submitted
                                        </span>

                                        <strong>
                                            {progress.submitted_tasks}
                                        </strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Approved
                                        </span>

                                        <strong>
                                            {progress.approved_tasks}
                                        </strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Approval rate
                                        </span>

                                        <strong>
                                            {formatPercent(
                                                progress.approval_rate
                                            )}
                                        </strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Average confidence
                                        </span>

                                        <strong>
                                            {formatRatio(
                                                progress.average_confidence
                                            )}
                                        </strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Assigned annotators
                                        </span>

                                        <strong>
                                            {progress.assigned_annotators}
                                        </strong>
                                    </div>

                                    <div className="detail-card">
                                        <span className="detail-label">
                                            Average rating
                                        </span>

                                        <strong>
                                            {progress.average_rating ?? "—"}
                                        </strong>
                                    </div>
                                </div>

                                <p className="card-lead">
                                    Task status mix:{" "}
                                    {Object.entries(
                                        progress.tasks_by_status || {}
                                    )
                                        .map(
                                            ([status, count]) =>
                                                `${humanise(status)}: ${count}`
                                        )
                                        .join(" · ") || "—"}
                                </p>
                            </>
                        )}
                    </div>

                    {canSeeInsights && (
                        <div className="content-card">
                            <div className="section-heading">
                                <div>
                                    <h2>AI quality insights</h2>

                                    <p>
                                        Agreement, AI coverage and flagged
                                        records detected for the selected job.
                                    </p>
                                </div>

                                {insights && (
                                    <span className="quality-provider">
                                        {insights.provider}
                                    </span>
                                )}
                            </div>

                            <ErrorBanner message={insightsError} />

                            {!insights ? (
                                <EmptyState
                                    title="No AI insights available"
                                    description="Select a labeling job that already has submitted annotations to unlock the quality signals."
                                />
                            ) : (
                                <>
                                    <div className="stat-grid">
                                        <StatCard
                                            label="Human / AI agreement"
                                            value={formatPercent(
                                                insights.agreement_rate
                                            )}
                                            hint="Share of labels the assistant agrees with"
                                        />

                                        <StatCard
                                            label="AI coverage"
                                            value={formatPercent(
                                                insights.ai_coverage
                                            )}
                                            hint="Submissions scored by the quality engine"
                                        />

                                        <StatCard
                                            label="Average confidence"
                                            value={formatRatio(
                                                insights.average_confidence
                                            )}
                                            hint="Reported by the annotators"
                                        />

                                        <StatCard
                                            label="Duplicate rows"
                                            value={
                                                insights.duplicate_annotations
                                            }
                                            hint="Same record submitted twice"
                                            tone={
                                                insights.duplicate_annotations
                                                    ? "warning"
                                                    : "default"
                                            }
                                        />
                                    </div>
                                    <p className="card-lead">
                                        {insights.total_annotations} annotation(s)
                                        across {insights.labelled_tasks} labelled
                                        task(s); {insights.unlabelled_tasks} still
                                        waiting for a first submission.
                                    </p>

                                    <div className="chip-row">
                                        {insights.label_distribution.length ===
                                            0 && (
                                            <span className="muted">
                                                No label has been recorded yet.
                                            </span>
                                        )}

                                        {insights.label_distribution.map(
                                            (entry) => (
                                                <span
                                                    className="chip"
                                                    key={entry.label}
                                                >
                                                    {entry.label} · {entry.count}{" "}
                                                    (
                                                    {formatPercent(entry.share)}
                                                    )
                                                </span>
                                            )
                                        )}
                                    </div>
                                    <div className="review-history">
                                        <h3>Flagged annotations</h3>

                                        {insights.flagged_annotations.length ===
                                        0 ? (
                                            <p className="card-lead">
                                                No annotation fell below the
                                                quality threshold.
                                            </p>
                                        ) : (
                                            <div className="data-list">
                                                {insights.flagged_annotations.map(
                                                    (item) => (
                                                        <div
                                                            className="data-item"
                                                            key={
                                                                item.annotation_id
                                                            }
                                                        >
                                                            <div className="data-item-main">
                                                                <div className="data-item-heading">
                                                                    <strong>
                                                                        Annotation #
                                                                        {
                                                                            item.annotation_id
                                                                        }
                                                                    </strong>

                                                                    <span className="count-badge">
                                                                        score{" "}
                                                                        {
                                                                            item.quality_score
                                                                        }
                                                                    </span>
                                                                </div>

                                                                <p className="data-item-text">
                                                                    Task #
                                                                    {
                                                                        item.task_id
                                                                    }{" "}
                                                                    · label{" "}
                                                                    <strong>
                                                                        {
                                                                            item.label
                                                                        }
                                                                    </strong>
                                                                </p>

                                                                <p className="data-item-meta">
                                                                    {item.flags
                                                                        .length >
                                                                    0
                                                                        ? item.flags.join(
                                                                              ", "
                                                                          )
                                                                        : "No specific flag"}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )
                                                )}
                                            </div>
                                        )}
                                    </div>
                                    <div className="review-history">
                                        <h3>Annotator productivity</h3>

                                        {insights.annotator_stats.length === 0 ? (
                                            <p className="card-lead">
                                                No annotation has been submitted
                                                for this job yet.
                                            </p>
                                        ) : (
                                            <ul className="plain-list">
                                                {insights.annotator_stats.map(
                                                    (stat) => (
                                                        <li
                                                            className="data-item"
                                                            key={
                                                                stat.annotator_id
                                                            }
                                                        >
                                                            <div className="data-item-main">
                                                                <div className="data-item-heading">
                                                                    <strong>
                                                                        {
                                                                            stat.annotator_name
                                                                        }
                                                                    </strong>
                                                                </div>

                                                                <p className="data-item-meta">
                                                                    {
                                                                        stat.annotations
                                                                    }{" "}
                                                                    submitted ·{" "}
                                                                    {
                                                                        stat.approved
                                                                    }{" "}
                                                                    approved ·{" "}
                                                                    {formatPercent(
                                                                        stat.agreement_rate
                                                                    )}{" "}
                                                                    agreement
                                                                </p>
                                                            </div>
                                                        </li>
                                                    )
                                                )}
                                            </ul>
                                        )}
                                    </div>
                                    <div className="quality-report">
                                        <div className="quality-report-head">
                                            <h3>Recommendations</h3>
                                        </div>

                                        <ul className="plain-list">
                                            {insights.recommendations.map(
                                                (recommendation) => (
                                                    <li
                                                        className="review-note"
                                                        key={recommendation}
                                                    >
                                                        {recommendation}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    </div>
                                </>
                            )}
                        </div>
                    )}
                </>
            )}
        </section>
    );
}


export default AnalyticsPage;
