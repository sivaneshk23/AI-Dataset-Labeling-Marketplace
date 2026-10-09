/**
 * Shared HTTP client used by every frontend service.
 *
 * The backend (R2021 Section 4.1) always answers with one consistent JSON
 * envelope: `{success, data, message}`. Centralising the fetch logic here means
 * each module service only describes its endpoint, while this file takes care
 * of
 *
 * * resolving the API base URL from `VITE_API_URL` (with a localhost default),
 * * attaching the JWT bearer token from `localStorage`,
 * * unwrapping `data` and turning `message`/`detail` into a readable Error,
 * * streaming CSV exports as a browser download.
 */

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const TOKEN_STORAGE_KEY = "access_token";

export const API_BASE_URL = (
    import.meta.env.VITE_API_URL || DEFAULT_API_BASE_URL
).replace(/\/+$/, "");


/**
 * Error raised for any non-2xx API response.
 *
 * Carrying the HTTP status lets screens react to specific conditions (for
 * example a 403 permission error versus a 404 missing record) instead of
 * showing a generic failure.
 */
export class ApiError extends Error {
    constructor(message, status, data) {
        super(message);

        this.name = "ApiError";
        this.status = status;
        this.data = data;
    }
}


/**
 * Read the stored JWT access token.
 *
 * @returns {string|null} The token, or null when the visitor is signed out.
 */
export function getAccessToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
}


/**
 * Persist the JWT access token after a successful login.
 *
 * @param {string} token Signed JWT returned by the backend.
 */
export function setAccessToken(token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
}


/**
 * Remove the stored JWT access token on logout or on an expired session.
 */
export function clearAccessToken() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
}


function buildHeaders(extraHeaders, requiresAuth) {
    const headers = {
        Accept: "application/json",
        ...extraHeaders,
    };

    if (requiresAuth) {
        const token = getAccessToken();

        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
    }

    return headers;
}


function extractErrorMessage(payload, status) {
    if (typeof payload === "string" && payload.trim()) {
        return payload;
    }

    if (payload && typeof payload === "object") {
        if (typeof payload.message === "string" && payload.message.trim()) {
            return payload.message;
        }

        if (typeof payload.detail === "string" && payload.detail.trim()) {
            return payload.detail;
        }

        if (Array.isArray(payload.data) && payload.data.length > 0) {
            const firstIssue = payload.data[0];

            if (firstIssue && firstIssue.message) {
                const field = firstIssue.field
                    ? `${firstIssue.field}: `
                    : "";

                return `${field}${firstIssue.message}`;
            }
        }
    }

    return `Request failed with status ${status}.`;
}


async function parsePayload(response) {
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        try {
            return await response.json();
        } catch {
            return null;
        }
    }

    try {
        return await response.text();
    } catch {
        return null;
    }
}


/**
 * Perform an authenticated JSON request and return the envelope payload.
 *
 * @param {string} path API path beginning with a slash (for example `/api/jobs`).
 * @param {object} [options] Request options.
 * @param {string} [options.method] HTTP method, defaults to GET.
 * @param {object} [options.body] JSON body to serialise.
 * @param {boolean} [options.auth] Attach the bearer token (default true).
 * @param {object} [options.headers] Extra request headers.
 * @returns {Promise<object>} The complete `{success, data, message}` envelope.
 * @throws {ApiError} When the response status is not successful.
 */
export async function requestEnvelope(path, options = {}) {
    const {
        method = "GET",
        body,
        auth = true,
        headers: extraHeaders = {},
    } = options;

    const headers = buildHeaders(extraHeaders, auth);
    const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

    if (body !== undefined && body !== null && !isFormData) {
        headers["Content-Type"] = "application/json";
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method,
            headers,
            body:
                body === undefined || body === null
                    ? undefined
                    : isFormData
                        ? body
                        : JSON.stringify(body),
        });
    } catch {
        throw new ApiError(
            "Unable to reach the API. Please check your connection and try again.",
            0,
            null
        );
    }

    const payload = await parsePayload(response);

    if (!response.ok) {
        if (response.status === 401 && auth) {
            clearAccessToken();
        }

        throw new ApiError(
            extractErrorMessage(payload, response.status),
            response.status,
            payload
        );
    }

    if (
        payload &&
        typeof payload === "object" &&
        "success" in payload &&
        "data" in payload
    ) {
        return payload;
    }

    return {
        success: true,
        data: payload,
        message: "Request completed successfully.",
    };
}

/**
 * Perform a request and return only the unwrapped `data` payload.
 *
 * @param {string} path API path beginning with a slash.
 * @param {object} [options] Same options accepted by {@link requestEnvelope}.
 * @returns {Promise<*>} The `data` field of the response envelope.
 */
export async function request(path, options = {}) {
    const envelope = await requestEnvelope(path, options);

    return envelope.data;
}


/**
 * Build a query string from defined values only.
 *
 * @param {object} params Key/value pairs to encode.
 * @returns {string} A query string beginning with `?`, or an empty string.
 */
export function buildQueryString(params = {}) {
    const search = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
            search.append(key, value);
        }
    });

    const query = search.toString();

    return query ? `?${query}` : "";
}


/**
 * Download a file produced by the API (for example a CSV dataset export).
 *
 * @param {string} path API path beginning with a slash.
 * @param {string} filename File name suggested to the browser.
 * @returns {Promise<void>} Resolves once the download has been triggered.
 * @throws {ApiError} When the export request fails.
 */
export async function downloadFile(path, filename) {
    let response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method: "GET",
            headers: buildHeaders({}, true),
        });
    } catch {
        throw new ApiError(
            "Unable to reach the API. Please check your connection and try again.",
            0,
            null
        );
    }

    if (!response.ok) {
        const payload = await parsePayload(response);

        throw new ApiError(
            extractErrorMessage(payload, response.status),
            response.status,
            payload
        );
    }

    const blob = await response.blob();
    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(objectUrl);
}

