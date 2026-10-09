"""Role definitions and helpers for role-based access control.

The platform supports three distinct roles. Self-registration is limited to the
two operational roles, while accounts with full administrative rights are
created or promoted by an existing administrator.
"""

DATASET_OWNER = "dataset_owner"
ANNOTATOR = "annotator"
ADMINISTRATOR = "administrator"

ALLOWED_ROLES = frozenset(
    {
        DATASET_OWNER,
        ANNOTATOR,
        ADMINISTRATOR,
    }
)

ROLE_LABELS = {
    DATASET_OWNER: "Dataset Owner",
    ANNOTATOR: "Annotator",
    ADMINISTRATOR: "Administrator",
}

# Roles a visitor may select while registering.
SELF_REGISTERABLE_ROLES = frozenset(
    {
        DATASET_OWNER,
        ANNOTATOR,
    }
)

# Roles allowed to configure datasets, jobs, assignments and quality review.
MANAGEMENT_ROLES = (
    DATASET_OWNER,
    ADMINISTRATOR,
)

DEFAULT_ROLE = ANNOTATOR


def normalise_role(role: str) -> str:
    """Normalise a role string to the canonical ``snake_case`` form."""
    return str(role).strip().lower().replace("-", "_").replace(" ", "_")


def is_valid_role(role: str) -> bool:
    """Return True when *role* is one of the supported platform roles."""
    return normalise_role(role) in ALLOWED_ROLES


def role_label(role: str) -> str:
    """Return a human readable label for *role*."""
    return ROLE_LABELS.get(normalise_role(role), "Unknown Role")
