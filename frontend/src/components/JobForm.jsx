import { useState } from "react";


const EMPTY_FORM = {
    dataset_id: "",
    title: "",
    description: "",
    status: "open",
    annotation_type: "single_label_text",
    label_options: "Positive, Negative, Neutral",
};


function createFormFromJob(job) {
    if (!job) {
        return EMPTY_FORM;
    }

    return {
        dataset_id: String(job.dataset_id),
        title: job.title,
        description: job.description,
        status: job.status,
        annotation_type: job.annotation_type || "single_label_text",
        label_options: (job.label_options || []).join(", "),
    };
}


function JobForm({
    datasets = [],
    editingJob = null,
    onSubmit,
    onCancel,
}) {
    const [form, setForm] = useState(
        createFormFromJob(editingJob)
    );


    function handleChange(event) {
        const { name, value } = event.target;

        setForm((currentForm) => ({
            ...currentForm,
            [name]: value,
        }));
    }


    async function handleSubmit(event) {
        event.preventDefault();

        await onSubmit({
            dataset_id: Number(form.dataset_id),
            title: form.title.trim(),
            description: form.description.trim(),
            status: form.status,
            annotation_type: form.annotation_type,
            label_options: form.label_options.split(",").map((value) => value.trim()).filter(Boolean),
        });

        if (!editingJob) {
            setForm(EMPTY_FORM);
        }
    }


    function handleCancel() {
        setForm(EMPTY_FORM);

        if (onCancel) {
            onCancel();
        }
    }


    return (
        <form
            className="form-card"
            onSubmit={handleSubmit}
        >
            <div className="form-header">
                <h2>
                    {editingJob
                        ? "Edit Labeling Job"
                        : "Create Labeling Job"}
                </h2>

                <p>
                    Create a labeling task for an
                    existing dataset.
                </p>
            </div>


            <div className="form-group">
                <label htmlFor="dataset_id">
                    Dataset
                </label>

                <select
                    id="dataset_id"
                    name="dataset_id"
                    value={form.dataset_id}
                    onChange={handleChange}
                    required
                >
                    <option value="">
                        Select a dataset
                    </option>

                    {datasets.map((dataset) => (
                        <option
                            key={dataset.id}
                            value={dataset.id}
                        >
                            {dataset.title}
                        </option>
                    ))}
                </select>
            </div>


            <div className="form-group">
                <label htmlFor="title">
                    Job Title
                </label>

                <input
                    id="title"
                    name="title"
                    type="text"
                    value={form.title}
                    onChange={handleChange}
                    minLength={3}
                    maxLength={150}
                    placeholder="Vehicle Object Detection Labeling"
                    required
                />
            </div>


            <div className="form-group">
                <label htmlFor="description">
                    Description
                </label>

                <textarea
                    id="description"
                    name="description"
                    value={form.description}
                    onChange={handleChange}
                    minLength={10}
                    rows={5}
                    placeholder="Describe what annotators need to label."
                    required
                />
            </div>


            <div className="form-group">
                <label htmlFor="annotation_type">
                    Annotation requirement
                </label>
                <select id="annotation_type" name="annotation_type" value={form.annotation_type} onChange={handleChange}>
                    <option value="single_label_text">Single label · text</option>
                </select>
            </div>

            <div className="form-group">
                <label htmlFor="label_options">
                    Allowed labels
                </label>
                <input id="label_options" name="label_options" type="text" value={form.label_options} onChange={handleChange} placeholder="Positive, Negative, Neutral" />
                <span className="field-hint">Comma-separated vocabulary used by the human annotator and AI assistant.</span>
            </div>

            <div className="form-group">
                <label htmlFor="status">
                    Status
                </label>

                <select
                    id="status"
                    name="status"
                    value={form.status}
                    onChange={handleChange}
                >
                    <option value="open">
                        Open
                    </option>

                    <option value="in_progress">
                        In Progress
                    </option>

                    <option value="completed">
                        Completed
                    </option>

                    <option value="cancelled">
                        Cancelled
                    </option>
                </select>
            </div>


            <div className="form-actions">
                <button
                    type="submit"
                    className="primary-button"
                >
                    {editingJob
                        ? "Update Job"
                        : "Create Job"}
                </button>


                {editingJob && (
                    <button
                        type="button"
                        className="secondary-button"
                        onClick={handleCancel}
                    >
                        Cancel
                    </button>
                )}
            </div>
        </form>
    );
}


export default JobForm;