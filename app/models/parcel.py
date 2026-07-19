from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Parcel(Base):
    __tablename__ = "parcel"

    __table_args__ = (
        UniqueConstraint("source_global_id", name="uq_parcel_source_global_id"),
        CheckConstraint("gross_acres > 0", name="ck_parcel_gross_acres_positive"),
        Index("ix_parcel_geometry", "geometry", postgresql_using="gist"),
        Index("ix_parcel_load_run_id", "load_run_id"),
        Index("ix_parcel_municipality", "municipality"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    load_run_id: Mapped[int] = mapped_column(
        ForeignKey("load_run.id"),
        nullable=False,
    )

    source_global_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    source_acres: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    swis_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    print_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    source_object_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    source_parcel_id: Mapped[str] = mapped_column(String(255), nullable=False)
    property_class_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    property_class: Mapped[str | None] = mapped_column(String(255), nullable=True)
    municipality: Mapped[str] = mapped_column(String(255), nullable=False)

    geometry: Mapped[WKBElement] = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=6535,
            spatial_index=False,
        ),
        nullable=False,
    )

    gross_acres: Mapped[Decimal] = mapped_column(
        Numeric(12, 6),
        nullable=False,
    )

    tax_status_date: Mapped[date | None] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
