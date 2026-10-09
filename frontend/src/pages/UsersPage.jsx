import { useEffect, useState } from "react";

import { ErrorBanner, LoadingState, PageHeader, SuccessBanner } from "../components/ui";
import { deleteUser, getUsers, updateUserRole, updateUserStatus } from "../services/userService";

function UsersPage() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    async function loadUsers() {
        setLoading(true);
        try {
            setUsers(await getUsers());
            setError("");
        } catch (requestError) {
            setError(requestError.message || "Unable to load users.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        let cancelled = false;
        async function initialLoad() {
            if (cancelled) return;
            await loadUsers();
        }
        initialLoad();
        return () => { cancelled = true; };
    }, []);

    async function changeRole(user, role) {
        try {
            await updateUserRole(user.id, role);
            setNotice(`${user.name}'s role was updated.`);
            await loadUsers();
        } catch (requestError) { setError(requestError.message); }
    }

    async function toggleStatus(user) {
        try {
            await updateUserStatus(user.id, !user.is_active);
            setNotice(`${user.name}'s account is now ${!user.is_active ? "active" : "inactive"}.`);
            await loadUsers();
        } catch (requestError) { setError(requestError.message); }
    }

    async function removeUser(user) {
        if (!window.confirm(`Delete ${user.name}'s account?`)) return;
        try {
            await deleteUser(user.id);
            setNotice("User account deleted.");
            await loadUsers();
        } catch (requestError) { setError(requestError.message); }
    }

    return (
        <section className="page">
            <PageHeader eyebrow="Administration" title="User management" description="Manage roles and account status with server-side administrator permissions." actions={<button className="secondary-button" onClick={loadUsers}>Refresh</button>} />
            <ErrorBanner message={error} />
            <SuccessBanner message={notice} />
            {loading && !users.length ? <LoadingState message="Loading accounts…" /> : (
                <div className="content-card table-card">
                    <div className="table-wrap">
                        <table>
                            <thead><tr><th>User</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.id}>
                                        <td><strong>{user.name}</strong><span className="table-secondary">{user.email}</span></td>
                                        <td>
                                            <select value={user.role} onChange={(event) => changeRole(user, event.target.value)}>
                                                <option value="annotator">Annotator</option>
                                                <option value="dataset_owner">Dataset Owner</option>
                                                <option value="administrator">Administrator</option>
                                            </select>
                                        </td>
                                        <td><span className={user.is_active ? "badge-success" : "badge-danger"}>{user.is_active ? "Active" : "Inactive"}</span></td>
                                        <td className="table-actions">
                                            <button className="secondary-button" onClick={() => toggleStatus(user)}>{user.is_active ? "Deactivate" : "Activate"}</button>
                                            <button className="danger-button" onClick={() => removeUser(user)}>Delete</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </section>
    );
}

export default UsersPage;
