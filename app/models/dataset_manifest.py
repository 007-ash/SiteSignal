from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DatasetManifest(Base):
    __tablename__ = "dataset_manifest"

    __table_args__ = (
        CheckConstraint(
            "char_length(file_sha256) = 64",
            name="ck_dataset_manifest_sha256_length",
        ),
        CheckConstraint(
            "record_count IS NULL OR record_count >= 0",
            name="ck_dataset_manifest_record_count_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_agency: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_vintage: Mapped[str] = mapped_column(String(100), nullable=False)

    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    file_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    source_crs: Mapped[str] = mapped_column(String(100), nullable=False)

    record_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
