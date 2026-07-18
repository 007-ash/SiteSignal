from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from pyproj import Transformer
from shapely.geometry import LinearRing, MultiPolygon, Polygon
from shapely.ops import transform as shapely_transform
from shapely.validation import explain_validity

# ArcGIS returns the Oswego parcel coordinates in EPSG:2261.
SOURCE_EPSG = 2261

# SiteSignal stores and analyzes parcel geometry in EPSG:6535.
# This projected CRS uses feet, which makes acreage calculations practical.
ANALYSIS_EPSG = 6535

# One acre contains exactly 43,560 square feet.
SQUARE_FEET_PER_ACRE = Decimal("43560")

# Store calculated acreage to six decimal places.
ACRE_PRECISION = Decimal("0.000001")


# Create the reusable coordinate transformer once when the module loads.

# always_xy=True ensures coordinates are interpreted consistently as:
# x = east/west
# y = north/south
TRANSFORMER = Transformer.from_crs(
    SOURCE_EPSG,
    ANALYSIS_EPSG,
    always_xy=True,
)


class ParcelTransformError(ValueError):
    """Raised when a source parcel cannot be transformed safely."""


@dataclass(frozen=True)
class TransformedParcelGeometry:
    """
    Represents one parcel that passed geometry transformation.

    This object stores the minimum information produced by this stage:

    - the source GlobalID, so the result can be traced to ArcGIS;
    - the valid EPSG:6535 geometry;
    - the acreage calculated from that geometry.

    frozen=True prevents these values from being changed accidentally
    after the object is created.
    """

    source_global_id: str
    geometry: MultiPolygon
    gross_acres: Decimal


@dataclass(frozen=True)
class RejectedParcelGeometry:
    """
    Represents one parcel that could not be transformed.

    source_global_id may be None because a badly formed source record
    might fail before we can successfully read its GlobalID.

    reason contains the exact ParcelTransformError message so the
    rejection remains visible and debuggable.
    """

    source_global_id: str | None
    reason: str


def _normalize_ring(
    raw_ring: list[list[float]],
) -> list[tuple[float, float]]:
    """
    Convert one ArcGIS polygon ring into clean Shapely coordinates.

    ArcGIS gives us coordinates as nested lists:

        [[x1, y1], [x2, y2], ...]

    Shapely works well with coordinate tuples:

        [(x1, y1), (x2, y2), ...]

    A valid polygon ring must also end at the same coordinate where it began.
    """

    coordinates = [(float(position[0]), float(position[1])) for position in raw_ring]

    # A polygon requires at least three distinct corner coordinates.
    if len(coordinates) < 3:
        raise ParcelTransformError("Polygon ring has fewer than three coordinates")

    # Close the ring when the source did not repeat the first coordinate.
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    # Once closed, the ring must contain at least four positions:
    # three corners plus the repeated starting coordinate.
    if len(coordinates) < 4:
        raise ParcelTransformError("Closed polygon ring has fewer than four positions")

    return coordinates


def esri_rings_to_multipolygon(
    rings: list[list[list[float]]],
) -> MultiPolygon:
    """
    Convert ArcGIS polygon rings into a Shapely MultiPolygon.

    ArcGIS sends polygon geometry as a collection of rings. Some rings are
    exterior boundaries, while others represent holes inside those boundaries.

    """

    if not rings:
        raise ParcelTransformError("Parcel geometry contains no rings")

    shells: list[list[tuple[float, float]]] = []
    holes: list[list[tuple[float, float]]] = []

    for raw_ring in rings:
        coordinates = _normalize_ring(raw_ring)

        # LinearRing lets Shapely inspect the direction of the coordinates.
        linear_ring = LinearRing(coordinates)

        # Under the Esri ring convention:
        # clockwise rings are exterior boundaries;
        # counterclockwise rings are holes.
        if linear_ring.is_ccw:
            holes.append(coordinates)
        else:
            shells.append(coordinates)

    # Without an exterior shell, we cannot construct a parcel polygon.
    if not shells:
        raise ParcelTransformError("Parcel geometry contains no exterior ring")

    polygons: list[Polygon] = []

    # Keep track of holes that have not yet been assigned to a shell.
    unassigned_holes = holes.copy()

    for shell in shells:
        shell_polygon = Polygon(shell)
        contained_holes: list[list[tuple[float, float]]] = []

        for hole in unassigned_holes:
            hole_polygon = Polygon(hole)

            # Use a representative interior point to determine whether
            # this hole belongs inside the current exterior shell.
            if shell_polygon.contains(hole_polygon.representative_point()):
                contained_holes.append(hole)

        # Remove holes that were assigned to this shell.
        unassigned_holes = [
            hole for hole in unassigned_holes if hole not in contained_holes
        ]

        # Build one polygon from its exterior shell and contained holes.
        polygons.append(
            Polygon(
                shell,
                holes=contained_holes,
            )
        )

    # Every hole must belong to an exterior polygon.
    if unassigned_holes:
        raise ParcelTransformError("One or more holes have no containing exterior ring")

    # Store every parcel as a MultiPolygon, even when it has one polygon.
    # This gives the database one consistent geometry type.
    geometry = MultiPolygon(polygons)

    if geometry.is_empty:
        raise ParcelTransformError("Parcel geometry is empty")

    # Tells us whether the problem is a self-intersection, malformed ring, or another exact geometry defect - without attempting to repair it.
    if not geometry.is_valid:
        raise ParcelTransformError(
            f"Source parcel geometry is invalid {explain_validity(geometry)}"
        )

    return geometry


def transform_parcel_geometry(
    feature: dict[str, Any],
) -> tuple[MultiPolygon, Decimal]:
    """
    Transform one raw ArcGIS feature into SiteSignal geometry and acreage.

    Returns:
        1. valid MultiPolygon geometry in EPSG:6535;
        2. gross parcel acreage rounded to six decimal places.
    """

    # Each ArcGIS feature should have a geometry object.
    raw_geometry = feature.get("geometry")

    if not isinstance(raw_geometry, dict):
        raise ParcelTransformError("Parcel feature has no geometry object")

    # ArcGIS polygon coordinates are stored under the "rings" key.
    rings = raw_geometry.get("rings")

    if not isinstance(rings, list):
        raise ParcelTransformError("Parcel geometry has no rings collection")

    # Convert raw Esri rings into a valid Shapely MultiPolygon
    # while still in the source CRS, EPSG:2261.
    source_geometry = esri_rings_to_multipolygon(rings)

    # Reproject every coordinate from EPSG:2261 into EPSG:6535.
    projected_geometry = shapely_transform(
        TRANSFORMER.transform,
        source_geometry,
    )

    # SiteSignal's Parcel table requires MULTIPOLYGON geometry.
    if not isinstance(projected_geometry, MultiPolygon):
        raise ParcelTransformError("Transformed geometry is not a MultiPolygon")

    # Recheck validity after coordinate transformation.
    if projected_geometry.is_empty:
        raise ParcelTransformError("Transformed parcel geometry is empty")

    if not projected_geometry.is_valid:
        raise ParcelTransformError("Transformed parcel geometry is invalid")

    # EPSG:6535 uses feet, so Shapely's area is square feet.
    # Divide by 43,560 to convert square feet into acres.
    gross_acres = (
        Decimal(str(projected_geometry.area)) / SQUARE_FEET_PER_ACRE
    ).quantize(ACRE_PRECISION)

    if gross_acres <= 0:
        raise ParcelTransformError("Calculated gross acreage is not positive")

    return projected_geometry, gross_acres


def _get_source_global_id(feature: dict[str, Any]) -> str:
    """
    Read and validate the source GlobalID from one ArcGIS feature.

    This helper makes sure the attributes object and GlobalID exist
    before the transformation result is accepted.
    """

    attributes = feature.get("attributes")

    # The attributes value must be a dictionary containing source fields.
    if not isinstance(attributes, dict):
        raise ParcelTransformError("Parcel feature has no attributes object")

    global_id = attributes.get("GlobalID")

    # GlobalID must be a nonempty string.
    if not isinstance(global_id, str) or not global_id.strip():
        raise ParcelTransformError("Parcel feature has no valid GlobalID")

    return global_id


def transform_parcel_geometries(
    features: list[dict[str, Any]],
) -> tuple[
    list[TransformedParcelGeometry],
    list[RejectedParcelGeometry],
]:
    """
    Attempt to transform every parcel in the bounded source set.

    Every feature is placed into exactly one of two lists:

    - accepted: transformation succeeded;
    - rejected: transformation raised ParcelTransformError.

    Unexpected programming errors are not swallowed. Only the known,
    deliberate ParcelTransformError is converted into a rejection.
    """

    accepted: list[TransformedParcelGeometry] = []
    rejected: list[RejectedParcelGeometry] = []

    # Process each source feature independently.
    #
    # One malformed parcel should not prevent us from learning whether
    # the other 1,635 parcels are valid.
    for feature in features:
        # Start with None because reading the GlobalID itself may fail.
        source_global_id: str | None = None

        try:
            # Validate and preserve the source identity first.
            source_global_id = _get_source_global_id(feature)

            # Reuse the already-proven single-parcel transformation.
            geometry, gross_acres = transform_parcel_geometry(feature)

            # The feature passed all validation and transformation steps.
            accepted.append(
                TransformedParcelGeometry(
                    source_global_id=source_global_id,
                    geometry=geometry,
                    gross_acres=gross_acres,
                )
            )

        except ParcelTransformError as error:
            # Record the rejection rather than silently skipping it.
            #
            # source_global_id will remain None when the failure occurred
            # before a valid GlobalID could be read.
            rejected.append(
                RejectedParcelGeometry(
                    source_global_id=source_global_id,
                    reason=str(error),
                )
            )

    return accepted, rejected


def main() -> None:
    """
    Transform all parcels in the bounded New Haven source set.

    This is currently a command-line proof. It reports whether every
    source feature was either accepted or rejected and checks that all
    accepted results satisfy the key geometry and acreage invariants.
    """

    from app.services.oswego_parcel_ingestion import (
        fetch_new_haven_parcels,
    )

    # Extract the deterministic 1,636-feature New Haven parcel set.
    features = fetch_new_haven_parcels()

    # Attempt the geometry transformation for every feature.
    accepted, rejected = transform_parcel_geometries(features)

    # Basic accounting totals.
    print(f"source_features={len(features)}")
    print(f"accepted={len(accepted)}")
    print(f"rejected={len(rejected)}")
    print(f"accounted_for={len(accepted) + len(rejected)}")

    if accepted:
        # Every accepted geometry should still be valid.
        all_accepted_valid = all(item.geometry.is_valid for item in accepted)

        # Every accepted parcel should have positive calculated acreage.
        all_acres_positive = all(item.gross_acres > 0 for item in accepted)

        print(f"all_accepted_valid={all_accepted_valid}")
        print(f"all_acres_positive={all_acres_positive}")

    # Show at most the first ten rejection reasons.
    #
    # This keeps terminal output manageable while still making problems
    # visible. The total rejected count is printed above.
    for item in rejected[:10]:
        displayed_id = item.source_global_id or "unknown"

        print(f"rejection={displayed_id}: {item.reason}")


if __name__ == "__main__":
    main()
