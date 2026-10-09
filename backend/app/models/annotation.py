"""Annotation model.

An annotation is the label an annotator submits for an annotation task. The
model also stores the AI suggested label and confidence so the platform can
measure human/AI agreement as part of the Day 42-59 enhancement.
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.core.time import utc_now

ANNOTATION_STATUSES = (
    "submitted",
    "approved",
    "rejected",
    "needs_revision",
)


class Annotation(Base):
    """Represent a submitted label for one annotation task."""

    __tablename__ = "annotations"

    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted', 'approved', 'rejected', 'needs_revision')",
            name="chk_annotation_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey(
            "annotation_tasks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    annotator_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_suggested_label: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    ai_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="submitted",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
