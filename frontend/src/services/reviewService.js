const API_BASE_URL = "http://127.0.0.1:8000";


function getAuthHeaders() {
    const token = localStorage.getItem("access_token");

    return token
        ? {
            Authorization: `Bearer ${token}`,
        }
        : {};
}


async function handleResponse(response) {
    if (!response.ok) {
        let message = "Request failed.";

        try {
            const errorData = await response.json();

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


export async function getReviews() {
    const response = await fetch(
        `${API_BASE_URL}/api/reviews`,
        {
            method: "GET",
            headers: {
                ...getAuthHeaders(),
            },
        }
    );

    return handleResponse(response);
}


export async function createReview(reviewData) {
    const response = await fetch(
        `${API_BASE_URL}/api/reviews`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify(reviewData),
        }
    );

    return handleResponse(response);
}


export async function updateReview(
    reviewId,
    reviewData
) {
    const response = await fetch(
        `${API_BASE_URL}/api/reviews/${reviewId}`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify(reviewData),
        }
    );

    return handleResponse(response);
}


export async function deleteReview(reviewId) {
    const response = await fetch(
        `${API_BASE_URL}/api/reviews/${reviewId}`,
        {
            method: "DELETE",
            headers: {
                ...getAuthHeaders(),
            },
        }
    );

    return handleResponse(response);
}