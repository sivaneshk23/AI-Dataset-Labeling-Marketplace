import { useCallback, useEffect, useState } from "react";

import DatasetForm from "../components/DatasetForm";
import DatasetList from "../components/DatasetList";
import DatasetUploadPanel from "../components/DatasetUploadPanel";
import { getDatasets, createDataset, updateDataset, deleteDataset } from "../services/datasetService";
import { ErrorBanner, LoadingState, PageHeader, SuccessBanner } from "../components/ui";


function DatasetPage() {
    const [datasets, setDatasets] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [editingDataset, setEditingDataset] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    const loadDatasets = useCallback(async () => {
        setLoading(true);
        setError("");
        try {
            const response = await getDatasets();
            setDatasets(response || []);
        } catch (requestError) {
            setError(requestError.message || "Unable to load datasets.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        let cancelled = false;
        async function initialLoad() {
            if (cancelled) return;
            await loadDatasets();
        }
        initialLoad();
        return () => { cancelled = true; };
    }, [loadDatasets]);

    async function handleSubmit(datasetData) {
        setError("");
        setNotice("");
        try {
            if (editingDataset) {
                await updateDataset(editingDataset.id, datasetData);
                setNotice("Dataset updated successfully.");
                setEditingDataset(null);
            } else {
                const created = await createDataset(datasetData);
                setSelectedId(created.id);
                setNotice("Dataset created. Upload the source file next.");
            }
            await loadDatasets();
        } catch (requestError) {
            setError(requestError.message || "Unable to save the dataset.");
            throw requestError;
        }
    }

    async function handleDelete(datasetId) {
        if (!window.confirm("Delete this dataset and its dependent labeling work?")) return;
        setError("");
        try {
            await deleteDataset(datasetId);
            if (selectedId === datasetId) setSelectedId(null);
            if (editingDataset?.id === datasetId) setEditingDataset(null);
            setNotice("Dataset deleted successfully.");
            await loadDatasets();
        } catch (requestError) {
            setError(requestError.message || "Unable to delete the dataset.");
        }
    }

    const selectedDataset = datasets.find((dataset) => dataset.id === selectedId) || datasets[0] || null;

    return (
        <section className="page">
            <PageHeader
                eyebrow="Core data module"
                title="Datasets"
                description="Create a dataset, upload validated source records, then turn those records into annotation tasks."
                actions={<button className="secondary-button" type="button" onClick={loadDatasets}>Refresh</button>}
            />
            <ErrorBanner message={error} />
            <SuccessBanner message={notice} />

            <div className="dataset-layout">
                <DatasetForm
                    editingDataset={editingDataset}
                    onSubmit={handleSubmit}
                    onCancel={() => setEditingDataset(null)}
                />
                <div className="dataset-results">
                    {loading && datasets.length === 0 ? (
                        <LoadingState message="Loading datasets…" />
                    ) : (
                        <>
                            <div className="section-heading">
                                <div>
                                    <p className="eyebrow">PostgreSQL source registry</p>
                                    <h2>Available datasets</h2>
                                </div>
                                <span className="count-badge">{datasets.length}</span>
                            </div>
                            <DatasetList
                                datasets={datasets}
                                loading={loading}
                                onEdit={setEditingDataset}
                                onDelete={handleDelete}
                                onSelect={setSelectedId}
                            />
                        </>
                    )}
                </div>
            </div>

            {selectedDataset ? (
                <DatasetUploadPanel dataset={selectedDataset} onUploaded={loadDatasets} />
            ) : (
                <div className="content-card">
                    <p className="muted">Create or select a dataset to upload source records.</p>
                </div>
            )}
        </section>
    );
}

export default DatasetPage;
