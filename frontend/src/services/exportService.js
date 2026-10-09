/**
 * Dataset export API calls.
 *
 * CSV exports stream a file download, while JSON exports return the standard
 * `{success, data, message}` envelope with the same rows so a preview can be
 * rendered inside the app before downloading.
 */

import { buildQueryString, downloadFile, request } from "./apiClient";


/**
 * Build the export query string for a request.
 *
 * @param {object} options Export options.
 * @param {string} [options.format] `csv` (default) or `json`.
 * @param {boolean} [options.includeUnapproved] Include unapproved labels too.
 * @returns {string} The encoded query string.
 */
function buildExportQuery(options = {}) {
    return buildQueryString({
        format: options.format || "csv",
        include_unapproved: options.includeUnapproved ? "true" : "false",
    });
}


/**
 * Preview the labeled records of a job as JSON rows.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @param {object} [options] Export options.
 * @returns {Promise<Array<object>>} The labeled rows.
 */
export async function previewJobExport(jobId, options = {}) {
    return request(
        `/api/exports/jobs/${jobId}${buildExportQuery({
            ...options,
            format: "json",
        })}`
    );
}


/**
 * Download the labeled records of a job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @param {object} [options] Export options.
 * @returns {Promise<void>} Resolves once the download has been triggered.
 */
export async function downloadJobExport(jobId, options = {}) {
    if ((options.format || "csv") === "json") {
        return previewJobExport(jobId, options);
    }

    return downloadFile(
        `/api/exports/jobs/${jobId}${buildExportQuery(options)}`,
        `job_${jobId}_labels.csv`
    );
}


/**
 * Preview the labeled records of a whole dataset as JSON rows.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @param {object} [options] Export options.
 * @returns {Promise<Array<object>>} The labeled rows.
 */
export async function previewDatasetExport(datasetId, options = {}) {
    return request(
        `/api/exports/datasets/${datasetId}${buildExportQuery({
            ...options,
            format: "json",
        })}`
    );
}


/**
 * Download the labeled records of a whole dataset.
 *
 * @param {number|string} datasetId Dataset identifier.
 * @param {object} [options] Export options.
 * @returns {Promise<void>} Resolves once the download has been triggered.
 */
export async function downloadDatasetExport(datasetId, options = {}) {
    if ((options.format || "csv") === "json") {
        return previewDatasetExport(datasetId, options);
    }

    return downloadFile(
        `/api/exports/datasets/${datasetId}${buildExportQuery(options)}`,
        `dataset_${datasetId}_labels.csv`
    );
}
