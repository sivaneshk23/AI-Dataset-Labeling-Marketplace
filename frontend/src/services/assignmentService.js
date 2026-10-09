/**
 * Job assignment API calls.
 *
 * An assignment links a labeling job to an annotator. The management roles see
 * every assignment while an annotator only sees their own workload.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List every job assignment (management roles only).
 *
 * @returns {Promise<Array<object>>} All assignments on the platform.
 */
export async function getAssignments() {
    return request("/api/assignments");
}


/**
 * List the assignments of the authenticated annotator.
 *
 * @returns {Promise<Array<object>>} The caller's own assignments.
 */
export async function getMyAssignments() {
    return request("/api/assignments/mine");
}


/**
 * List the assignments created for one labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<Array<object>>} The assignments of that job.
 */
export async function getAssignmentsByJob(jobId) {
    return request(`/api/assignments/job/${jobId}`);
}


/**
 * Retrieve a single assignment.
 *
 * @param {number|string} assignmentId Assignment identifier.
 * @returns {Promise<object>} The requested assignment.
 */
export async function getAssignment(assignmentId) {
    return request(`/api/assignments/${assignmentId}`);
}


/**
 * Assign a labeling job to an annotator.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @param {number|string} workerId Annotator user identifier.
 * @returns {Promise<object>} The created assignment.
 */
export async function createAssignment(jobId, workerId) {
    return request("/api/assignments", {
        method: "POST",
        body: {
            job_id: Number(jobId),
            worker_id: Number(workerId),
        },
    });
}


/**
 * Update the status of an assignment.
 *
 * @param {number|string} assignmentId Assignment identifier.
 * @param {string} status New status (assigned, in_progress, completed).
 * @returns {Promise<object>} The updated assignment.
 */
export async function updateAssignment(assignmentId, status) {
    return request(`/api/assignments/${assignmentId}`, {
        method: "PUT",
        body: { status },
    });
}


/**
 * Delete an assignment.
 *
 * @param {number|string} assignmentId Assignment identifier.
 * @returns {Promise<null>} Null when the assignment has been removed.
 */
export async function deleteAssignment(assignmentId) {
    return request(`/api/assignments/${assignmentId}`, {
        method: "DELETE",
    });
}


/**
 * List annotator accounts available for assignment.
 *
 * @returns {Promise<Array<object>>} Active annotator accounts.
 */
export async function getAssignableAnnotators() {
    return request(
        `/api/users/annotators${buildQueryString({ active_only: true })}`
    );
}
