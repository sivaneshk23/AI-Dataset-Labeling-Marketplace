"""Annotation review model.

Quality control is the second half of the platform's business logic: a dataset
owner reviews a submitted annotation and records an approval decision together
with a comment. The decision drives the annotation and task status.
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.core.time import utc_now

REVIEW_DECISIONS = (
    "approved",
    "rejected",
    "needs_revision",
)


class AnnotationReview(Base):
    """Represent a quality review decision for a submitted annotation."""

    __tablename__ = "annotation_reviews"

    __table_args__ = (
        CheckConstraint(
            "decision IN ('approved', 'rejected', 'needs_revision')",
            name="chk_annotation_review_decision",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    annotation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "annotations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )
