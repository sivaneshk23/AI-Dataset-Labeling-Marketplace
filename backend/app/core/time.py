"""Time helpers shared by the persistence layer.

``datetime.utcnow()`` is deprecated from Python 3.12 onwards, therefore the
project stores naive UTC timestamps produced by :func:`utc_now`.
"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC time as a naive ``datetime``.

    Returns:
        A timezone stripped ``datetime`` in UTC, suitable for the
        ``TIMESTAMP`` columns used by the marketplace tables.
    """
    return datetime.now(UTC).replace(tzinfo=None)
