/**
 * Authentication API calls.
 *
 * The backend issues a real JWT after checking the credentials against the
 * database. The token is stored in `localStorage` and attached to every other
 * request by `apiClient.js`.
 */

import {
    clearAccessToken,
    getAccessToken as readAccessToken,
    request,
    requestEnvelope,
    setAccessToken,
} from "./apiClient";


/**
 * Register a dataset owner or annotator account.
 *
 * @param {object} userData Payload with name, email, password and role.
 * @returns {Promise<object>} The public profile of the new account.
 */
export async function registerUser(userData) {
    const envelope = await requestEnvelope("/api/auth/register", {
        method: "POST",
        body: userData,
        auth: false,
    });

    return envelope.data;
}


/**
 * Sign in and store the returned access token.
 *
 * @param {object} credentials Payload with email and password.
 * @returns {Promise<object>} The token payload (`access_token`, `token_type`).
 */
export async function loginUser(credentials) {
    const tokenPayload = await request("/api/auth/login", {
        method: "POST",
        body: credentials,
        auth: false,
    });

    setAccessToken(tokenPayload.access_token);

    return tokenPayload;
}


/**
 * Clear the stored token and sign the visitor out.
 */
export function logoutUser() {
    clearAccessToken();
}


/**
 * Read the stored JWT access token.
 *
 * @returns {string|null} The token, or null when signed out.
 */
export function getAccessToken() {
    return readAccessToken();
}


/**
 * Return True when an access token is stored.
 *
 * @returns {boolean} Authentication state based on the stored token.
 */
export function isAuthenticated() {
    return Boolean(readAccessToken());
}


/**
 * Fetch the profile of the authenticated user.
 *
 * Expired or revoked tokens are cleared so the app falls back to the login
 * screen instead of showing a broken workspace.
 *
 * @returns {Promise<object|null>} The user profile, or null when unavailable.
 */
export async function getCurrentUser() {
    if (!readAccessToken()) {
        return null;
    }

    try {
        return await request("/api/auth/me");
    } catch {
        logoutUser();

        return null;
    }
}
