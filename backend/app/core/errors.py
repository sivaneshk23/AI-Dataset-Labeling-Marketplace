"""Domain level exceptions shared by the service layer.

The service layer never raises raw :class:`Exception` subclasses for business
failures. It raises one of the errors below, which the API layer converts into
the standard ``{success, data, message}`` envelope with the correct HTTP status
code. Every error inherits from :class:`ValueError` so callers written against
the original API keep working.
"""


class MarketplaceError(ValueError):
    """Base class for every expected business error."""

    status_code = 400
    default_message = "The request could not be processed."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class ValidationError(MarketplaceError):
    """Raised when business validation rules are violated."""

    status_code = 400
    default_message = "The submitted data is not valid."


class NotFoundError(MarketplaceError):
    """Raised when a requested entity does not exist."""

    status_code = 404
    default_message = "The requested resource was not found."


class ConflictError(MarketplaceError):
    """Raised when an operation conflicts with existing data."""

    status_code = 409
    default_message = "The request conflicts with the current state."


class AuthorizationError(MarketplaceError):
    """Raised when authentication is missing or invalid."""

    status_code = 401
    default_message = "Authentication is required."


class PermissionDeniedError(MarketplaceError):
    """Raised when an authenticated user lacks the required role."""

    status_code = 403
    default_message = "You do not have permission to perform this action."


class InvalidStateError(MarketplaceError):
    """Raised when a workflow transition is not allowed."""

    status_code = 409
    default_message = "This action is not allowed in the current state."


class ExternalServiceError(MarketplaceError):
    """Raised when an optional third-party integration fails."""

    status_code = 502
    default_message = "An external service is currently unavailable."
