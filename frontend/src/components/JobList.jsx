function JobList({
    jobs,
    datasets,
    onEdit,
    onDelete,
    loading,
}) {
    function getDatasetTitle(datasetId) {
        const dataset = datasets.find(
            (item) => item.id === datasetId
        );

        return dataset
            ? dataset.title
            : `Dataset #${datasetId}`;
    }


    if (loading) {
        return (
            <section>
                <h2>Labeling Jobs</h2>
                <p>Loading jobs...</p>
            </section>
        );
    }


    return (
        <section className="job-list-section">
            <div className="section-heading">
                <h2>Labeling Jobs</h2>

                <span>
                    {jobs.length} job
                    {jobs.length === 1 ? "" : "s"}
                </span>
            </div>


            {jobs.length === 0 ? (
                <p>
                    No labeling jobs found.
                </p>
            ) : (
                <div className="job-list">
                    {jobs.map((job) => (
                        <article
                            key={job.id}
                            className="job-card"
                        >
                            <div className="job-card-header">
                                <div>
                                    <h3>
                                        {job.title}
                                    </h3>

                                    <p>
                                        Job #{job.id}
                                    </p>
                                </div>

                                <span className="job-status">
                                    {job.status}
                                </span>
                            </div>


                            <p>
                                {job.description}
                            </p>


                            <p>
                                <strong>
                                    Dataset:
                                </strong>{" "}
                                {getDatasetTitle(
                                    job.dataset_id
                                )}
                            </p>


                            <p>
                                <strong>
                                    Created by:
                                </strong>{" "}
                                User #{job.created_by}
                            </p>


                            <p>
                                <strong>
                                    Created:
                                </strong>{" "}
                                {new Date(
                                    job.created_at
                                ).toLocaleString()}
                            </p>


                            <div className="job-actions">
                                <button
                                    type="button"
                                    onClick={() =>
                                        onEdit(job)
                                    }
                                >
                                    Edit
                                </button>

                                <button
                                    type="button"
                                    onClick={() =>
                                        onDelete(job)
                                    }
                                >
                                    Delete
                                </button>
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
}


export default JobList;