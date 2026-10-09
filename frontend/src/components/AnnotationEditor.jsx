/**
 * Annotation editor used by the annotator workspace.
 *
 * The annotator can ask the AI enhancement for a pre-labelling suggestion,
 * accept it with one click, adjust the label, record a confidence value and
 * submit the annotation. The suggestion shown here is the same one the backend
 * stores, which is how human/AI agreement is measured later.
 *
 * The component is mounted with `key={task.id}` by its parent, so switching to
 * another task remounts it and the form restarts from :data:`EMPTY_FORM`
 * without an effect that would cascade an extra render.
 */

import { useState } from "react";

import { StatusBadge } from "./ui";
import { formatRatio } from "../utils/format";


const EMPTY_FORM = {
    label: "",
    notes: "",
    confidence: "0.8",
};


function AnnotationEditor({
    task,
    annotations,
    labelSuggestions,
    suggestion,
    onRequestSuggestion,
    onSubmit,
    onClearSuggestion,
    submitting,
}) {
    const [form, setForm] = useState(EMPTY_FORM);


    if (!task) {
        return null;
    }


    const latest = annotations[0] || null;
    const locked = task.status === "approved";


    function handleChange(event) {
        const { name, value } = event.target;

        setForm((current) => ({ ...current, [name]: value }));
    }


    function handleSubmit(event) {
        event.preventDefault();

        onSubmit({
            task_id: task.id,
            label: form.label.trim(),
            notes: form.notes.trim() || null,
            confidence: form.confidence ? Number(form.confidence) : null,
        });
    }


    return (
        <form className="content-card annotation-editor" onSubmit={handleSubmit}>
            <div className="section-heading">
                <div>
                    <p className="eyebrow">Annotate</p>

                    <h2>Task #{task.id}</h2>
                </div>

                <StatusBadge status={task.status} />
            </div>

            <blockquote className="record-text">{task.input_text}</blockquote>

            {suggestion && (
                <div className="ai-suggestion">
                    <div className="ai-suggestion-head">
                        <strong>AI suggestion</strong>

                        <span className="ai-confidence">
                            confidence {formatRatio(suggestion.confidence)}
                        </span>
                    </div>

                    <p className="ai-label">{suggestion.label}</p>

                    <p className="ai-rationale">{suggestion.rationale}</p>

                    <div className="chip-row">
                        <button
                            type="button"
                            className="chip chip-accept"
                            onClick={() =>
                                setForm((current) => ({
                                    ...current,
                                    label: suggestion.label,
                                    confidence: String(
                                        suggestion.confidence.toFixed(2)
                                    ),
                                }))
                            }
                        >
                            Use this label
                        </button>

                        {suggestion.alternatives.map((alternative) => (
                            <button
                                key={alternative.label}
                                type="button"
                                className="chip"
                                onClick={() =>
                                    setForm((current) => ({
                                        ...current,
                                        label: alternative.label,
                                    }))
                                }
                            >
                                {alternative.label} (
                                {formatRatio(alternative.confidence)})
                            </button>
                        ))}

                        <button
                            type="button"
                            className="chip chip-ghost"
                            onClick={onClearSuggestion}
                        >
                            Dismiss
                        </button>
                    </div>
                </div>
            )}

            <label>
                Label

                <input
                    type="text"
                    name="label"
                    value={form.label}
                    onChange={handleChange}
                    list="label-suggestions"
                    minLength={1}
                    maxLength={120}
                    placeholder="e.g. billing"
                    required
                    disabled={locked}
                />

                <datalist id="label-suggestions">
                    {labelSuggestions.map((label) => (
                        <option key={label} value={label} />
                    ))}
                </datalist>
            </label>

            <label>
                Notes for the reviewer

                <textarea
                    name="notes"
                    value={form.notes}
                    onChange={handleChange}
                    rows={3}
                    maxLength={2000}
                    placeholder="Explain an unusual decision."
                    disabled={locked}
                />
            </label>

            <label>
                Your confidence (0 - 1)

                <input
                    type="number"
                    name="confidence"
                    value={form.confidence}
                    onChange={handleChange}
                    min="0"
                    max="1"
                    step="0.05"
                    disabled={locked}
                />
            </label>

            <div className="form-actions">
                <button
                    type="button"
                    className="secondary-button"
                    onClick={onRequestSuggestion}
                    disabled={submitting}
                >
                    Ask the AI assistant
                </button>

                <button
                    type="submit"
                    className="primary-button"
                    disabled={submitting || locked}
                >
                    {submitting ? "Submitting..." : "Submit annotation"}
                </button>
            </div>

            {latest && (
                <p className="editor-hint">
                    Last submitted label: <strong>{latest.label}</strong>

                    {latest.ai_suggested_label && (
                        <>
                            {" "}
                            · AI suggested{" "}
                            <strong>{latest.ai_suggested_label}</strong>
                        </>
                    )}
                </p>
            )}
        </form>
    );
}


export default AnnotationEditor;
