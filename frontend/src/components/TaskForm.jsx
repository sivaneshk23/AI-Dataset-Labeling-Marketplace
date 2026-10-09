/**
 * Create annotation tasks from manual records or uploaded dataset records.
 */
import { useState } from "react";

const EMPTY_SINGLE = { job_id: "", input_text: "", assigned_to: "" };
const EMPTY_BULK = { job_id: "", assigned_to: "", items: "" };
const EMPTY_IMPORT = { dataset_id: "", job_id: "", assigned_to: "", limit: 1000 };

function TaskForm({ jobs = [], datasets = [], annotators = [], onCreateSingle, onCreateBulk, onImportDataset }) {
    const [mode, setMode] = useState("uploaded");
    const [single, setSingle] = useState(EMPTY_SINGLE);
    const [bulk, setBulk] = useState(EMPTY_BULK);
    const [datasetImport, setDatasetImport] = useState(EMPTY_IMPORT);
    const [submitting, setSubmitting] = useState(false);

    const activeJobId = single.job_id || bulk.job_id || datasetImport.job_id || (jobs[0] ? String(jobs[0].id) : "");
    const activeItems = bulk.items.split("\n").map((line) => line.trim()).filter(Boolean);

    function setBoth(name, value) {
        setSingle((current) => ({ ...current, [name]: value }));
        setBulk((current) => ({ ...current, [name]: value }));
        setDatasetImport((current) => ({ ...current, [name]: value }));
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (!activeJobId) return;
        setSubmitting(true);
        try {
            if (mode === "single") {
                await onCreateSingle({ job_id: Number(activeJobId), input_text: single.input_text.trim(), assigned_to: single.assigned_to ? Number(single.assigned_to) : null });
                setSingle(EMPTY_SINGLE);
            } else if (mode === "bulk") {
                await onCreateBulk({ job_id: Number(activeJobId), items: activeItems, assigned_to: bulk.assigned_to ? Number(bulk.assigned_to) : null });
                setBulk(EMPTY_BULK);
            } else {
                if (!datasetImport.dataset_id) return;
                await onImportDataset({
                    dataset_id: Number(datasetImport.dataset_id),
                    job_id: Number(activeJobId),
                    assigned_to: datasetImport.assigned_to ? Number(datasetImport.assigned_to) : null,
                    limit: Number(datasetImport.limit),
                    offset: 0,
                    skip_duplicates: true,
                });
            }
        } finally {
            setSubmitting(false);
        }
    }

    const annotatorOptions = (
        <>
            <option value="">Leave unassigned</option>
            {annotators.map((annotator) => <option key={annotator.id} value={annotator.id}>{annotator.name}</option>)}
        </>
    );

    return (
        <form className="content-card form-card" onSubmit={handleSubmit}>
            <div className="section-heading">
                <div>
                    <p className="eyebrow">Task authoring</p>
                    <h2>Create annotation tasks</h2>
                    <p>Import uploaded source records or add controlled manual batches.</p>
                </div>
                <div className="tab-switch">
                    {[['uploaded', 'From dataset'], ['single', 'Single'], ['bulk', 'Bulk']].map(([value, label]) => (
                        <button key={value} type="button" aria-pressed={mode === value} className={mode === value ? "tab-button active" : "tab-button"} onClick={() => setMode(value)}>{label}</button>
                    ))}
                </div>
            </div>

            <label>
                Labeling job
                <select name="job_id" value={activeJobId} onChange={(event) => setBoth("job_id", event.target.value)} required>
                    <option value="">Select a job</option>
                    {jobs.map((job) => <option key={job.id} value={job.id}>{job.title}</option>)}
                </select>
            </label>

            {mode === "uploaded" && (
                <>
                    <label>
                        Uploaded dataset
                        <select value={datasetImport.dataset_id} onChange={(event) => setDatasetImport((current) => ({ ...current, dataset_id: event.target.value }))} required>
                            <option value="">Select a dataset</option>
                            {datasets.filter((dataset) => dataset.record_count > 0).map((dataset) => <option key={dataset.id} value={dataset.id}>{dataset.title} · {dataset.record_count.toLocaleString()} records</option>)}
                        </select>
                    </label>
                    <label>
                        Records to import
                        <input type="number" min="1" max="1000" value={datasetImport.limit} onChange={(event) => setDatasetImport((current) => ({ ...current, limit: event.target.value }))} />
                        <span className="field-hint">Import in batches of up to 1,000 records.</span>
                    </label>
                </>
            )}

            {mode === "single" && (
                <label>
                    Record to annotate
                    <textarea name="input_text" value={single.input_text} onChange={(event) => setSingle((current) => ({ ...current, input_text: event.target.value }))} rows={4} maxLength={5000} placeholder="Delivery driver left the parcel at the front door." required />
                </label>
            )}

            {mode === "bulk" && (
                <label>
                    Records (one per line)
                    <span className="field-hint">{activeItems.length} record(s) ready to import</span>
                    <textarea name="items" value={bulk.items} onChange={(event) => setBulk((current) => ({ ...current, items: event.target.value }))} rows={8} placeholder={'First record\nSecond record\nThird record'} required />
                </label>
            )}

            <label>
                Assign to annotator
                <select value={mode === "single" ? single.assigned_to : mode === "bulk" ? bulk.assigned_to : datasetImport.assigned_to} onChange={(event) => {
                    const value = event.target.value;
                    setSingle((current) => ({ ...current, assigned_to: value }));
                    setBulk((current) => ({ ...current, assigned_to: value }));
                    setDatasetImport((current) => ({ ...current, assigned_to: value }));
                }}>{annotatorOptions}</select>
            </label>

            <div className="form-actions">
                <button type="submit" className="primary-button" disabled={submitting || jobs.length === 0}>
                    {submitting ? "Creating…" : mode === "uploaded" ? "Create tasks from dataset" : "Create task(s)"}
                </button>
            </div>
        </form>
    );
}

export default TaskForm;
