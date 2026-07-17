# Analysis CRS

Every spatial calculation in SiteSignal uses one analysis coordinate reference system:

```
EPSG:6535
NAD83(2011) / New York Central (ftUS)
```

SiteSignal uses EPSG:6535 for three reasons. Its area of use explicitly includes Oswego County. It is a projected coordinate system, so coordinates are represented on a Cartesian plane suitable for local spatial operations.
Its US survey foot units support straightforward distance and area calculations.

## Rules

- Preserve each dataset's original CRS in `dataset_manifest.source_crs`. I always know what a layer arrived as.
- Never assume an unknown CRS. If I can't identify a dataset's CRS, the dataset gets rejected. Assigning an assumed CRS can silently place geometries in the wrong location.
- Reproject every spatial layer to EPSG:6535 before any intersection, subtraction, distance, or area calculation.
- Store SiteSignal analysis geometries in EPSG:6535.
- Calculate acres from square US survey feet:

```
`acres = square_feet / 43,560`
```

- Do not use Web Mercator for authoritative area calculations. It distorts area badly at these latitudes and exists for map tiles, not measurement.
- Output APIs may transform geometry to EPSG:4326 later for web display. That's fine. But calculations happen in EPSG:6535, always.

## Why

PostGIS can compare geometries meaningfully only when they use the same coordinate reference system. An intersection between layers in incompatible coordinate systems may return a result, but that result is spatially invalid.

SiteSignal therefore validates every source CRS and reprojects every spatial layer into EPSG:6535 before performing intersections, subtractions, distance calculations, or area calculations. Geometry may be transformed to EPSG:4326 only when preparing output for web display.

Reference: [NAD83(2011) / New York Central (ftUS) — EPSG:6535](https://epsg.io/6535)
