/**
 * Annotation (submitted label) API calls.
 *
 * When a label is submitted the backend stores the AI suggestion that was on
 * screen as well, which lets the platform compute human/AI agreement.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List annotations, optionally restricted to one labeling job.
 *
 * @param {object} [filters] Optional filters.
 * @param {number|string} [filters.jobId] Only annotations of this job.
 * @returns {Promise<Array<object>>} Annotations visible to the caller.
 */
export async function getAnnotations(filters = {}) {
    return request(
        `/api/annotations${buildQueryString({ job_id: filters.jobId })}`
    );
}


/**
 * List the annotation attempts recorded for one task.
 *
 * @param {number|string} taskId Annotation task identifier.
 * @returns {Promise<Array<object>>} The annotation history of the task.
 */
export async function getAnnotationsForTask(taskId) {
    return request(`/api/annotations/task/${taskId}`);
}


/**
 * List the annotations submitted for one labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<Array<object>>} The annotations of that job.
 */
export async function getAnnotationsForJob(jobId) {
    return request(`/api/annotations/job/${jobId}`);
}


/**
 * Retrieve a single annotation.
 *
 * @param {number|string} annotationId Annotation identifier.
 * @returns {Promise<object>} The requested annotation.
 */
export async function getAnnotation(annotationId) {
    return request(`/api/annotations/${annotationId}`);
}


/**
 * Submit a label for an annotation task.
 *
 * @param {object} annotationData Payload: task_id, label, notes, confidence.
 * @returns {Promise<object>} The created annotation.
 */
export async function submitAnnotation(annotationData) {
    return request("/api/annotations", {
        method: "POST",
        body: annotationData,
    });
}


/**
 * Revise a label that has not been approved yet.
 *
 * @param {number|string} annotationId Annotation identifier.
 * @param {object} annotationData Fields to change.
 * @returns {Promise<object>} The updated annotation.
 */
export async function updateAnnotation(annotationId, annotationData) {
    return request(`/api/annotations/${annotationId}`, {
        method: "PUT",
        body: annotationData,
    });
}


/**
 * Withdraw a submitted annotation.
 *
 * @param {number|string} annotationId Annotation identifier.
 * @returns {Promise<null>} Null when the annotation has been withdrawn.
 */
export async function deleteAnnotation(annotationId) {
    return request(`/api/annotations/${annotationId}`, {
        method: "DELETE",
    });
}
