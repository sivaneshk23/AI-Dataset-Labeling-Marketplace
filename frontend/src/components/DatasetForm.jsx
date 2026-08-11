import { useState } from "react";

const emptyForm = {
    title: "",
    description: "",
    dataset_type: "",
};

function DatasetForm({
    editingDataset,
    onSubmit,
    onCancel,
}) {
    const [form, setForm] = useState(() => {
        if (editingDataset) {
            return {
                title: editingDataset.title,
                description: editingDataset.description,
                dataset_type: editingDataset.dataset_type,
            };
        }

        return emptyForm;
    });

    const [submitting, setSubmitting] = useState(false);

    function handleChange(event) {
        const { name, value } = event.target;

        setForm((current) => ({
            ...current,
            [name]: value,
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setSubmitting(true);

        try {
            await onSubmit(form);

            if (!editingDataset) {
                setForm(emptyForm);
            }
        } finally {
            setSubmitting(false);
        }
    }

    function handleCancel() {
        setForm(emptyForm);
        onCancel();
    }

    return (
        <form
            className="dataset-form"
            onSubmit={handleSubmit}
        >
            <div className="form-header">
                <div>
                    <p className="eyebrow">
                        Dataset Management
                    </p>

                    <h2>
                        {editingDataset
                            ? "Update Dataset"
                            : "Create Dataset"}
                    </h2>
                </div>
            </div>

            <label>
                Dataset Title

                <input
                    type="text"
                    name="title"
                    value={form.title}
                    onChange={handleChange}
                    minLength={3}
                    maxLength={150}
                    placeholder="e.g. Vehicle Images"
                    required
                />
            </label>

            <label>
                Description

                <textarea
                    name="description"
                    value={form.description}
                    onChange={handleChange}
                    minLength={10}
                    placeholder="Describe the dataset and its intended use."
                    rows={5}
                    required
                />
            </label>

            <label>
                Dataset Type

                <select
                    name="dataset_type"
                    value={form.dataset_type}
                    onChange={handleChange}
                    required
                >
                    <option value="">
                        Select dataset type
                    </option>

                    <option value="Computer Vision">
                        Computer Vision
                    </option>

                    <option value="Natural Language Processing">
                        Natural Language Processing
                    </option>

                    <option value="Audio">
                        Audio
                    </option>

                    <option value="Tabular">
                        Tabular
                    </option>

                    <option value="Other">
                        Other
                    </option>
                </select>
            </label>

            <div className="form-actions">
                <button
                    type="submit"
                    className="primary-button"
                    disabled={submitting}
                >
                    {submitting
                        ? "Saving..."
                        : editingDataset
                            ? "Update Dataset"
                            : "Create Dataset"}
                </button>

                {editingDataset && (
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

export default DatasetForm;