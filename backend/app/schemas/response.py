"""Standard JSON response envelope used by every JSON endpoint.

R2021 Section 4.1 requires one consistent JSON structure across the whole
project: ``{success, data, message}``. Modules import :class:`APIResponse` for
their ``response_model`` and :func:`success_response` when building payloads.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standard envelope returned by JSON endpoints."""

    success: bool = Field(
        default=True,
        description="True when the request completed successfully.",
    )
    data: DataT | None = Field(
        default=None,
        description="Endpoint specific payload.",
    )
    message: str = Field(
        default="Request completed successfully.",
        description="Human readable outcome of the request.",
    )


def success_response(
    data: Any = None,
    message: str = "Request completed successfully.",
) -> APIResponse[Any]:
    """Build a successful envelope.

    Args:
        data: Payload returned by the endpoint.
        message: Human readable outcome message.

    Returns:
        An :class:`APIResponse` with ``success=True``.
    """
    return APIResponse[Any](
        success=True,
        data=data,
        message=message,
    )


def error_response(message: str) -> APIResponse[None]:
    """Build a failure envelope.

    Args:
        message: Human readable reason for the failure.

    Returns:
        An :class:`APIResponse` with ``success=False`` and ``data=None``.
    """
    return APIResponse[None](
        success=False,
        data=None,
        message=message,
    )
