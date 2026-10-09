/**
 * AI enhancement API calls (Day 42-59 enhancement).
 *
 * * pre-labelling suggestions for annotators,
 * * AI quality reports for submitted annotations,
 * * job level quality insights for dataset owners.
 */

import { request } from "./apiClient";


/**
 * Report which AI provider is active.
 *
 * @returns {Promise<object>} Provider name, model and confidence threshold.
 */
export async function getAIStatus() {
    return request("/api/ai/status");
}


/**
 * Request an AI label suggestion for one record.
 *
 * @param {number|string} jobId Labeling job the record belongs to.
 * @param {string} inputText Record that needs a label.
 * @param {Array<string>} [candidateLabels] Label set defined by the owner.
 * @returns {Promise<object>} Suggested label, confidence and alternatives.
 */
export async function suggestLabel(jobId, inputText, candidateLabels = [], taskId = null) {
    return request(`/api/ai/jobs/${jobId}/suggest`, {
        method: "POST",
        body: {
            task_id: taskId ? Number(taskId) : undefined,
            input_text: inputText,
            candidate_labels: candidateLabels,
        },
    });
}


/**
 * Fetch AI generated quality insights for a labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<object>} Agreement, duplicates and flagged annotations.
 */
export async function getJobInsights(jobId) {
    return request(`/api/ai/jobs/${jobId}/insights`);
}


/**
 * Score one submitted annotation and explain the detected issues.
 *
 * @param {number|string} annotationId Annotation identifier.
 * @returns {Promise<object>} Quality score, recommendation and flags.
 */
export async function getAnnotationQuality(annotationId) {
    return request(`/api/ai/annotations/${annotationId}/quality`);
}
