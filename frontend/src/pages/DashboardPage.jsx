/**
 * Role aware landing screen.
 *
 * The dashboard is a real read-only view of the platform: it shows the live
 * platform summary returned by `/api/analytics/summary`, the AI provider that
 * is currently active and, depending on the role, the next action to take.
 *
 * The screen degrades to an informative error banner when the summary endpoint
 * is unavailable, so a temporary backend problem never blocks navigation.
 */

import { useCallback, useEffect, useState } from "react";

import {
    ErrorBanner,
    LoadingState,
    PageHeader,
    ProgressBar,
    StatCard,
} from "../components/ui";
import { getAIStatus } from "../services/aiService";
import { getPlatformSummary } from "../services/analyticsService";
import { errorMessage, formatRatio, humanise } from "../utils/format";


const ROLE_ACTIONS = {
    dataset_owner: [
        {
            page: "datasets",
            title: "Manage datasets",
            description: "Register the data that needs to be labeled.",
        },
        {
            page: "tasks",
            title: "Create annotation tasks",
            description: "Split a dataset into units of work for annotators.",
        },
        {
            page: "quality",
            title: "Review annotation quality",
            description: "Approve, reject or request a revision with AI support.",
        },
        {
            page: "exports",
            title: "Export labeled data",
            description: "Download the approved labels as CSV or JSON.",
        },
    ],
    administrator: [
        {
            page: "users",
            title: "Administer accounts",
            description: "Change roles, deactivate or remove accounts.",
        },
        {
            page: "analytics",
            title: "Monitor the platform",
            description: "Track workload, completion and AI agreement.",
        },
        {
            page: "quality",
            title: "Audit annotation quality",
            description: "Check that reviewer decisions stay consistent.",
        },
        {
            page: "exports",
            title: "Export labeled data",
            description: "Download approved labels for downstream training.",
        },
    ],
    annotator: [
        {
            page: "workspace",
            title: "Open my work queue",
            description: "Label the tasks assigned to you with AI pre-labelling.",
        },
        {
            page: "assignments",
            title: "My assignments",
            description: "See which labeling jobs you are working on.",
        },
    ],
};


function DashboardPage({ currentUser, onNavigate }) {
    const [summary, setSummary] = useState(null);
    const [aiStatus, setAiStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    const loadDashboard = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const [summaryData, statusData] = await Promise.all([
                getPlatformSummary(),
                getAIStatus(),
            ]);

            setSummary(summaryData);
            setAiStatus(statusData);
        } catch (requestError) {
            setError(
                errorMessage(
                    requestError,
                    "Unable to load the platform dashboard."
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

            await loadDashboard();
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [loadDashboard]);


    const role = currentUser?.role || "annotator";
    const actions = ROLE_ACTIONS[role] || ROLE_ACTIONS.annotator;
    const firstName = (currentUser?.name || "there").split(" ")[0];


    return (
        <section className="page dashboard-page">
            <PageHeader
                eyebrow="Workspace overview"
                title={`Welcome back, ${firstName}.`}
                description={
                    "Human labeling, AI assistance and quality control in "
                    + "one workflow."
                }
                actions={
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={loadDashboard}
                    >
                        Refresh
                    </button>
                }
            />

            <ErrorBanner message={error} />

            {loading && !summary ? (
                <LoadingState message="Loading platform summary..." />
            ) : (
                <>
                    <div className="stat-grid">
                        <StatCard
                            label="Datasets"
                            value={summary?.total_datasets ?? 0}
                            hint="Registered data sources"
                        />

                        <StatCard
                            label="Labeling jobs"
                            value={summary?.total_jobs ?? 0}
                            hint={`${summary?.active_jobs ?? 0} active`}
                        />

                        <StatCard
                            label="Annotation tasks"
                            value={summary?.total_tasks ?? 0}
                            hint={`${summary?.open_tasks ?? 0} still open`}
                        />

                        <StatCard
                            label="Annotations"
                            value={summary?.total_annotations ?? 0}
                            hint={
                                `${summary?.pending_reviews ?? 0} awaiting review`
                            }
                        />

                        <StatCard
                            label="Reviewer decisions"
                            value={summary?.total_reviews ?? 0}
                            hint="Approved, rejected or revised"
                        />

                        <StatCard
                            label="AI assistance"
                            value={summary?.ai_suggestions_used ?? 0}
                            hint={
                                summary?.ai_agreement_rate === null ||
                                summary?.ai_agreement_rate === undefined
                                    ? "Agreement not measured yet"
                                    : `Agreement ${summary.ai_agreement_rate}%`
                            }
                            tone="positive"
                        />
                    </div>

                    <div className="dashboard-columns">
                        <article className="content-card">
                            <h2>Labeling completion</h2>

                            <ProgressBar
                                value={
                                    summary?.annotation_completion_percentage
                                    ?? 0
                                }
                                label="Approved annotations"
                            />

                            <div className="mini-metrics">
                                {Object.entries(
                                    summary?.tasks_by_status || {}
                                ).map(([status, count]) => (
                                    <span className="mini-metric" key={status}>
                                        {humanise(status)}
                                        <strong>{count}</strong>
                                    </span>
                                ))}
                            </div>
                        </article>

                        <article className="content-card">
                            <h2>AI enhancement</h2>

                            <p className="card-lead">
                                {aiStatus
                                    ? `Active provider: ${aiStatus.provider}`
                                    : "AI provider status unavailable."}
                            </p>

                            <ul className="plain-list">
                                <li>
                                    Model:{" "}
                                    <strong>
                                        {aiStatus?.model || "not configured"}
                                    </strong>
                                </li>

                                <li>
                                    External provider:{" "}
                                    <strong>
                                        {aiStatus?.external_provider_enabled
                                            ? "enabled"
                                            : "disabled (offline provider)"}
                                    </strong>
                                </li>

                                <li>
                                    Minimum confidence:{" "}
                                    <strong>
                                        {formatRatio(
                                            aiStatus?.minimum_confidence
                                        )}
                                    </strong>
                                </li>
                            </ul>

                            {role !== "annotator" && (
                                <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={() => onNavigate("analytics")}
                                >
                                    Open AI insights
                                </button>
                            )}
                        </article>
                    </div>

                    <div className="dashboard-grid">
                        {actions.map((action) => (
                            <article
                                className="dashboard-card dashboard-card-action"
                                key={action.page}
                            >
                                <h2>{action.title}</h2>

                                <p>{action.description}</p>

                                <button
                                    type="button"
                                    className="primary-button"
                                    onClick={() => onNavigate(action.page)}
                                >
                                    Open
                                </button>
                            </article>
                        ))}
                    </div>
                </>
            )}
        </section>
    );
}

export default DashboardPage;