import { useEffect, useState } from "react";

import { ErrorBanner, LoadingState, PageHeader } from "../components/ui";
import { getDatasets } from "../services/datasetService";
import { getJobs } from "../services/jobService";
import { downloadDatasetExport, downloadJobExport, previewDatasetExport } from "../services/exportService";

function ExportsPage() {
    const [datasets, setDatasets] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [preview, setPreview] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    async function load() {
        setLoading(true);
        try {
            const [datasetData, jobData] = await Promise.all([getDatasets(), getJobs()]);
            setDatasets(datasetData);
            setJobs(jobData);
        } catch (requestError) { setError(requestError.message || "Unable to load export options."); }
        finally { setLoading(false); }
    }

    useEffect(() => {
        let cancelled = false;
        async function initialLoad() {
            if (cancelled) return;
            await load();
        }
        initialLoad();
        return () => { cancelled = true; };
    }, []);

    async function showPreview(datasetId) {
        try { setPreview(await previewDatasetExport(datasetId)); setError(""); }
        catch (requestError) { setError(requestError.message); }
    }

    return (
        <section className="page">
            <PageHeader eyebrow="Delivery" title="Labeled-data exports" description="Export only approved annotations, with AI provenance preserved in the output." actions={<button className="secondary-button" onClick={load}>Refresh</button>} />
            <ErrorBanner message={error} />
            {loading ? <LoadingState message="Loading export catalog…" /> : (
                <>
                    <div className="content-grid">
                        <div className="content-card"><h2>By labeling job</h2><div className="stack-list">{jobs.map((job) => <div className="list-row" key={job.id}><div><strong>{job.title}</strong><span className="table-secondary">Job #{job.id}</span></div><button className="primary-button" onClick={() => downloadJobExport(job.id)}>Download CSV</button></div>)}</div></div>
                        <div className="content-card"><h2>By dataset</h2><div className="stack-list">{datasets.map((dataset) => <div className="list-row" key={dataset.id}><div><strong>{dataset.title}</strong><span className="table-secondary">{dataset.record_count || 0} source records</span></div><div className="form-actions"><button className="secondary-button" onClick={() => showPreview(dataset.id)}>Preview</button><button className="primary-button" onClick={() => downloadDatasetExport(dataset.id)}>Download CSV</button></div></div>)}</div></div>
                    </div>
                    {preview.length > 0 && <div className="content-card"><div className="section-heading"><div><p className="eyebrow">Preview</p><h2>Approved records</h2></div><span className="count-badge">{preview.length}</span></div><pre className="json-preview">{JSON.stringify(preview.slice(0, 20), null, 2)}</pre></div>}
                </>
            )}
        </section>
    );
}

export default ExportsPage;
