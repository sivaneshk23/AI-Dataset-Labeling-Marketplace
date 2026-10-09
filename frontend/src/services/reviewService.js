/**
 * Marketplace review API calls.
 *
 * This is the directory-level rating module (1-5 stars for a finished labeling
 * job). Annotation quality decisions are handled by
 * `annotationReviewService.js`.
 */

import { request } from "./apiClient";


/**
 * List every job review.
 *
 * @returns {Promise<Array<object>>} Reviews, newest first.
 */
export async function getReviews() {
    return request("/api/reviews");
}


/**
 * List the reviews recorded for one labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<Array<object>>} The reviews of that job.
 */
export async function getReviewsByJob(jobId) {
    return request(`/api/reviews/job/${jobId}`);
}


/**
 * Retrieve a single review.
 *
 * @param {number|string} reviewId Review identifier.
 * @returns {Promise<object>} The requested review.
 */
export async function getReview(reviewId) {
    return request(`/api/reviews/${reviewId}`);
}


/**
 * Submit a rating for a labeling job.
 *
 * @param {object} reviewData Payload with job_id, rating and optional comment.
 * @returns {Promise<object>} The created review.
 */
export async function createReview(reviewData) {
    return request("/api/reviews", {
        method: "POST",
        body: reviewData,
    });
}


/**
 * Update a review that was already submitted.
 *
 * @param {number|string} reviewId Review identifier.
 * @param {object} reviewData Fields to change (rating, comment).
 * @returns {Promise<object>} The updated review.
 */
export async function updateReview(reviewId, reviewData) {
    return request(`/api/reviews/${reviewId}`, {
        method: "PUT",
        body: reviewData,
    });
}


/**
 * Delete a review.
 *
 * @param {number|string} reviewId Review identifier.
 * @returns {Promise<null>} Null when the review has been deleted.
 */
export async function deleteReview(reviewId) {
    return request(`/api/reviews/${reviewId}`, {
        method: "DELETE",
    });
}
