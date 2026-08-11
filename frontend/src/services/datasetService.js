const API_BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(response) {
    const body = await response.json();

    if (!response.ok) {
        throw new Error(
            body.detail || body.message || "Request failed"
        );
    }

    return body;
}

export async function getDatasets() {
    const response = await fetch(
        `${API_BASE_URL}/api/datasets`
    );

    return handleResponse(response);
}

export async function createDataset(dataset) {
    const response = await fetch(
        `${API_BASE_URL}/api/datasets`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(dataset),
        }
    );

    return handleResponse(response);
}

export async function updateDataset(datasetId, dataset) {
    const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(dataset),
        }
    );

    return handleResponse(response);
}

export async function deleteDataset(datasetId) {
    const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}`,
        {
            method: "DELETE",
        }
    );

    return handleResponse(response);
}