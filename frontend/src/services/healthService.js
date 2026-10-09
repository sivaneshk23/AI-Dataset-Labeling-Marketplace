/**
 * Health and service metadata API calls.
 *
 * These endpoints are public (no token required) so the login screen can show
 * whether the backend is reachable, and so the deployed smoke test has a
 * predictable call to make.
 */

import { request, requestEnvelope } from "./apiClient";


/**
 * Fetch the liveness status of the backend.
 *
 * @returns {Promise<object|null>} Health payload, or null when unreachable.
 */
export async function getHealth() {
    try {
        return await request("/health", { auth: false });
    } catch {
        return null;
    }
}


/**
 * Fetch the service information returned by the API root.
 *
 * @returns {Promise<object|null>} Service metadata, or null when unreachable.
 */
export async function getServiceInfo() {
    try {
        const envelope = await requestEnvelope("/", { auth: false });

        return envelope.data;
    } catch {
        return null;
    }
}
