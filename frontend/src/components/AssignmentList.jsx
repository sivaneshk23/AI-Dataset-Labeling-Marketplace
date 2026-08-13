function AssignmentList({
    assignments,
    jobs,
    users,
    onUpdate,
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

    function getWorkerName(workerId) {
        const user = users.find(
            (item) => item.id === workerId
        );

        return user
            ? `${user.name} (${user.email})`
            : `User #${workerId}`;
    }

    if (assignments.length === 0) {
        return (
            <section className="card">
                <h2>Assignments</h2>

                <p>
                    No job assignments found.
                </p>
            </section>
        );
    }

    return (
        <section className="card">
            <h2>Assignments</h2>

            <div className="assignment-list">
                {assignments.map(
                    (assignment) => (
                        <article
                            className="list-item"
                            key={assignment.id}
                        >
                            <div>
                                <h3>
                                    {
                                        getJobTitle(
                                            assignment.job_id
                                        )
                                    }
                                </h3>

                                <p>
                                    Annotator:{" "}
                                    {
                                        getWorkerName(
                                            assignment.worker_id
                                        )
                                    }
                                </p>

                                <p>
                                    Status:{" "}
                                    <strong>
                                        {
                                            assignment.status
                                        }
                                    </strong>
                                </p>
                            </div>

                            <div className="button-group">
                                <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={() =>
                                        onUpdate(
                                            assignment
                                        )
                                    }
                                >
                                    Update
                                </button>

                                <button
                                    type="button"
                                    className="danger-button"
                                    onClick={() =>
                                        onDelete(
                                            assignment.id
                                        )
                                    }
                                >
                                    Delete
                                </button>
                            </div>
                        </article>
                    )
                )}
            </div>
        </section>
    );
}

export default AssignmentList;