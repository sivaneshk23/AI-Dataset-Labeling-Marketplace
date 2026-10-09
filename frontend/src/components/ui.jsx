/**
 * Shared presentation primitives.
 *
 * Every screen is composed from these small building blocks so panels, badges
 * and metric tiles stay visually consistent (and responsive) across the app.
 */

import { humanise } from "../utils/format";


/**
 * Render the heading of a workspace screen.
 *
 * @param {object} props Component props.
 * @param {string} props.title Screen title.
 * @param {string} [props.description] Short explanation under the title.
 * @param {string} [props.eyebrow] Small label rendered above the title.
 * @param {React.ReactNode} [props.actions] Buttons rendered on the right.
 */
export function PageHeader({ title, description, eyebrow, actions }) {
    return (
        <header className="page-heading">
            <div>
                {eyebrow && <p className="eyebrow">{eyebrow}</p>}

                <h1>{title}</h1>

                {description && <p>{description}</p>}
            </div>

            {actions && <div className="page-heading-actions">{actions}</div>}
        </header>
    );
}


/**
 * Render a metric tile used by the dashboard and analytics screens.
 *
 * @param {object} props Component props.
 * @param {string} props.label Metric name.
 * @param {string|number} props.value Metric value.
 * @param {string} [props.hint] Supporting line under the value.
 * @param {string} [props.tone] Accent tone (default, positive, warning).
 */
export function StatCard({ label, value, hint, tone = "default" }) {
    return (
        <article className={`stat-card stat-card-${tone}`}>
            <span className="stat-label">{label}</span>

            <strong className="stat-value">{value}</strong>

            {hint && <span className="stat-hint">{hint}</span>}
        </article>
    );
}


/**
 * Render a coloured pill for a workflow status, role or decision.
 *
 * @param {object} props Component props.
 * @param {string} props.status Raw status value.
 */
export function StatusBadge({ status }) {
    const tone = String(status || "").toLowerCase();

    return (
        <span className={`status-badge status-${tone}`}>
            {humanise(status)}
        </span>
    );
}


/**
 * Render a horizontal progress bar.
 *
 * @param {object} props Component props.
 * @param {number} props.value Percentage between 0 and 100.
 * @param {string} [props.label] Caption shown above the bar.
 */
export function ProgressBar({ value, label }) {
    const safeValue = Math.min(Math.max(Number(value) || 0, 0), 100);

    return (
        <div className="progress-block">
            <div className="progress-meta">
                <span>{label || "Progress"}</span>
                <strong>{Math.round(safeValue)}%</strong>
            </div>

            <div
                className="progress-track"
                role="progressbar"
                aria-valuenow={Math.round(safeValue)}
                aria-valuemin="0"
                aria-valuemax="100"
                aria-label={label || "Progress"}
            >
                <span
                    className="progress-fill"
                    style={{ width: `${safeValue}%` }}
                />
            </div>
        </div>
    );
}


/**
 * Render a placeholder for an empty list or an empty selection.
 *
 * @param {object} props Component props.
 * @param {string} props.title Primary message.
 * @param {string} [props.description] Optional supporting message.
 */
export function EmptyState({ title, description }) {
    return (
        <div className="empty-state">
            <h3>{title}</h3>

            {description && <p>{description}</p>}
        </div>
    );
}


/**
 * Render the inline error banner used by every screen.
 *
 * @param {object} props Component props.
 * @param {string} props.message Error text, hidden when empty.
 */
export function ErrorBanner({ message }) {
    if (!message) {
        return null;
    }

    return (
        <div className="error-banner" role="alert">
            {message}
        </div>
    );
}


/**
 * Render the inline success banner used after a completed action.
 *
 * @param {object} props Component props.
 * @param {string} props.message Success text, hidden when empty.
 */
export function SuccessBanner({ message }) {
    if (!message) {
        return null;
    }

    return (
        <div className="success-banner" role="status">
            {message}
        </div>
    );
}


/**
 * Render a labelled key/value line inside detail cards.
 *
 * @param {object} props Component props.
 * @param {string} props.label Field label.
 * @param {React.ReactNode} props.children Field value.
 */
export function DetailRow({ label, children }) {
    return (
        <div className="detail-row">
            <span className="detail-label">{label}</span>
            <span className="detail-value">{children}</span>
        </div>
    );
}


/**
 * Render the loading placeholder used while a screen loads its data.
 *
 * @param {object} props Component props.
 * @param {string} [props.message] Message shown to the user.
 */
export function LoadingState({ message = "Loading..." }) {
    return (
        <div className="loading-state" role="status">
            <span className="loading-dot" />

            <p>{message}</p>
        </div>
    );
}
