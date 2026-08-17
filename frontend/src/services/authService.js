const API_BASE_URL = "http://127.0.0.1:8000";


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
            // Keep default error message.
        }

        throw new Error(message);
    }

    return response.json();
}


export async function registerUser(userData) {
    const response = await fetch(
        `${API_BASE_URL}/api/auth/register`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(userData),
        }
    );

    return handleResponse(response);
}


export async function loginUser(credentials) {
    const response = await fetch(
        `${API_BASE_URL}/api/auth/login`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(credentials),
        }
    );

    const data = await handleResponse(response);

    localStorage.setItem(
        "access_token",
        data.access_token
    );

    return data;
}


export function logoutUser() {
    localStorage.removeItem("access_token");
}


export function getAccessToken() {
    return localStorage.getItem(
        "access_token"
    );
}


export function isAuthenticated() {
    return Boolean(getAccessToken());
}
export async function getCurrentUser() {
    const token = getAccessToken();

    if (!token) {
        return null;
    }

    const response = await fetch(
        `${API_BASE_URL}/api/auth/me`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    if (!response.ok) {
        logoutUser();
        return null;
    }

    return response.json();
}