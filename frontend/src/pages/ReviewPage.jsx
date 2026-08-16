import { useEffect, useState } from "react";

import ReviewForm from "../components/ReviewForm";
import ReviewList from "../components/ReviewList";

import { getJobs } from "../services/jobService";

import {
    createReview,
    deleteReview,
    getReviews,
    updateReview,
} from "../services/reviewService";


function ReviewPage() {
    const [jobs, setJobs] = useState([]);
    const [reviews, setReviews] = useState([]);

    const [editingReview, setEditingReview] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    useEffect(() => {
        let cancelled = false;

        async function initializePage() {
            setLoading(true);
            setError("");

            try {
                const [
                    jobData,
                    reviewData,
                ] = await Promise.all([
                    getJobs(),
                    getReviews(),
                ]);

                if (cancelled) {
                    return;
                }

                setJobs(jobData);
                setReviews(reviewData);
            } catch (requestError) {
                if (cancelled) {
                    return;
                }

                setError(
                    requestError.message ||
                    "Unable to load review data."
                );
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        initializePage();

        return () => {
            cancelled = true;
        };
    }, []);


    async function handleLoadData() {
        setLoading(true);
        setError("");

        try {
            const [
                jobData,
                reviewData,
            ] = await Promise.all([
                getJobs(),
                getReviews(),
            ]);

            setJobs(jobData);
            setReviews(reviewData);
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to load review data."
            );
        } finally {
            setLoading(false);
        }
    }


    async function handleSubmit(reviewData) {
        setError("");

        try {
            if (editingReview) {
                await updateReview(
                    editingReview.id,
                    reviewData
                );

                setEditingReview(null);
            } else {
                await createReview(reviewData);
            }

            await handleLoadData();
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to save review."
            );
        }
    }


    function handleEdit(review) {
        setEditingReview(review);
    }


    function handleCancelEdit() {
        setEditingReview(null);
    }


    async function handleDelete(reviewId) {
        const confirmed = window.confirm(
            "Are you sure you want to delete this review?"
        );

        if (!confirmed) {
            return;
        }

        setError("");

        try {
            await deleteReview(reviewId);

            if (
                editingReview &&
                editingReview.id === reviewId
            ) {
                setEditingReview(null);
            }

            await handleLoadData();
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to delete review."
            );
        }
    }


    if (loading) {
        return (
            <section className="page-section">
                <div className="page-header">
                    <h1>Reviews</h1>

                    <p>
                        Loading reviews...
                    </p>
                </div>
            </section>
        );
    }


    return (
        <section className="page-section">
            <div className="page-header">
                <div>
                    <h1>Reviews</h1>

                    <p>
                        Review labeling jobs and
                        provide quality feedback.
                    </p>
                </div>

                <button
                    type="button"
                    className="secondary-button"
                    onClick={handleLoadData}
                >
                    Refresh
                </button>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {jobs.length === 0 ? (
                <div className="content-card">
                    <h2>
                        No labeling jobs available
                    </h2>

                    <p>
                        Create a labeling job before
                        submitting a review.
                    </p>
                </div>
            ) : (
                <ReviewForm
                    key={
                        editingReview?.id ??
                        "new"
                    }
                    jobs={jobs}
                    editingReview={
                        editingReview
                    }
                    onSubmit={handleSubmit}
                    onCancel={
                        handleCancelEdit
                    }
                />
            )}

            <ReviewList
                reviews={reviews}
                jobs={jobs}
                onEdit={handleEdit}
                onDelete={handleDelete}
            />
        </section>
    );
}


export default ReviewPage;