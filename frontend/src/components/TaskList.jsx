/**
 * Annotation task list with assignment and status controls.
 *
 * The list is intentionally presentational: every action is delegated to the
 * container page, which owns the API calls and the refresh logic.
 */

import { EmptyState, StatusBadge } from "./ui";
import { formatDateTime, indexById, jobTitle } from "../utils/format";


const STATUS_OPTIONS = [
    "pending",
    "in_progress",
    "submitted",
    "approved",
    "rejected",
];


function TaskList({
    tasks,
    jobs,
    annotators,
    onAssign,
    onStatusChange,
    onDelete,
}) {
    const jobsById = indexById(jobs);
    const annotatorsById = indexById(annotators);

    function annotatorName(userId) {
        if (!userId) {
            return "Unassigned";
        }

        const annotator = annotatorsById.get(userId);

        return annotator ? annotator.name : `User #${userId}`;
    }


    if (tasks.length === 0) {
        return (
            <div className="content-card">
                <h2>Annotation tasks</h2>

                <EmptyState
                    title="No annotation tasks yet"
                    description="Create a task above, or import a batch of records."
                />
            </div>
        );
    }


    return (
        <div className="content-card">
            <div className="section-heading">
                <div>
                    <h2>Annotation tasks</h2>

                    <p>Assign work, follow progress and correct mistakes.</p>
                </div>

                <span className="count-badge">{tasks.length}</span>
            </div>

            <div className="data-list">
                {tasks.map((task) => (
                    <article className="data-item" key={task.id}>
                        <div className="data-item-main">
                            <div className="data-item-heading">
                                <strong>Task #{task.id}</strong>

                                <StatusBadge status={task.status} />
                            </div>

                            <p className="data-item-text">{task.input_text}</p>

                            <div className="data-item-meta">
                                <span>{jobTitle(jobsById, task.job_id)}</span>

                                <span>{annotatorName(task.assigned_to)}</span>

                                <span>{formatDateTime(task.created_at)}</span>
                            </div>
                        </div>

                        <div className="data-item-actions">
                            <label className="inline-field">
                                Annotator

                                <select
                                    value={task.assigned_to ?? ""}
                                    onChange={(event) =>
                                        onAssign(
                                            task.id,
                                            event.target.value
                                        )
                                    }
                                >
                                    <option value="">Unassigned</option>

                                    {annotators.map((annotator) => (
                                        <option
                                            key={annotator.id}
                                            value={annotator.id}
                                        >
                                            {annotator.name}
                                        </option>
                                    ))}
                                </select>
                            </label>

                            <label className="inline-field">
                                Status

                                <select
                                    value={task.status}
                                    onChange={(event) =>
                                        onStatusChange(
                                            task.id,
                                            event.target.value
                                        )
                                    }
                                >
                                    {STATUS_OPTIONS.map((status) => (
                                        <option key={status} value={status}>
                                            {status.replace("_", " ")}
                                        </option>
                                    ))}
                                </select>
                            </label>

                            <button
                                type="button"
                                className="danger-button"
                                onClick={() => onDelete(task.id)}
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


export default TaskList;
