"""Central logging configuration for the backend.

Basic monitoring is a Review-II requirement: user signup, login and error
events must be logged. Every module obtains its logger through
:func:`get_logger` so log formatting and levels stay consistent.
"""

import logging
import sys

from backend.app.core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging() -> None:
    """Configure the root logger once, writing structured lines to stdout."""
    global _configured

    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())
    root_logger.handlers = [handler]

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger.

    Args:
        name: Logger name, conventionally ``__name__`` of the caller.

    Returns:
        A standard library logger instance.
    """
    return logging.getLogger(name)
