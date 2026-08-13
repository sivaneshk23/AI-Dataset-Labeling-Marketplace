const API_BASE_URL = "http://127.0.0.1:8000";

function getAuthHeaders() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        throw new Error("Authentication token not found.");
    }

    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    };
}

export async function getAssignments() {
    const response = await fetch(
        `${API_BASE_URL}/api/assignments`,
        {
            headers: getAuthHeaders(),
        }
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load assignments: ${response.status}`
        );
    }

    return response.json();
}

export async function getAssignmentsByJob(jobId) {
    const response = await fetch(
        `${API_BASE_URL}/api/assignments/job/${jobId}`,
        {
            headers: getAuthHeaders(),
        }
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load job assignments: ${response.status}`
        );
    }

    return response.json();
}

export async function createAssignment(
    jobId,
    workerId
) {
    const response = await fetch(
        `${API_BASE_URL}/api/assignments`,
        {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                job_id: Number(jobId),
                worker_id: Number(workerId),
            }),
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(
            () => ({})
        );

        throw new Error(
            errorData.detail ||
            `Failed to create assignment: ${response.status}`
        );
    }

    return response.json();
}

export async function updateAssignment(
    assignmentId,
    status
) {
    const response = await fetch(
        `${API_BASE_URL}/api/assignments/${assignmentId}`,
        {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                status,
            }),
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(
            () => ({})
        );

        throw new Error(
            errorData.detail ||
            `Failed to update assignment: ${response.status}`
        );
    }

    return response.json();
}

export async function deleteAssignment(
    assignmentId
) {
    const response = await fetch(
        `${API_BASE_URL}/api/assignments/${assignmentId}`,
        {
            method: "DELETE",
            headers: getAuthHeaders(),
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(
            () => ({})
        );

        throw new Error(
            errorData.detail ||
            `Failed to delete assignment: ${response.status}`
        );
    }
}