from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from shapely.geometry import MultiPolygon

from app.services.oswego_parcel_geometry import (
    ParcelTransformError,
    transform_parcel_geometry,
)

SUPPORTED_MUNICIPALITY = "New Haven"


@dataclass(frozen=True)
class NormalizedParcel:
    """A validated parcel ready for database loading."""

    source_global_id: UUID
    source_object_id: int
    source_parcel_id: str
    print_key: str | None
    swis_code: str | None
    municipality: str
    tax_status_date: date
    source_acres: Decimal | None
    property_class_code: str | None
    property_class: str | None
    geometry: MultiPolygon
    gross_acres: Decimal


@dataclass(frozen=True)
class RejectedParcel:
    """A parcel rejected during attribute or geometry normalization."""

    source_global_id: str | None
    reason: str


def _get_attributes(feature: dict[str, Any]) -> dict[str, Any]:
    """Return the ArcGIS attributes dictionary."""
    attributes = feature.get("attributes")

    if not isinstance(attributes, dict):
        raise ParcelTransformError("Parcel feature has no attributes object")

    return attributes


def _required_text(
    attributes: dict[str, Any],
    field_name: str,
) -> str:
    """Return a required field as nonempty text."""
    value = attributes.get(field_name)

    if value is None:
        raise ParcelTransformError(f"Required field {field_name} is missing")

    text = str(value).strip()

    if not text:
        raise ParcelTransformError(f"Required field {field_name} is blank")

    return text


def _optional_text(
    attributes: dict[str, Any],
    field_name: str,
) -> str | None:
    """Return an optional field as cleaned text or None."""
    value = attributes.get(field_name)

    if value is None:
        return None

    text = str(value).strip()

    return text or None


def _parse_global_id(attributes: dict[str, Any]) -> UUID:
    """Convert the ArcGIS GlobalID into a Python UUID."""
    raw_global_id = _required_text(
        attributes,
        "GlobalID",
    ).strip("{}")

    try:
        return UUID(raw_global_id)
    except ValueError as error:
        raise ParcelTransformError(
            f"GlobalID is not a valid UUID: {raw_global_id}"
        ) from error


def _parse_object_id(attributes: dict[str, Any]) -> int:
    """Return the required ArcGIS OBJECTID as an integer."""
    value = attributes.get("OBJECTID")

    if value is None or isinstance(value, bool):
        raise ParcelTransformError(f"OBJECTID is not a valid integer: {value}")

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        text = value.strip()

        if not text:
            raise ParcelTransformError("OBJECTID is blank")

        try:
            return int(text)
        except ValueError as error:
            raise ParcelTransformError(
                f"OBJECTID is not a valid integer: {value}"
            ) from error

    raise ParcelTransformError(f"OBJECTID is not a valid integer: {value}")


def _parse_tax_status_date(
    attributes: dict[str, Any],
) -> date:
    """Convert the observed ArcGIS TAX_STATUS value into a date."""
    raw_date = _required_text(
        attributes,
        "TAX_STATUS",
    )

    try:
        return datetime.strptime(
            raw_date,
            "%Y-%m-%d %I:%M:%S %p",
        ).date()
    except ValueError as error:
        raise ParcelTransformError(
            f"TAX_STATUS has an unexpected format: {raw_date}"
        ) from error


def _parse_optional_decimal(
    attributes: dict[str, Any],
    field_name: str,
) -> Decimal | None:
    """Convert an optional numeric source field into Decimal."""
    value = attributes.get(field_name)

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        decimal_value = Decimal(text)
    except InvalidOperation as error:
        raise ParcelTransformError(f"{field_name} is not numeric: {value}") from error

    if not decimal_value.is_finite():
        raise ParcelTransformError(f"{field_name} is not finite: {value}")

    return decimal_value


def normalize_parcel(
    feature: dict[str, Any],
) -> NormalizedParcel:
    """
    Convert one raw ArcGIS feature into a typed parcel.

    Attribute validation and geometry transformation must both succeed.
    """
    attributes = _get_attributes(feature)

    source_global_id = _parse_global_id(attributes)
    source_object_id = _parse_object_id(attributes)
    source_parcel_id = _required_text(attributes, "rpsjoin")
    municipality = _required_text(attributes, "MUNI")
    tax_status_date = _parse_tax_status_date(attributes)

    if municipality != SUPPORTED_MUNICIPALITY:
        raise ParcelTransformError(f"Unsupported municipality: {municipality}")

    geometry, gross_acres = transform_parcel_geometry(feature)

    return NormalizedParcel(
        source_global_id=source_global_id,
        source_object_id=source_object_id,
        source_parcel_id=source_parcel_id,
        print_key=_optional_text(attributes, "PRINT_KEY"),
        swis_code=_optional_text(attributes, "SWIS"),
        municipality=municipality,
        tax_status_date=tax_status_date,
        source_acres=_parse_optional_decimal(
            attributes,
            "ACRES",
        ),
        property_class_code=_optional_text(
            attributes,
            "PRP_CLS_CODE",
        ),
        property_class=_optional_text(
            attributes,
            "PROP_CLASS",
        ),
        geometry=geometry,
        gross_acres=gross_acres,
    )


def normalize_parcels(
    features: list[dict[str, Any]],
) -> tuple[
    list[NormalizedParcel],
    list[RejectedParcel],
]:
    """
    Normalize every feature and retain visible rejection reasons.

    Every source feature is placed into either the normalized collection
    or the rejected collection.
    """
    normalized: list[NormalizedParcel] = []
    rejected: list[RejectedParcel] = []

    for feature in features:
        source_global_id: str | None = None
        attributes = feature.get("attributes")

        if isinstance(attributes, dict):
            raw_global_id = attributes.get("GlobalID")

            if isinstance(raw_global_id, str):
                source_global_id = raw_global_id.strip() or None

        try:
            normalized.append(normalize_parcel(feature))
        except ParcelTransformError as error:
            rejected.append(
                RejectedParcel(
                    source_global_id=source_global_id,
                    reason=str(error),
                )
            )

    return normalized, rejected


def main() -> None:
    """Normalize the complete bounded New Haven source set."""
    from app.services.oswego_parcel_ingestion import (
        fetch_new_haven_parcels,
    )

    features = fetch_new_haven_parcels()
    normalized, rejected = normalize_parcels(features)

    print(f"source_features={len(features)}")
    print(f"normalized={len(normalized)}")
    print(f"rejected={len(rejected)}")
    print(f"accounted_for={len(normalized) + len(rejected)}")

    if normalized:
        sample = normalized[0]

        print(f"sample_global_id={sample.source_global_id}")
        print(f"sample_object_id={sample.source_object_id}")
        print(f"sample_tax_status={sample.tax_status_date}")
        print(f"sample_source_acres={sample.source_acres}")
        print(f"sample_gross_acres={sample.gross_acres}")

    for item in rejected[:10]:
        displayed_id = item.source_global_id or "unknown"

        print(f"rejection={displayed_id}: {item.reason}")


if __name__ == "__main__":
    main()
