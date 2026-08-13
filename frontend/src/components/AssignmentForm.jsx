import { useState } from "react";

function AssignmentForm({
    jobs,
    users,
    onSubmit,
    loading,
}) {
    const [jobId, setJobId] = useState("");
    const [workerId, setWorkerId] = useState("");

    const selectedJobId =
        jobId || (jobs.length > 0 ? String(jobs[0].id) : "");

    const selectedWorkerId =
        workerId || (users.length > 0 ? String(users[0].id) : "");

    async function handleSubmit(event) {
        event.preventDefault();

        if (!jobId || !workerId) {
            return;
        }

        await onSubmit({
            job_id: Number(selectedJobId),
            worker_id: Number(selectedWorkerId),
        });
    }

    return (
        <form
            className="card"
            onSubmit={handleSubmit}
        >
            <h2>Assign Job</h2>

            <div className="form-group">
                <label htmlFor="assignment-job">
                    Labeling Job
                </label>

                <select
                    id="assignment-job"
                    value={selectedJobId}
                    onChange={(event) =>
                        setJobId(event.target.value)
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
            </div>

            <div className="form-group">
                <label htmlFor="assignment-worker">
                    Annotator
                </label>

                <select
                    id="assignment-worker"
                    value={selectedWorkerId}
                    onChange={(event) =>
                        setWorkerId(event.target.value)
                    }
                    required
                >
                    <option value="">
                        Select an annotator
                    </option>

                    {users.map((user) => (
                        <option
                            key={user.id}
                            value={user.id}
                        >
                            {user.name} ({user.email})
                        </option>
                    ))}
                </select>
            </div>

            <button
                type="submit"
                className="primary-button"
                disabled={
                    loading ||
                    !jobId ||
                    !workerId
                }
            >
                {loading
                    ? "Assigning..."
                    : "Assign Job"}
            </button>
        </form>
    );
}

export default AssignmentForm;