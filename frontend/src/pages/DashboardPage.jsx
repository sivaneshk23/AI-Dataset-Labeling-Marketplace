function DashboardPage() {
    return (
        <section className="page dashboard-page">
            <div className="hero">
                <p className="eyebrow">
                    AI Dataset Labeling Marketplace
                </p>

                <h1>
                    Dataset labeling,
                    <br />
                    organized for AI teams.
                </h1>

                <p className="hero-description">
                    Manage datasets and prepare them for
                    structured human labeling workflows.
                </p>
            </div>

            <div className="dashboard-grid">
                <article className="dashboard-card">
                    <span className="card-number">
                        01
                    </span>

                    <h2>Datasets</h2>

                    <p>
                        Create, update, view and delete
                        datasets through the live backend
                        API.
                    </p>
                </article>

                <article className="dashboard-card">
                    <span className="card-number">
                        02
                    </span>

                    <h2>Labeling Jobs</h2>

                    <p>
                        Create structured labeling jobs
                        from datasets. This module is
                        coming next.
                    </p>
                </article>

                <article className="dashboard-card">
                    <span className="card-number">
                        03
                    </span>

                    <h2>PostgreSQL</h2>

                    <p>
                        Application data is persisted in
                        the project's PostgreSQL database.
                    </p>
                </article>
            </div>
        </section>
    );
}

export default DashboardPage;