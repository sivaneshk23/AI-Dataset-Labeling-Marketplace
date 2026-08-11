function DatasetList({
    datasets,
    loading,
    onEdit,
    onDelete,
}) {
    if (loading) {
        return (
            <div className="empty-state">
                Loading datasets...
            </div>
        );
    }

    if (datasets.length === 0) {
        return (
            <div className="empty-state">
                <h3>No datasets yet</h3>
                <p>
                    Create your first dataset using the
                    form.
                </p>
            </div>
        );
    }

    return (
        <div className="dataset-list">
            {datasets.map((dataset) => (
                <article
                    className="dataset-card"
                    key={dataset.id}
                >
                    <div className="dataset-card-header">
                        <div>
                            <span className="dataset-id">
                                #{dataset.id}
                            </span>

                            <h3>{dataset.title}</h3>
                        </div>

                        <span className="dataset-type">
                            {dataset.dataset_type}
                        </span>
                    </div>

                    <p className="dataset-description">
                        {dataset.description}
                    </p>

                    <div className="dataset-card-footer">
                        <small>
                            Created:{" "}
                            {new Date(
                                dataset.created_at
                            ).toLocaleString()}
                        </small>

                        <div className="card-actions">
                            <button
                                className="secondary-button"
                                onClick={() =>
                                    onEdit(dataset)
                                }
                            >
                                Edit
                            </button>

                            <button
                                className="danger-button"
                                onClick={() =>
                                    onDelete(dataset.id)
                                }
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </article>
            ))}
        </div>
    );
}

export default DatasetList;