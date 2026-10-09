/**
 * Labeling job API calls.
 *
 * A labeling job (also called an annotation project) is created on top of a
 * dataset and owns the annotation tasks that annotators work through.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List labeling jobs.
 *
 * @param {object} [filters] Optional filters.
 * @param {string} [filters.status] Only jobs with this status.
 * @returns {Promise<Array<object>>} Labeling jobs visible to the caller.
 */
export async function getJobs(filters = {}) {
    return request(
        `/api/jobs${buildQueryString({ status_filter: filters.status })}`
    );
}


/**
 * Retrieve a single labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<object>} The requested job.
 */
export async function getJob(jobId) {
    return request(`/api/jobs/${jobId}`);
}


/**
 * Create a labeling job.
 *
 * @param {object} jobData Payload with dataset_id, title, description, status.
 * @returns {Promise<object>} The created job.
 */
export async function createJob(jobData) {
    return request("/api/jobs", {
        method: "POST",
        body: jobData,
    });
}


/**
 * Update an existing labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @param {object} jobData Fields to change.
 * @returns {Promise<object>} The updated job.
 */
export async function updateJob(jobId, jobData) {
    return request(`/api/jobs/${jobId}`, {
        method: "PUT",
        body: jobData,
    });
}


/**
 * Delete a labeling job and its dependent work items.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<null>} Null when the job has been deleted.
 */
export async function deleteJob(jobId) {
    return request(`/api/jobs/${jobId}`, {
        method: "DELETE",
    });
}
