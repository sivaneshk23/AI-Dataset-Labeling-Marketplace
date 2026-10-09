/**
 * Dataset API calls.
 *
 * Datasets are the top level container of the platform: a dataset is described
 * by its type and then prepared for labeling through one or more labeling jobs.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List every dataset.
 *
 * @param {object} [filters] Optional filters.
 * @param {string} [filters.datasetType] Only datasets of this type.
 * @returns {Promise<Array<object>>} Datasets visible to the caller.
 */
export async function getDatasets(filters = {}) {
    return request(
        `/api/datasets${buildQueryString({
            dataset_type: filters.datasetType,
        })}`
    );
}


/**
 * Retrieve a single dataset.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @returns {Promise<object>} The requested dataset.
 */
export async function getDataset(datasetId) {
    return request(`/api/datasets/${datasetId}`);
}


/**
 * Create a dataset.
 *
 * @param {object} datasetData Payload with title, description, dataset_type.
 * @returns {Promise<object>} The created dataset.
 */
export async function createDataset(datasetData) {
    return request("/api/datasets", {
        method: "POST",
        body: datasetData,
    });
}


/**
 * Update an existing dataset.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @param {object} datasetData Fields to change.
 * @returns {Promise<object>} The updated dataset.
 */
export async function updateDataset(datasetId, datasetData) {
    return request(`/api/datasets/${datasetId}`, {
        method: "PUT",
        body: datasetData,
    });
}


/**
 * Delete a dataset.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @returns {Promise<null>} Null when the dataset has been deleted.
 */
export async function deleteDataset(datasetId) {
    return request(`/api/datasets/${datasetId}`, {
        method: "DELETE",
    });
}

/**
 * Upload and parse a dataset file.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @param {File} file CSV, JSON, JSONL or XLSX file.
 * @param {object} options Upload options.
 * @returns {Promise<object>} Import summary.
 */
export async function uploadDataset(datasetId, file, options = {}) {
    const formData = new FormData();
    formData.append("file", file);
    if (options.textColumn) {
        formData.append("text_column", options.textColumn);
    }
    formData.append("replace_existing", options.replaceExisting ? "true" : "false");

    return request(`/api/datasets/${datasetId}/upload`, {
        method: "POST",
        body: formData,
    });
}
