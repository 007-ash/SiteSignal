from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LoadRun(Base):
    __tablename__ = "load_run"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'succeeded', 'failed')",
            name="ck_load_run_status",
        ),
        CheckConstraint(
            "rows_read >= 0",
            name="ck_load_run_rows_read_nonnegative",
        ),
        CheckConstraint(
            "rows_loaded >= 0",
            name="ck_load_run_rows_loaded_nonnegative",
        ),
        CheckConstraint(
            "rows_rejected >= 0",
            name="ck_load_run_rows_rejected_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    dataset_manifest_id: Mapped[int] = mapped_column(
        ForeignKey("dataset_manifest.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rows_read: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    rows_loaded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    rows_rejected: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
