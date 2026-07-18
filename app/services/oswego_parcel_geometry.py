from decimal import Decimal
from typing import Any

from pyproj import Transformer
from shapely.geometry import LinearRing, MultiPolygon, Polygon
from shapely.ops import transform as shapely_transform
from shapely.validation import explain_validity

SOURCE_EPSG = 2261
ANALYSIS_EPSG = 6535

SQUARE_FEET_PER_ACRE = Decimal("43560")
ACRE_PRECISION = Decimal("0.000001")

TRANSFORMER = Transformer.from_crs(
    SOURCE_EPSG,
    ANALYSIS_EPSG,
    always_xy=True,
)


class ParcelTransformError(ValueError):
    """Raised when a source parcel cannot be transformed safely."""


def _normalize_ring(raw_ring: object) -> list[tuple[float, float]]:
    """Validate and close one ArcGIS polygon ring."""
    if not isinstance(raw_ring, list):
        raise ParcelTransformError("Polygon ring is not a list")

    coordinates: list[tuple[float, float]] = []

    for position in raw_ring:
        if not isinstance(position, list) or len(position) < 2:
            raise ParcelTransformError("Polygon ring contains an invalid coordinate")

        try:
            x_coordinate = float(position[0])
            y_coordinate = float(position[1])
        except (TypeError, ValueError) as error:
            raise ParcelTransformError(
                "Polygon ring contains a nonnumeric coordinate"
            ) from error

        coordinates.append((x_coordinate, y_coordinate))

    if len(coordinates) < 3:
        raise ParcelTransformError("Polygon ring has fewer than three coordinates")

    # Polygon rings must finish at the same coordinate where they began.
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    if len(coordinates) < 4:
        raise ParcelTransformError("Closed polygon ring has fewer than four positions")

    return coordinates


def esri_rings_to_multipolygon(rings: list[Any]) -> MultiPolygon:
    """
    Convert ArcGIS polygon rings into a Shapely MultiPolygon.

    Under the Esri convention, clockwise rings are exterior shells
    and counterclockwise rings are interior holes.
    """
    if not rings:
        raise ParcelTransformError("Parcel geometry contains no rings")

    shells: list[list[tuple[float, float]]] = []
    holes: list[list[tuple[float, float]]] = []

    for raw_ring in rings:
        coordinates = _normalize_ring(raw_ring)
        linear_ring = LinearRing(coordinates)

        if linear_ring.is_ccw:
            holes.append(coordinates)
        else:
            shells.append(coordinates)

    if not shells:
        raise ParcelTransformError("Parcel geometry contains no exterior ring")

    polygons: list[Polygon] = []
    unassigned_holes = holes.copy()

    for shell in shells:
        shell_polygon = Polygon(shell)
        contained_holes: list[list[tuple[float, float]]] = []

        for hole in unassigned_holes:
            hole_polygon = Polygon(hole)
            interior_point = hole_polygon.representative_point()

            if shell_polygon.contains(interior_point):
                contained_holes.append(hole)

        unassigned_holes = [
            hole for hole in unassigned_holes if hole not in contained_holes
        ]

        polygons.append(
            Polygon(
                shell=shell,
                holes=contained_holes,
            )
        )

    if unassigned_holes:
        raise ParcelTransformError("One or more holes have no containing exterior ring")

    geometry = MultiPolygon(polygons)

    if geometry.is_empty:
        raise ParcelTransformError("Source parcel geometry is empty")

    if not geometry.is_valid:
        raise ParcelTransformError(
            f"Source parcel geometry is invalid: {explain_validity(geometry)}"
        )

    return geometry


def transform_parcel_geometry(
    feature: dict[str, Any],
) -> tuple[MultiPolygon, Decimal]:
    """
    Convert one ArcGIS parcel geometry to EPSG:6535.

    Returns the projected MultiPolygon and calculated gross acreage.
    """
    raw_geometry = feature.get("geometry")

    if not isinstance(raw_geometry, dict):
        raise ParcelTransformError("Parcel feature has no geometry object")

    rings = raw_geometry.get("rings")

    if not isinstance(rings, list):
        raise ParcelTransformError("Parcel geometry has no rings collection")

    source_geometry = esri_rings_to_multipolygon(rings)

    projected_geometry = shapely_transform(
        TRANSFORMER.transform,
        source_geometry,
    )

    if not isinstance(projected_geometry, MultiPolygon):
        raise ParcelTransformError("Transformed geometry is not a MultiPolygon")

    if projected_geometry.is_empty:
        raise ParcelTransformError("Transformed parcel geometry is empty")

    if not projected_geometry.is_valid:
        raise ParcelTransformError(
            "Transformed parcel geometry is invalid: "
            f"{explain_validity(projected_geometry)}"
        )

    # EPSG:6535 uses feet, so the calculated area is in square feet.
    gross_acres = (
        Decimal(str(projected_geometry.area)) / SQUARE_FEET_PER_ACRE
    ).quantize(ACRE_PRECISION)

    if gross_acres <= 0:
        raise ParcelTransformError("Calculated gross acreage is not positive")

    return projected_geometry, gross_acres
