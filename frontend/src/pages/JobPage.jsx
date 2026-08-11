import { useEffect, useState } from "react";

import JobForm from "../components/JobForm";
import JobList from "../components/JobList";
import { getDatasets } from "../services/datasetService";
import {
    createJob,
    deleteJob,
    getJobs,
    updateJob,
} from "../services/jobService";


function JobPage() {
    const [datasets, setDatasets] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [editingJob, setEditingJob] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    async function loadJobs() {
        const data = await getJobs();
        setJobs(data);
    }


    async function loadDatasets() {
        const data = await getDatasets();
        setDatasets(data);
    }


    async function handleLoadData() {
        setLoading(true);
        setError("");

        try {
            await Promise.all([
                loadDatasets(),
                loadJobs(),
            ]);
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to load job data."
            );
        } finally {
            setLoading(false);
        }
    }


    useEffect(() => {
        let cancelled = false;

        async function initializePage() {
            setLoading(true);
            setError("");

            try {
                const [
                    datasetData,
                    jobData,
                ] = await Promise.all([
                    getDatasets(),
                    getJobs(),
                ]);

                if (cancelled) {
                    return;
                }

                setDatasets(datasetData);
                setJobs(jobData);
            } catch (requestError) {
                if (cancelled) {
                    return;
                }

                setError(
                    requestError.message ||
                    "Unable to load job data."
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


    async function handleSubmit(jobData) {
        setError("");

        try {
            if (editingJob) {
                await updateJob(
                    editingJob.id,
                    jobData
                );

                setEditingJob(null);
            } else {
                await createJob(jobData);
            }

            await handleLoadData();
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to save labeling job."
            );
        }
    }


    async function handleEdit(job) {
        setEditingJob(job);
    }


    async function handleDelete(jobId) {
        const confirmed = window.confirm(
            "Are you sure you want to delete this labeling job?"
        );

        if (!confirmed) {
            return;
        }

        setError("");

        try {
            await deleteJob(jobId);

            if (
                editingJob &&
                editingJob.id === jobId
            ) {
                setEditingJob(null);
            }

            await handleLoadData();
        } catch (requestError) {
            setError(
                requestError.message ||
                "Unable to delete labeling job."
            );
        }
    }


    function handleCancelEdit() {
        setEditingJob(null);
    }


    if (loading) {
        return (
            <section className="page-section">
                <div className="page-header">
                    <h1>Labeling Jobs</h1>
                    <p>
                        Loading labeling jobs...
                    </p>
                </div>
            </section>
        );
    }


    return (
        <section className="page-section">
            <div className="page-header">
                <div>
                    <h1>Labeling Jobs</h1>

                    <p>
                        Create and manage dataset
                        labeling jobs.
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


            <JobForm
                key={editingJob?.id ?? "new"}
                datasets={datasets}
                editingJob={editingJob}
                onSubmit={handleSubmit}
                onCancel={handleCancelEdit}
            />


            <JobList
                jobs={jobs}
                datasets={datasets}
                onEdit={handleEdit}
                onDelete={handleDelete}
            />
        </section>
    );
}


export default JobPage;