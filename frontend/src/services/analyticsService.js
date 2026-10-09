/**
 * Progress tracking and analytics API calls.
 *
 * The platform summary powers the dashboard, while the per-job progress
 * snapshot powers the analytics screen and the export readiness indicators.
 */

import { request } from "./apiClient";


/**
 * Fetch the platform wide workload and quality summary.
 *
 * @returns {Promise<object>} Aggregated counters used by the dashboard.
 */
export async function getPlatformSummary() {
    return request("/api/analytics/summary");
}


/**
 * Fetch the progress snapshot of one labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<object>} Completion, approval and AI agreement metrics.
 */
export async function getJobProgress(jobId) {
    return request(`/api/analytics/jobs/${jobId}/progress`);
}
