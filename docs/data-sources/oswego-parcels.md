# Oswego County Active Tax Parcels

## Publisher

Oswego County GIS / Department of Real Property Tax Services

## Official dataset identity

- Dataset: Oswego County Active Tax Parcels
- ArcGIS item ID: `b15088eeef32423b890e4e50b03775d6`
- Discovery source: NYS GIS Clearinghouse

## Current source vintage

To be confirmed from the downloaded dataset metadata.

## Acquisition policy

- Download only from the official county or NYS-hosted source. The NYS GIS
  Clearinghouse is the discovery source; the manifest records the actual
  download endpoint associated with the ArcGIS item ID above.
- An acquisition is not considered complete until the download can be
  reproduced through a documented, scripted step rather than an undocumented
  browser workflow.
- The ArcGIS item ID identifies the official dataset. The acquisition
  timestamp and SHA-256 checksum identify the exact snapshot used by
  SiteSignal.
- Do not use mirrors or repackaged copies.

## Raw-file policy

- Do not commit raw GIS files to Git. The raw data directory is gitignored.
- Git tracks the ingestion code, schema, and documentation.
- PostgreSQL stores each dataset-manifest record.

## Provenance fields

Every acquisition is recorded in `dataset_manifest`:

- filename
- SHA-256 checksum
- acquisition timestamp
- source CRS
- vintage
- source URL
- record count

A changed checksum represents a different dataset snapshot and requires a newmanifest entry. Each downstream analysis result will reference the relevant dataset manifest or load run so SiteSignal can identify exactly which source
snapshot produced it.

## V1 extraction boundary

The exact deterministic parcel subset will be locked after inspecting the published schema. The rule must be reproducible from source fields and must not depend on manually selecting parcels in a map.

That is deliberately unresolved for one more commit. I haven't inspected the real fields yet, and I'd rather leave the boundary open than invent a subset rule against a schema I'm imagining. Whatever the rule ends up being, anyone with the same raw file must arrive at the same parcel set.

## Known limitations

- Parcel geometry is intended for planning and general-use analysis.
- It is not a legal boundary survey.
- Temporal or assessment changes may have occurred after publication.
- Geometry and attribute completeness must be validated during ingestion.
