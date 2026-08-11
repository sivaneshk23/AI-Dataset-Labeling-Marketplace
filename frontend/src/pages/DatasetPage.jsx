import { useEffect, useState } from "react";

import DatasetForm from "../components/DatasetForm";
import DatasetList from "../components/DatasetList";

import {
    createDataset,
    deleteDataset,
    getDatasets,
    updateDataset,
} from "../services/datasetService";

function DatasetPage() {
    const [datasets, setDatasets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingDataset, setEditingDataset] =
        useState(null);
    const [error, setError] = useState("");

    async function loadDatasets() {
        try {
            const response = await getDatasets();

            setDatasets(response.data || []);
            setError("");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        let cancelled = false;

        async function fetchDatasets() {
            try {
                const response = await getDatasets();

                if (!cancelled) {
                    setDatasets(response.data || []);
                    setError("");
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err.message);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchDatasets();

        return () => {
            cancelled = true;
        };
    }, []);

    async function handleSubmit(datasetData) {
        setError("");

        try {
            if (editingDataset) {
                await updateDataset(
                    editingDataset.id,
                    datasetData
                );

                setEditingDataset(null);
            } else {
                await createDataset(datasetData);
            }

            await loadDatasets();
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }

    async function handleDelete(datasetId) {
        const confirmed = window.confirm(
            "Are you sure you want to delete this dataset?"
        );

        if (!confirmed) {
            return;
        }

        setError("");

        try {
            await deleteDataset(datasetId);

            if (editingDataset?.id === datasetId) {
                setEditingDataset(null);
            }

            await loadDatasets();
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <section className="page">
            <div className="page-heading">
                <div>
                    <p className="eyebrow">
                        Core Module
                    </p>

                    <h1>Datasets</h1>

                    <p>
                        Manage datasets available for
                        annotation and labeling workflows.
                    </p>
                </div>

                <button
                    className="secondary-button"
                    onClick={() => {
                        setLoading(true);
                        loadDatasets();
                    }}
                >
                    Refresh
                </button>
            </div>

            {error && (
                <div className="error-banner">
                    {error}
                </div>
            )}

            <div className="dataset-layout">
                <DatasetForm
                    editingDataset={editingDataset}
                    onSubmit={handleSubmit}
                    onCancel={() =>
                        setEditingDataset(null)
                    }
                />

                <div className="dataset-results">
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">
                                PostgreSQL Data
                            </p>

                            <h2>
                                Available Datasets
                            </h2>
                        </div>

                        <span className="count-badge">
                            {datasets.length}
                        </span>
                    </div>

                    <DatasetList
                        datasets={datasets}
                        loading={loading}
                        onEdit={setEditingDataset}
                        onDelete={handleDelete}
                    />
                </div>
            </div>
        </section>
    );
}

export default DatasetPage;