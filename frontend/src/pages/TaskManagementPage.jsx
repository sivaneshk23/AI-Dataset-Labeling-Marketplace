/**
 * Annotation task management screen (dataset owner / administrator).
 *
 * The page owns all data loading and mutation so the presentation components
 * stay reusable: it loads the jobs, the annotator directory and the tasks, and
 * exposes create / assign / status / delete actions to `TaskForm` and
 * `TaskList`.
 */

import { useCallback, useEffect, useState } from "react";

import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
import {
    ErrorBanner,
    LoadingState,
    PageHeader,
    SuccessBanner,
} from "../components/ui";
import {
    assignTask,
    createTask,
    createTasksBulk,
    deleteTask,
    getTasks,
    updateTask,
} from "../services/annotationTaskService";
import { getAssignableAnnotators } from "../services/assignmentService";
import { getJobs } from "../services/jobService";
import { getDatasets } from "../services/datasetService";
import { importDatasetRecords } from "../services/annotationTaskService";
import { errorMessage } from "../utils/format";


function TaskManagementPage() {
    const [jobs, setJobs] = useState([]);
    const [datasets, setDatasets] = useState([]);
    const [annotators, setAnnotators] = useState([]);
    const [tasks, setTasks] = useState([]);

    const [jobFilter, setJobFilter] = useState("");

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");


    const loadData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const [jobData, datasetData, annotatorData, taskData] = await Promise.all([
                getJobs(),
                getDatasets(),
                getAssignableAnnotators(),
                getTasks(),
            ]);

            setJobs(jobData);
            setDatasets(datasetData);
            setAnnotators(annotatorData);
            setTasks(taskData);
        } catch (requestError) {
            setError(
                errorMessage(requestError, "Unable to load annotation tasks.")
            );
        } finally {
            setLoading(false);
        }
    }, []);


    useEffect(() => {
        let cancelled = false;

        async function load() {
            if (cancelled) {
                return;
            }

            await loadData();
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [loadData]);


    async function runAction(action, successMessage) {
        setError("");
        setNotice("");

        try {
            await action();
            await loadData();
            setNotice(successMessage);
        } catch (requestError) {
            setError(
                errorMessage(requestError, "The action could not be completed.")
            );
        }
    }


    const visibleTasks = jobFilter
        ? tasks.filter((task) => String(task.job_id) === jobFilter)
        : tasks;


    return (
        <section className="page">
            <PageHeader
                eyebrow="Task management"
                title="Annotation tasks"
                description="Split dataset records into units of work, assign them to annotators and follow their progress."
                actions={
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={loadData}
                    >
                        Refresh
                    </button>
                }
            />

            <ErrorBanner message={error} />

            <SuccessBanner message={notice} />

            {loading && tasks.length === 0 ? (
                <LoadingState message="Loading annotation tasks..." />
            ) : (
                <div className="workspace-layout">
                    <div className="workspace-side">
                        <TaskForm
                            jobs={jobs}
                            datasets={datasets}
                            annotators={annotators}
                            onImportDataset={(payload) =>
                                runAction(
                                    () => importDatasetRecords(payload),
                                    "Uploaded dataset records converted into annotation tasks."
                                )
                            }
                            onCreateSingle={(payload) =>
                                runAction(
                                    () => createTask(payload),
                                    "Annotation task created successfully."
                                )
                            }
                            onCreateBulk={(payload) =>
                                runAction(
                                    () => createTasksBulk(payload),
                                    "Annotation tasks imported successfully."
                                )
                            }
                        />
                    </div>

                    <div className="workspace-main">
                        <div className="toolbar">
                            <label className="inline-field">
                                Filter by job

                                <select
                                    value={jobFilter}
                                    onChange={(event) =>
                                        setJobFilter(event.target.value)
                                    }
                                >
                                    <option value="">All labeling jobs</option>

                                    {jobs.map((job) => (
                                        <option key={job.id} value={job.id}>
                                            {job.title}
                                        </option>
                                    ))}
                                </select>
                            </label>

                            <span className="toolbar-count">
                                {visibleTasks.length} task(s)
                            </span>
                        </div>

                        <TaskList
                            tasks={visibleTasks}
                            jobs={jobs}
                            annotators={annotators}
                            onAssign={(taskId, annotatorId) =>
                                runAction(
                                    () => assignTask(taskId, annotatorId),
                                    "Task assignment updated."
                                )
                            }
                            onStatusChange={(taskId, status) =>
                                runAction(
                                    () => updateTask(taskId, { status }),
                                    "Task status updated."
                                )
                            }
                            onDelete={(taskId) => {
                                const confirmed = window.confirm(
                                    "Delete this annotation task?"
                                );

                                if (!confirmed) {
                                    return;
                                }

                                runAction(
                                    () => deleteTask(taskId),
                                    "Annotation task deleted."
                                );
                            }}
                        />
                    </div>
                </div>
            )}
        </section>
    );
}


export default TaskManagementPage;
