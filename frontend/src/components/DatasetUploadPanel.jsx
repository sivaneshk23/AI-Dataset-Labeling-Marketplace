import { useState } from "react";

import { uploadDataset } from "../services/datasetService";


function DatasetUploadPanel({ dataset, onUploaded }) {
    const [file, setFile] = useState(null);
    const [textColumn, setTextColumn] = useState("");
    const [replaceExisting, setReplaceExisting] = useState(false);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");
        setNotice("");

        if (!file) {
            setError("Choose a CSV, JSON, JSONL or XLSX file first.");
            return;
        }

        setBusy(true);
        try {
            const result = await uploadDataset(dataset.id, file, {
                textColumn: textColumn.trim() || undefined,
                replaceExisting,
            });
            setNotice(`${result.records_imported.toLocaleString()} records imported successfully.`);
            setFile(null);
            setTextColumn("");
            setReplaceExisting(false);
            event.target.reset();
            await onUploaded();
        } catch (requestError) {
            setError(requestError.message || "Dataset upload failed.");
        } finally {
            setBusy(false);
        }
    }

    return (
        <form className="content-card upload-panel" onSubmit={handleSubmit}>
            <div className="section-heading">
                <div>
                    <p className="eyebrow">Source data</p>
                    <h2>Upload dataset</h2>
                    <p>Import bounded, validated records into PostgreSQL before creating annotation tasks.</p>
                </div>
                <span className="status-badge status-dataset_owner">{dataset.record_count || 0} records</span>
            </div>

            <label className="file-drop">
                <span className="file-drop-title">Choose dataset file</span>
                <span className="file-drop-hint">CSV · JSON · JSONL · XLSX · maximum 25 MB / 10,000 records</span>
                <input
                    type="file"
                    accept=".csv,.json,.jsonl,.xlsx"
                    onChange={(event) => setFile(event.target.files?.[0] || null)}
                />
                {file && <strong>{file.name}</strong>}
            </label>

            <label>
                Text column <span className="field-hint">Optional — auto-detected when blank</span>
                <input
                    value={textColumn}
                    onChange={(event) => setTextColumn(event.target.value)}
                    placeholder="e.g. review or text"
                />
            </label>

            <label className="checkbox-row">
                <input
                    type="checkbox"
                    checked={replaceExisting}
                    onChange={(event) => setReplaceExisting(event.target.checked)}
                />
                Replace previously imported records
            </label>

            {error && <div className="error-banner">{error}</div>}
            {notice && <div className="success-banner">{notice}</div>}

            <div className="form-actions">
                <button className="primary-button" type="submit" disabled={busy || !file}>
                    {busy ? "Importing…" : "Import dataset"}
                </button>
            </div>
        </form>
    );
}

export default DatasetUploadPanel;
