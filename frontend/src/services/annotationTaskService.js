/**
 * Annotation task API calls.
 *
 * An annotation task is one unit of labeling work (a record, sentence or image
 * reference) inside a labeling job. Dataset owners create and assign tasks;
 * annotators receive the tasks assigned to them.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List annotation tasks, optionally restricted to one labeling job.
 *
 * @param {object} [filters] Optional filters.
 * @param {number|string} [filters.jobId] Only tasks of this job.
 * @returns {Promise<Array<object>>} Tasks visible to the authenticated role.
 */
export async function getTasks(filters = {}) {
    return request(
        `/api/tasks${buildQueryString({ job_id: filters.jobId })}`
    );
}


/**
 * List the tasks of one labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<Array<object>>} The tasks of that job.
 */
export async function getTasksForJob(jobId) {
    return request(`/api/tasks/job/${jobId}`);
}


/**
 * Retrieve a single annotation task.
 *
 * @param {number|string} taskId Annotation task identifier.
 * @returns {Promise<object>} The requested task.
 */
export async function getTask(taskId) {
    return request(`/api/tasks/${taskId}`);
}


/**
 * Create one annotation task.
 *
 * @param {object} taskData Payload with job_id, input_text, assigned_to.
 * @returns {Promise<object>} The created task.
 */
export async function createTask(taskData) {
    return request("/api/tasks", {
        method: "POST",
        body: taskData,
    });
}


/**
 * Create many annotation tasks in one request.
 *
 * @param {object} payload Payload with job_id, items, assigned_to.
 * @returns {Promise<Array<object>>} The created tasks.
 */
export async function createTasksBulk(payload) {
    return request("/api/tasks/bulk", {
        method: "POST",
        body: {
            skip_duplicates: true,
            ...payload,
        },
    });
}


/**
 * Update the record, status or assignment of a task.
 *
 * @param {number|string} taskId Annotation task identifier.
 * @param {object} taskData Fields to change.
 * @returns {Promise<object>} The updated task.
 */
export async function updateTask(taskId, taskData) {
    return request(`/api/tasks/${taskId}`, {
        method: "PUT",
        body: taskData,
    });
}


/**
 * Hand a task over to an annotator.
 *
 * @param {number|string} taskId Annotation task identifier.
 * @param {number|string} assignedTo Annotator user identifier.
 * @returns {Promise<object>} The updated task.
 */
export async function assignTask(taskId, assignedTo) {
    return request(`/api/tasks/${taskId}/assign`, {
        method: "POST",
        body: { assigned_to: Number(assignedTo) },
    });
}


/**
 * Delete a task that has not been approved yet.
 *
 * @param {number|string} taskId Annotation task identifier.
 * @returns {Promise<null>} Null when the task has been deleted.
 */
export async function deleteTask(taskId) {
    return request(`/api/tasks/${taskId}`, {
        method: "DELETE",
    });
}

/** Create tasks from records already imported into a dataset. */
export async function importDatasetRecords(payload) {
    return request("/api/tasks/import-dataset", {
        method: "POST",
        body: payload,
    });
}
