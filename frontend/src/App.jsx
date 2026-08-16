import { useState } from "react";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import DatasetPage from "./pages/DatasetPage";
import JobPage from "./pages/JobPage";
import LoginPage from "./pages/LoginPage";
import AssignmentPage from "./pages/AssignmentPage";
import ReviewPage from "./pages/ReviewPage";
import {
    isAuthenticated,
    logoutUser,
} from "./services/authService";


function App() {
    const [authenticated, setAuthenticated] =
        useState(isAuthenticated());
    const [showRegister, setShowRegister] = useState(false);
    const [activePage, setActivePage] =
        useState("dashboard");
    

    function handleLogin() {
        setAuthenticated(true);
        setActivePage("dashboard");
    }


    function handleLogout() {
        logoutUser();
        setAuthenticated(false);
    }


   if (!authenticated) {

    if (showRegister) {
        return (
            <RegisterPage
                onRegistered={() =>
                    setShowRegister(false)
                }
                onBackToLogin={() =>
                    setShowRegister(false)
                }
            />
        );
    }

    return (
        <LoginPage
            onLogin={handleLogin}
            onRegister={() =>
                setShowRegister(true)
            }
        />
    );
}


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


                    <button
                        className={
                            activePage === "jobs"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("jobs")
                        }
                    >
                        Labeling Jobs
                    </button>
                    <button
                        className={
                            activePage === "assignments"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("assignments")
                        }
                    >
                        Assignments
                    </button>
                    <button
                        className={
                            activePage === "reviews"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("reviews")
                        }
            >
                Reviews
                    </button>

                    <button
                        className="nav-button"
                        onClick={handleLogout}
                    >
                        Logout
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

                {activePage === "jobs" && (
                    <JobPage />
                )}
                {activePage === "assignments" && (
                    <AssignmentPage />
                )}
                {activePage === "reviews" && (
                    <ReviewPage />
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