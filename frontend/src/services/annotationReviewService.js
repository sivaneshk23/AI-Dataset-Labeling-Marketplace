/**
 * Annotation quality review API calls.
 *
 * A quality review records the decision (approved / rejected / needs revision)
 * that a dataset owner takes on a submitted annotation. The decision drives the
 * annotation, task and job status on the backend.
 */

import { request } from "./apiClient";


/**
 * List the complete quality review history.
 *
 * @returns {Promise<Array<object>>} Every recorded review decision.
 */
export async function getAnnotationReviews() {
    return request("/api/annotation-reviews");
}


/**
 * List the review decisions recorded for one annotation.
 *
 * @param {number|string} annotationId Annotation identifier.
 * @returns {Promise<Array<object>>} The review history of that annotation.
 */
export async function getReviewsForAnnotation(annotationId) {
    return request(`/api/annotation-reviews/annotation/${annotationId}`);
}


/**
 * List the review decisions recorded for a labeling job.
 *
 * @param {number|string} jobId Labeling job identifier.
 * @returns {Promise<Array<object>>} The reviews of that job.
 */
export async function getReviewsForJob(jobId) {
    return request(`/api/annotation-reviews/job/${jobId}`);
}


/**
 * Retrieve a single quality review.
 *
 * @param {number|string} reviewId Quality review identifier.
 * @returns {Promise<object>} The requested review.
 */
export async function getAnnotationReview(reviewId) {
    return request(`/api/annotation-reviews/${reviewId}`);
}


/**
 * Record a quality decision for a submitted annotation.
 *
 * @param {object} reviewData Payload with annotation_id, decision, comment.
 * @returns {Promise<object>} The created review.
 */
export async function createAnnotationReview(reviewData) {
    return request("/api/annotation-reviews", {
        method: "POST",
        body: reviewData,
    });
}


/**
 * Delete a review decision recorded by mistake (administrator only).
 *
 * @param {number|string} reviewId Quality review identifier.
 * @returns {Promise<null>} Null when the review has been deleted.
 */
export async function deleteAnnotationReview(reviewId) {
    return request(`/api/annotation-reviews/${reviewId}`, {
        method: "DELETE",
    });
}
