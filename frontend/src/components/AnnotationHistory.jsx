/**
 * Annotation history for the selected task.
 *
 * Besides the submission log this panel renders the AI quality report
 * (`/api/ai/annotations/{id}/quality`) so an annotator can self-check a
 * submission before the reviewer looks at it.
 */

import { EmptyState, StatusBadge } from "./ui";
import { formatDateTime, formatPercent, formatRatio } from "../utils/format";


function AnnotationHistory({
    annotations,
    qualityReport,
    onWithdraw,
    onRequestQuality,
    busy,
}) {
    if (annotations.length === 0) {
        return (
            <div className="content-card">
                <h2>Submission history</h2>

                <EmptyState
                    title="Nothing submitted yet"
                    description="Your submissions for this task will appear here."
                />
            </div>
        );
    }


    return (
        <div className="content-card">
            <div className="section-heading">
                <div>
                    <h2>Submission history</h2>

                    <p>Every attempt recorded for this task.</p>
                </div>

                <span className="count-badge">{annotations.length}</span>
            </div>

            <div className="data-list">
                {annotations.map((annotation) => (
                    <article className="data-item" key={annotation.id}>
                        <div className="data-item-main">
                            <div className="data-item-heading">
                                <strong>{annotation.label}</strong>

                                <StatusBadge status={annotation.status} />
                            </div>

                            <div className="data-item-meta">
                                <span>
                                    Confidence{" "}
                                    {formatRatio(annotation.confidence)}
                                </span>

                                <span>
                                    AI suggested{" "}
                                    {annotation.ai_suggested_label || "—"}
                                </span>

                                <span>{formatDateTime(annotation.created_at)}</span>
                            </div>

                            {annotation.notes && (
                                <p className="data-item-text">
                                    {annotation.notes}
                                </p>
                            )}
                        </div>

                        <div className="data-item-actions">
                            <button
                                type="button"
                                className="secondary-button"
                                onClick={() => onRequestQuality(annotation.id)}
                                disabled={busy}
                            >
                                AI quality check
                            </button>

                            {annotation.status !== "approved" && (
                                <button
                                    type="button"
                                    className="danger-button"
                                    onClick={() => onWithdraw(annotation.id)}
                                >
                                    Withdraw
                                </button>
                            )}
                        </div>
                    </article>
                ))}
            </div>

            {qualityReport && (
                <div className="quality-report">
                    <div className="quality-report-head">
                        <strong>
                            AI quality score:{" "}
                            {formatPercent(qualityReport.quality_score)}
                        </strong>

                        <span className="quality-provider">
                            {qualityReport.provider}
                        </span>
                    </div>

                    <p className="quality-recommendation">
                        {qualityReport.recommendation}
                    </p>

                    {qualityReport.flags.length > 0 && (
                        <ul className="flag-list">
                            {qualityReport.flags.map((flag) => (
                                <li key={flag.code} className={`flag-${flag.severity}`}>
                                    {flag.message}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
}


export default AnnotationHistory;
