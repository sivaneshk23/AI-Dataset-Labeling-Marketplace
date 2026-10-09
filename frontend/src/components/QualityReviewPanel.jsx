/**
 * Quality review panel for one submitted annotation.
 *
 * The reviewer sees the record, the submitted label, the annotator's
 * confidence, the AI suggestion and an on-demand AI quality report before
 * recording the decision that drives the annotation and task status.
 */

import { useState } from "react";

import { StatusBadge } from "./ui";
import { formatDateTime, formatPercent, formatRatio } from "../utils/format";


const DECISIONS = [
    { value: "approved", label: "Approve" },
    { value: "needs_revision", label: "Request revision" },
    { value: "rejected", label: "Reject" },
];


/**
 * Compare the submitted label with the stored AI suggestion.
 *
 * @param {object} annotation Annotation payload from the API.
 * @returns {string} "Agrees", "Differs" or a dash when no suggestion exists.
 */
function agreementLabel(annotation) {
    if (!annotation.ai_suggested_label) {
        return "—";
    }

    return annotation.ai_suggested_label.toLowerCase() ===
        annotation.label.toLowerCase()
        ? "Agrees"
        : "Differs";
}


function QualityReviewPanel({
    annotation,
    task,
    jobTitle: currentJobTitle,
    annotatorName,
    reviews,
    qualityReport,
    busy,
    onDecision,
    onRequestQuality,
}) {
    const [decision, setDecision] = useState("approved");
    const [comment, setComment] = useState("");


    function handleSubmit(event) {
        event.preventDefault();

        onDecision({
            annotation_id: annotation.id,
            decision,
            comment: comment.trim() || null,
        });

        setComment("");
        setDecision("approved");
    }


    return (
        <div className="content-card">
            <div className="section-heading">
                <div>
                    <p className="eyebrow">Quality control</p>

                    <h2>Annotation #{annotation.id}</h2>

                    <p>{currentJobTitle}</p>
                </div>

                <StatusBadge status={annotation.status} />
            </div>

            {task && (
                <blockquote className="record-text">{task.input_text}</blockquote>
            )}

            <div className="detail-grid">
                <div className="detail-card">
                    <span className="detail-label">Submitted label</span>
                    <strong>{annotation.label}</strong>
                </div>

                <div className="detail-card">
                    <span className="detail-label">Annotator confidence</span>
                    <strong>{formatRatio(annotation.confidence)}</strong>
                </div>

                <div className="detail-card">
                    <span className="detail-label">AI suggestion</span>
                    <strong>{annotation.ai_suggested_label || "—"}</strong>
                </div>

                <div className="detail-card">
                    <span className="detail-label">AI agreement</span>
                    <strong>{agreementLabel(annotation)}</strong>
                </div>

                <div className="detail-card">
                    <span className="detail-label">Annotator</span>
                    <strong>{annotatorName}</strong>
                </div>

                <div className="detail-card">
                    <span className="detail-label">Submitted at</span>
                    <strong>{formatDateTime(annotation.created_at)}</strong>
                </div>
            </div>

            {annotation.notes && (
                <p className="review-note">“{annotation.notes}”</p>
            )}

            <div className="panel-actions">
                <button
                    type="button"
                    className="secondary-button"
                    onClick={() => onRequestQuality(annotation.id)}
                    disabled={busy}
                >
                    AI quality report
                </button>
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
                                <li
                                    key={flag.code}
                                    className={`flag-${flag.severity}`}
                                >
                                    {flag.message}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}

            <form className="form-grid" onSubmit={handleSubmit}>
                <label>
                    Decision

                    <select
                        value={decision}
                        onChange={(event) => setDecision(event.target.value)}
                    >
                        {DECISIONS.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </label>

                <label>
                    Comment for the annotator

                    <textarea
                        value={comment}
                        onChange={(event) => setComment(event.target.value)}
                        rows={3}
                        maxLength={2000}
                        placeholder="Explain the decision so the annotator can improve."
                    />
                </label>

                <div className="form-actions">
                    <button
                        type="submit"
                        className="primary-button"
                        disabled={busy}
                    >
                        {busy ? "Saving..." : "Record decision"}
                    </button>
                </div>
            </form>

            <div className="review-history">
                <h3>Review history</h3>

                {reviews.length === 0 ? (
                    <p className="muted">No decision recorded yet.</p>
                ) : (
                    <ul className="plain-list">
                        {reviews.map((review) => (
                            <li key={review.id}>
                                <StatusBadge status={review.decision} />

                                <span>{review.comment || "No comment"}</span>

                                <small>
                                    {formatDateTime(review.created_at)}
                                </small>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}


export default QualityReviewPanel;
