/**
 * Small formatting helpers shared by the presentation layer.
 *
 * Keeping these in one place guarantees that a status or a date is rendered the
 * same way on every screen.
 */

const STATUS_LABELS = {
    pending: "Pending",
    in_progress: "In Progress",
    submitted: "Submitted",
    approved: "Approved",
    rejected: "Rejected",
    needs_revision: "Needs Revision",
    open: "Open",
    completed: "Completed",
    cancelled: "Cancelled",
    assigned: "Assigned",
    dataset_owner: "Dataset Owner",
    annotator: "Annotator",
    administrator: "Administrator",
};


/**
 * Convert a snake_case identifier into a readable label.
 *
 * @param {string} value Raw status or role value.
 * @returns {string} Human readable label.
 */
export function humanise(value) {
    if (!value) {
        return "Unknown";
    }

    if (STATUS_LABELS[value]) {
        return STATUS_LABELS[value];
    }

    return String(value)
        .replace(/_/g, " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


/**
 * Render an ISO date as a short local date and time.
 *
 * @param {string|null|undefined} value ISO timestamp.
 * @returns {string} Formatted timestamp, or a dash when unavailable.
 */
export function formatDateTime(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleString(undefined, {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}


/**
 * Render a ratio as a percentage string.
 *
 * @param {number|null|undefined} value Ratio between 0 and 1.
 * @returns {string} Percentage string, or a dash when unavailable.
 */
export function formatRatio(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    return `${Math.round(value * 100)}%`;
}


/**
 * Render a number that is already a percentage.
 *
 * @param {number|null|undefined} value Percentage value between 0 and 100.
 * @returns {string} Percentage string, or a dash when unavailable.
 */
export function formatPercent(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    return `${Math.round(value * 10) / 10}%`;
}


/**
 * Convert an unknown error into a readable message.
 *
 * @param {unknown} error Error thrown by a service call.
 * @param {string} fallback Message used when the error has no message.
 * @returns {string} Readable error text.
 */
export function errorMessage(error, fallback = "Something went wrong.") {
    if (error && typeof error.message === "string" && error.message.trim()) {
        return error.message;
    }

    return fallback;
}


/**
 * Build a lookup map from a list keyed by its `id` field.
 *
 * @param {Array<object>} items Records returned by the API.
 * @returns {Map<number, object>} Map of identifier to record.
 */
export function indexById(items = []) {
    return new Map(items.map((item) => [item.id, item]));
}


/**
 * Resolve a job title from a lookup map.
 *
 * @param {Map<number, object>} jobsById Map built with {@link indexById}.
 * @param {number} jobId Labeling job identifier.
 * @returns {string} The job title, or a fallback label.
 */
export function jobTitle(jobsById, jobId) {
    const job = jobsById.get(jobId);

    return job ? job.title : `Job #${jobId}`;
}
