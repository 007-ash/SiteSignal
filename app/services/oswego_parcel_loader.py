import sys
from datetime import UTC, datetime
from typing import Any

from geoalchemy2.shape import from_shape
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import SessionFactory
from app.models.dataset_manifest import DatasetManifest
from app.models.load_run import LoadRun
from app.models.parcel import Parcel
from app.services.oswego_parcel_geometry import ANALYSIS_EPSG
from app.services.oswego_parcel_ingestion import (
    PARCEL_QUERY_URL,
    fetch_new_haven_parcels,
    source_snapshot_sha256,
)
from app.services.oswego_parcel_transform import (
    NormalizedParcel,
    normalize_parcels,
)

DATASET_NAME = "Oswego County Active Tax Parcels - New Haven subset"
SOURCE_AGENCY = "Oswego County GIS / Department of Real Property Tax Services"
SNAPSHOT_FILE_NAME = "oswego-new-haven-parcels.json"
SOURCE_CRS = "EPSG:2261"


def _parcel_values(
    parcel: NormalizedParcel,
    load_run_id: int,
) -> dict[str, Any]:
    """Map one normalized parcel to its database values."""
    return {
        "load_run_id": load_run_id,
        "source_global_id": parcel.source_global_id,
        "source_acres": parcel.source_acres,
        "swis_code": parcel.swis_code,
        "print_key": parcel.print_key,
        "source_object_id": parcel.source_object_id,
        "source_parcel_id": parcel.source_parcel_id,
        "property_class_code": parcel.property_class_code,
        "property_class": parcel.property_class,
        "municipality": parcel.municipality,
        "geometry": from_shape(
            parcel.geometry,
            srid=ANALYSIS_EPSG,
        ),
        "gross_acres": parcel.gross_acres,
        "tax_status_date": parcel.tax_status_date,
    }


def _upsert_parcels(
    session: Session,
    parcels: list[NormalizedParcel],
    load_run_id: int,
) -> None:
    """Insert or update parcels using the source GlobalID."""
    rows = [_parcel_values(parcel, load_run_id) for parcel in parcels]

    if not rows:
        return

    statement = insert(Parcel).values(rows)

    session.execute(
        statement.on_conflict_do_update(
            constraint="uq_parcel_source_global_id",
            set_={
                "load_run_id": statement.excluded.load_run_id,
                "source_acres": statement.excluded.source_acres,
                "swis_code": statement.excluded.swis_code,
                "print_key": statement.excluded.print_key,
                "source_object_id": statement.excluded.source_object_id,
                "source_parcel_id": statement.excluded.source_parcel_id,
                "property_class_code": statement.excluded.property_class_code,
                "property_class": statement.excluded.property_class,
                "municipality": statement.excluded.municipality,
                "geometry": statement.excluded.geometry,
                "gross_acres": statement.excluded.gross_acres,
                "tax_status_date": statement.excluded.tax_status_date,
            },
        )
    )


def _get_or_create_manifest_id(
    *,
    snapshot_sha256: str,
    source_vintage: str,
    record_count: int,
) -> int:
    """Return the manifest ID for the exact source snapshot."""
    with SessionFactory.begin() as session:
        manifest = session.scalar(
            select(DatasetManifest).where(
                DatasetManifest.file_sha256 == snapshot_sha256
            )
        )

        if manifest is None:
            manifest = DatasetManifest(
                dataset_name=DATASET_NAME,
                source_agency=SOURCE_AGENCY,
                source_url=PARCEL_QUERY_URL,
                source_vintage=source_vintage,
                acquired_at=datetime.now(UTC),
                file_name=SNAPSHOT_FILE_NAME,
                file_sha256=snapshot_sha256,
                source_crs=SOURCE_CRS,
                record_count=record_count,
            )
            session.add(manifest)
            session.flush()

        return manifest.id


def load_new_haven_parcels(
    *,
    source_vintage: str,
) -> int:
    """Fetch, normalize, and idempotently load New Haven parcels."""
    source_vintage = source_vintage.strip()

    if not source_vintage:
        raise ValueError("source_vintage must not be blank")

    features = fetch_new_haven_parcels()
    snapshot_sha256 = source_snapshot_sha256(features)
    parcels, rejected = normalize_parcels(features)

    rows_read = len(features)
    rows_loaded = len(parcels)
    rows_rejected = len(rejected)

    if rows_loaded + rows_rejected != rows_read:
        raise RuntimeError("Loaded and rejected counts do not match rows read")

    manifest_id = _get_or_create_manifest_id(
        snapshot_sha256=snapshot_sha256,
        source_vintage=source_vintage,
        record_count=rows_read,
    )

    # Commit the running record first so a later failure remains visible.
    with SessionFactory.begin() as session:
        load_run = LoadRun(
            dataset_manifest_id=manifest_id,
            status="running",
            rows_read=rows_read,
            rows_loaded=0,
            rows_rejected=rows_rejected,
        )
        session.add(load_run)
        session.flush()
        load_run_id = load_run.id

    try:
        with SessionFactory.begin() as session:
            _upsert_parcels(
                session=session,
                parcels=parcels,
                load_run_id=load_run_id,
            )

            session.execute(
                update(LoadRun)
                .where(LoadRun.id == load_run_id)
                .values(
                    status="succeeded",
                    rows_loaded=rows_loaded,
                    completed_at=datetime.now(UTC),
                    error_message=None,
                )
            )
    except Exception as error:
        with SessionFactory.begin() as session:
            session.execute(
                update(LoadRun)
                .where(LoadRun.id == load_run_id)
                .values(
                    status="failed",
                    completed_at=datetime.now(UTC),
                    error_message=str(error),
                )
            )
        raise

    print(f"load_run_id={load_run_id}")
    print(f"source_snapshot_sha256={snapshot_sha256}")
    print(f"rows_read={rows_read}")
    print(f"rows_loaded={rows_loaded}")
    print(f"rows_rejected={rows_rejected}")

    for rejected_parcel in rejected:
        source_id = rejected_parcel.source_global_id or "unknown"
        print(f"rejection={source_id}: {rejected_parcel.reason}")

    return load_run_id


def main() -> None:
    """Run the bounded loader from the command line."""
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m app.services.oswego_parcel_loader <source-vintage>"
        )

    load_new_haven_parcels(source_vintage=sys.argv[1])


if __name__ == "__main__":
    main()
