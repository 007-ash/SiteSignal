# Oswego Parcel Ingestion Rules

## Extraction boundary

The exact V1 municipality or geographic subset remains unresolved until parcel
counts are compared with NWI wetland and FEMA regulatory-floodway coverage.

The subset must be reproducible from source attributes or a documented spatial
boundary. It must not depend on manually selecting parcels in a map.

## Identity and idempotency

Insert or update source features using `GlobalID`.

A repeated ingestion of the same source snapshot must update or leave the
existing feature unchanged rather than create another copy.

Do not use `OBJECTID` as the permanent identity key.

## Required source fields

A record must contain:

- `GlobalID`
- geometry
- `MUNI`
- `TAX_STATUS`

The loader must validate required values before inserting a parcel into the
accepted parcel table.

## Duplicate handling

Do not deduplicate records using `rpsjoin`.

Multiple source features may share the same county parcel identifier. Preserve
those records until geometry analysis proves they are redundant.

Distinct `GlobalID` values represent distinct source features, even when their
business attributes appear identical.

## Acreage policy

Do not reject a parcel merely because `ACRES` is missing, zero, or negative.

Preserve `ACRES` as `source_acres` for quality-assurance comparisons.

Calculate authoritative `gross_acres` from normalized geometry after
reprojection into EPSG:6535.

## Privacy boundary

Request and ingest only approved fields needed for parcel screening.

Do not ingest:

- owner names
- mailing addresses
- bank or escrow information
- deed information
- other unnecessary personal information

## Rejection and quarantine policy

Quarantine records that are missing required attributes rather than silently
dropping them.

The current source contains 29 records missing both `MUNI` and `TAX_STATUS`.
Those records must not enter the accepted V1 parcel set.

A quarantined record should retain enough technical information to explain:

- which source feature failed
- which validation rule failed
- which load run encountered the failure

## Pagination

The ArcGIS service limits responses to 2,000 records.

The extraction process must paginate deterministically until all records in the
selected V1 boundary have been retrieved.

Pagination should use a stable ordering or ArcGIS object-ID workflow so records
are not skipped or loaded twice.

## Open geometry decisions

Geometry repair-versus-rejection remains unresolved until actual source
geometries are validated.

Before implementation is considered complete, the project must define:

- how invalid polygons are detected
- which invalid geometries may be repaired
- which geometries must be rejected
- how geometry failures are recorded
- how repeated `rpsjoin` geometries are compared
