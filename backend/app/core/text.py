"""Reusable text helpers used by analytics and AI quality control.

Keeping normalisation in one place means human labels and AI suggested labels
are compared consistently across the whole application.
"""

import re

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "with",
    }
)


def normalise_label(label: str | None) -> str:
    """Normalise a label for reliable comparison.

    Args:
        label: Raw label text.

    Returns:
        A lowercase, whitespace collapsed label.
    """
    if label is None:
        return ""

    return " ".join(str(label).split()).strip().lower()


def tokenize(text: str | None) -> list[str]:
    """Split text into lowercase alphanumeric tokens without stop words."""
    if not text:
        return []

    tokens = [
        token
        for token in _TOKEN_PATTERN.findall(str(text).lower())
        if token not in STOP_WORDS
    ]

    return [_singularise(token) for token in tokens]


def _singularise(token: str) -> str:
    """Apply a very small stemming rule to group simple plurals."""
    if len(token) > 3 and token.endswith("ies"):
        return token[:-3] + "y"

    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]

    return token


def labels_match(
    first: str | None,
    second: str | None,
) -> bool:
    """Return True when two labels refer to the same value."""
    return normalise_label(first) == normalise_label(second)
