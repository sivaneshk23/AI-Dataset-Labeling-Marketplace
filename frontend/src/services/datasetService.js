const API_BASE_URL =
    "http://127.0.0.1:8000";


function getAuthHeaders() {
    const token =
        localStorage.getItem("access_token");

    return token
        ? {
            Authorization: `Bearer ${token}`,
        }
        : {};
}


async function handleResponse(response) {

    if (!response.ok) {

        let message =
            "Request failed.";

        try {
            const errorData =
                await response.json();

            message =
                errorData.detail ||
                errorData.message ||
                message;

        } catch {
            // Keep default message.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}


export async function getDatasets() {

    const response = await fetch(
        `${API_BASE_URL}/api/datasets`,
        {
            method: "GET",
            headers: {
                ...getAuthHeaders(),
            },
        }
    );

    return handleResponse(response);
}


export async function createDataset(datasetData) {

    const response = await fetch(
        `${API_BASE_URL}/api/datasets`,
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json",

                ...getAuthHeaders(),
            },

            body: JSON.stringify(
                datasetData
            ),
        }
    );

    return handleResponse(response);
}


export async function updateDataset(
    datasetId,
    datasetData
) {

    const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}`,
        {
            method: "PUT",

            headers: {
                "Content-Type":
                    "application/json",

                ...getAuthHeaders(),
            },

            body: JSON.stringify(
                datasetData
            ),
        }
    );

    return handleResponse(response);
}


export async function deleteDataset(
    datasetId
) {

    const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}`,
        {
            method: "DELETE",

            headers: {
                ...getAuthHeaders(),
            },
        }
    );

    return handleResponse(response);
}