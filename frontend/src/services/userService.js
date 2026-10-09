/**
 * User directory and administration API calls.
 *
 * Annotators are listed through the directory endpoint (available to the
 * management roles), while full account administration is reserved for the
 * administrator role.
 */

import { buildQueryString, request } from "./apiClient";


/**
 * List every registered account (administrator only).
 *
 * @returns {Promise<Array<object>>} All accounts on the platform.
 */
export async function getUsers() {
    return request("/api/users");
}


/**
 * List annotator accounts available for assignment.
 *
 * @param {object} [filters] Optional filters.
 * @param {boolean} [filters.activeOnly] Only active accounts (default true).
 * @returns {Promise<Array<object>>} Annotator accounts.
 */
export async function getAnnotators(filters = {}) {
    return request(
        `/api/users/annotators${buildQueryString({
            active_only: filters.activeOnly === false ? "false" : "true",
        })}`
    );
}


/**
 * Fetch the profile of the authenticated user.
 *
 * @returns {Promise<object>} The caller profile.
 */
export async function getMyProfile() {
    return request("/api/users/me");
}


/**
 * Change the role of an account (administrator only).
 *
 * @param {number|string} userId Account identifier.
 * @param {string} role New role (dataset_owner, annotator, administrator).
 * @returns {Promise<object>} The updated account.
 */
export async function updateUserRole(userId, role) {
    return request(`/api/users/${userId}/role`, {
        method: "PATCH",
        body: { role },
    });
}


/**
 * Activate or deactivate an account (administrator only).
 *
 * @param {number|string} userId Account identifier.
 * @param {boolean} isActive New activation state.
 * @returns {Promise<object>} The updated account.
 */
export async function updateUserStatus(userId, isActive) {
    return request(`/api/users/${userId}/status`, {
        method: "PATCH",
        body: { is_active: isActive },
    });
}


/**
 * Delete an account (administrator only).
 *
 * @param {number|string} userId Account identifier.
 * @returns {Promise<null>} Null when the account has been deleted.
 */
export async function deleteUser(userId) {
    return request(`/api/users/${userId}`, {
        method: "DELETE",
    });
}
