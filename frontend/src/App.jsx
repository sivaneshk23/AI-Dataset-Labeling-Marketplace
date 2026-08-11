import { useState } from "react";

import DashboardPage from "./pages/DashboardPage";
import DatasetPage from "./pages/DatasetPage";

function App() {
    const [activePage, setActivePage] =
        useState("dashboard");

    return (
        <div className="app-shell">
            <header className="navbar">
                <div className="brand">
                    <span className="brand-mark">
                        AI
                    </span>

                    <span>
                        Dataset Marketplace
                    </span>
                </div>

                <nav>
                    <button
                        className={
                            activePage === "dashboard"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("dashboard")
                        }
                    >
                        Dashboard
                    </button>

                    <button
                        className={
                            activePage === "datasets"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("datasets")
                        }
                    >
                        Datasets
                    </button>
                </nav>
            </header>

            <main>
                {activePage === "dashboard" && (
                    <DashboardPage />
                )}

                {activePage === "datasets" && (
                    <DatasetPage />
                )}
            </main>

            <footer className="footer">
                <span>
                    AI Dataset Labeling Marketplace
                </span>

                <span>
                    Capstone Project · R2021
                </span>
            </footer>
        </div>
    );
}

export default App;