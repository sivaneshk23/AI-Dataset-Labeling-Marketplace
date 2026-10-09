"""Annotation task model and workflow status rules."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.core.time import utc_now

TASK_STATUSES = ("pending", "in_progress", "submitted", "approved", "rejected")
OPEN_TASK_STATUSES = ("pending", "in_progress", "rejected")


class AnnotationTask(Base):
    """Represent one unit of annotation work inside a labeling job."""

    __tablename__ = "annotation_tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'submitted', 'approved', 'rejected')",
            name="chk_annotation_task_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("labeling_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataset_records.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
