function ReviewList({
    reviews,
    jobs,
    onEdit,
    onDelete,
}) {
    function getJobTitle(jobId) {
        const job = jobs.find(
            (item) => item.id === jobId
        );

        return job
            ? job.title
            : `Job #${jobId}`;
    }

    if (reviews.length === 0) {
        return (
            <div className="content-card">
                <h2>Reviews</h2>

                <p>
                    No reviews found.
                </p>
            </div>
        );
    }

    return (
        <div className="content-card">
            <div className="section-heading">
                <div>
                    <h2>Reviews</h2>

                    <p>
                        Review feedback stored in
                        PostgreSQL.
                    </p>
                </div>

                <span className="count-badge">
                    {reviews.length}
                </span>
            </div>

            <div className="data-list">
                {reviews.map((review) => (
                    <article
                        key={review.id}
                        className="data-item"
                    >
                        <div>
                            <h3>
                                {getJobTitle(
                                    review.job_id
                                )}
                            </h3>

                            <p>
                                Rating:{" "}
                                <strong>
                                    {review.rating}/5
                                </strong>
                            </p>

                            {review.comment && (
                                <p>
                                    {review.comment}
                                </p>
                            )}

                            <small>
                                Reviewer ID:{" "}
                                {review.reviewer_id}
                            </small>
                        </div>

                        <div className="item-actions">
                            <button
                                type="button"
                                className="secondary-button"
                                onClick={() =>
                                    onEdit(review)
                                }
                            >
                                Edit
                            </button>

                            <button
                                type="button"
                                className="danger-button"
                                onClick={() =>
                                    onDelete(
                                        review.id
                                    )
                                }
                            >
                                Delete
                            </button>
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}


export default ReviewList;