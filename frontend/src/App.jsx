import { useEffect, useState } from "react";

import RegisterPage from "./pages/RegisterPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AnnotationWorkspacePage from "./pages/AnnotationWorkspacePage";
import DashboardPage from "./pages/DashboardPage";
import DatasetPage from "./pages/DatasetPage";
import JobPage from "./pages/JobPage";
import LoginPage from "./pages/LoginPage";
import AssignmentPage from "./pages/AssignmentPage";
import QualityReviewPage from "./pages/QualityReviewPage";
import ReviewPage from "./pages/ReviewPage";
import TaskManagementPage from "./pages/TaskManagementPage";
import UsersPage from "./pages/UsersPage";
import ExportsPage from "./pages/ExportsPage";

import {
    getCurrentUser,
    isAuthenticated,
    logoutUser,
} from "./services/authService";


function App() {
    const [authenticated, setAuthenticated] =
        useState(isAuthenticated());

    const [currentUser, setCurrentUser] =
        useState(null);

    const [loadingUser, setLoadingUser] =
        useState(isAuthenticated());

    const [showRegister, setShowRegister] =
        useState(false);

    const [activePage, setActivePage] =
        useState("dashboard");


    useEffect(() => {
    if (!authenticated) {
        return;
    }

    let cancelled = false;

    async function loadCurrentUser() {
        setLoadingUser(true);

        try {
            const user = await getCurrentUser();

            if (cancelled) {
                return;
            }

            if (!user) {
                setAuthenticated(false);
                setCurrentUser(null);
                return;
            }

            setCurrentUser(user);
        } catch {
            if (cancelled) {
                return;
            }

            logoutUser();
            setAuthenticated(false);
            setCurrentUser(null);
        } finally {
            if (!cancelled) {
                setLoadingUser(false);
            }
        }
    }

    loadCurrentUser();

    return () => {
        cancelled = true;
    };
}, [authenticated]);


    function handleLogin() {
        setAuthenticated(true);
        setActivePage("dashboard");
    }


    function handleLogout() {
        logoutUser();
        setCurrentUser(null);
        setAuthenticated(false);
        setActivePage("dashboard");
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


    if (loadingUser || !currentUser) {
        return (
            <section className="page-section">
                <div className="page-header">
                    <h1>Loading account...</h1>
                    <p>
                        Loading your role and permissions.
                    </p>
                </div>
            </section>
        );
    }


    const isOwner =
        currentUser.role === "dataset_owner";

    const isAnnotator =
        currentUser.role === "annotator";

    const isAdministrator =
        currentUser.role === "administrator";


    const canManageDatasets =
        isOwner || isAdministrator;

    const canManageJobs =
        isOwner || isAdministrator;

    const canManageAssignments =
        isOwner || isAdministrator;

    const canManageReviews =
        isOwner || isAdministrator;

    // Annotation task management and the per-annotation quality decisions are
    // management screens, exactly like the backend role guards require.
    const canManageTasks =
        isOwner || isAdministrator;

    const canReviewQuality =
        isOwner || isAdministrator;

    // Only annotator accounts may submit labels (enforced by the service
    // layer), so the annotation workspace is annotator-only.
    const canAnnotate =
        isAnnotator;

    // Progress metrics are readable by every authenticated role; the AI tab
    // inside the screen is hidden for annotators because the insights
    // endpoint requires a management role.
    const canViewAnalytics = true;



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


                    {isAdministrator && (
                        <button
                            className={
                                activePage === "users"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() => setActivePage("users")}
                        >
                            Users
                        </button>
                    )}

                    {canManageDatasets && (
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
                    )}


                    {canManageJobs && (
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
                    )}


                    {canManageTasks && (
                        <button
                            className={
                                activePage === "tasks"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage("tasks")
                            }
                        >
                            Tasks
                        </button>
                    )}


                    {canManageAssignments && (
                        <button
                            className={
                                activePage === "assignments"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage(
                                    "assignments"
                                )
                            }
                        >
                            Assignments
                        </button>
                    )}


                    {canManageReviews && (
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
                    )}


                    {canReviewQuality && (
                        <button
                            className={
                                activePage === "quality"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage("quality")
                            }
                        >
                            Quality Review
                        </button>
                    )}


                    {canManageReviews && (
                        <button
                            className={
                                activePage === "exports"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() => setActivePage("exports")}
                        >
                            Exports
                        </button>
                    )}

                    {canViewAnalytics && (
                        <button
                            className={
                                activePage === "analytics"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage("analytics")
                            }
                        >
                            Analytics
                        </button>
                    )}


                    {canAnnotate && (
                        <button
                            className={
                                activePage === "workspace"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage("workspace")
                            }
                        >
                            Workspace
                        </button>
                    )}


                    {isAnnotator && (
                        <button
                            className={
                                activePage === "assignments"
                                    ? "nav-button active"
                                    : "nav-button"
                            }
                            onClick={() =>
                                setActivePage(
                                    "assignments"
                                )
                            }
                        >
                            My Assignments
                        </button>
                    )}

                    <span
                        className={`status-badge status-${currentUser.role}`}
                        title={currentUser.email}
                    >
                        {currentUser.name} · {currentUser.role}
                    </span>


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
                    <DashboardPage
                        currentUser={currentUser}
                        onNavigate={setActivePage}
                    />
                )}


                {activePage === "datasets" &&
                    canManageDatasets && (
                        <DatasetPage />
                    )}


                {activePage === "jobs" &&
                    canManageJobs && (
                        <JobPage />
                    )}


                {activePage === "tasks" &&
                    canManageTasks && (
                        <TaskManagementPage />
                    )}


                {activePage === "assignments" && (
                    <AssignmentPage
                        currentUser={currentUser}
                    />
                )}


                {activePage === "reviews" &&
                    canManageReviews && (
                        <ReviewPage />
                    )}


                {activePage === "quality" &&
                    canReviewQuality && (
                        <QualityReviewPage />
                    )}


                {activePage === "users" &&
                    isAdministrator && (
                        <UsersPage />
                    )}

                {activePage === "exports" &&
                    canManageReviews && (
                        <ExportsPage />
                    )}

                {activePage === "analytics" &&
                    canViewAnalytics && (
                        <AnalyticsPage
                            currentUser={currentUser}
                        />
                    )}


                {activePage === "workspace" &&
                    canAnnotate && (
                        <AnnotationWorkspacePage />
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