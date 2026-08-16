import { useState } from "react";


function ReviewForm({
    jobs,
    editingReview,
    onSubmit,
    onCancel,
}) {
    const [jobId, setJobId] = useState(
        editingReview
            ? String(editingReview.job_id)
            : ""
    );

    const [rating, setRating] = useState(
        editingReview
            ? String(editingReview.rating)
            : "5"
    );

    const [comment, setComment] = useState(
        editingReview?.comment || ""
    );


    function handleSubmit(event) {
        event.preventDefault();

        if (!editingReview && !jobId) {
            return;
        }

        onSubmit({
            ...(editingReview
                ? {}
                : {
                    job_id: Number(jobId),
                }),
            rating: Number(rating),
            comment:
                comment.trim() || null,
        });
    }


    return (
        <div className="content-card">
            <div className="section-heading">
                <div>
                    <h2>
                        {editingReview
                            ? "Edit Review"
                            : "Submit Review"}
                    </h2>

                    <p>
                        Rate a completed labeling job
                        and provide feedback.
                    </p>
                </div>
            </div>

            <form
                className="form-grid"
                onSubmit={handleSubmit}
            >
                {!editingReview && (
                    <label>
                        Labeling Job

                        <select
                            value={jobId}
                            onChange={(event) =>
                                setJobId(
                                    event.target.value
                                )
                            }
                            required
                        >
                            <option value="">
                                Select a job
                            </option>

                            {jobs.map((job) => (
                                <option
                                    key={job.id}
                                    value={job.id}
                                >
                                    {job.title}
                                </option>
                            ))}
                        </select>
                    </label>
                )}

                <label>
                    Rating

                    <select
                        value={rating}
                        onChange={(event) =>
                            setRating(
                                event.target.value
                            )
                        }
                        required
                    >
                        <option value="5">
                            5 - Excellent
                        </option>

                        <option value="4">
                            4 - Good
                        </option>

                        <option value="3">
                            3 - Average
                        </option>

                        <option value="2">
                            2 - Poor
                        </option>

                        <option value="1">
                            1 - Very Poor
                        </option>
                    </select>
                </label>

                <label>
                    Comment

                    <textarea
                        value={comment}
                        onChange={(event) =>
                            setComment(
                                event.target.value
                            )
                        }
                        placeholder="Enter your feedback..."
                        rows="4"
                        maxLength="2000"
                    />
                </label>

                <div className="form-actions">
                    <button
                        type="submit"
                        className="primary-button"
                        disabled={
                            !editingReview &&
                            jobs.length === 0
                        }
                    >
                        {editingReview
                            ? "Update Review"
                            : "Submit Review"}
                    </button>

                    {editingReview && (
                        <button
                            type="button"
                            className="secondary-button"
                            onClick={onCancel}
                        >
                            Cancel
                        </button>
                    )}
                </div>
            </form>
        </div>
    );
}


export default ReviewForm;