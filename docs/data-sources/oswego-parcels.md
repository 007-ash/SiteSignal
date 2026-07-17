# Oswego County Active Tax Parcels

## Publisher

Oswego County GIS / Department of Real Property Tax Services

## Official dataset identity

- Dataset: Oswego County Active Tax Parcels
- ArcGIS item ID: `b15088eeef32423b890e4e50b03775d6`
- ArcGIS layer: `parcelsActive`
- Discovery source: NYS GIS Clearinghouse

## Current source vintage

The inspected source contains 59,481 parcel records with a `TAX_STATUS` value
of March 1, 2025. Twenty-nine records have no taxable-status value.

The dataset manifest records this observed source vintage together with the
acquisition timestamp, source URL, filename, checksum, source CRS, and record
count.

## Acquisition policy

- Download only from the official county or NYS-hosted source.
- The NYS GIS Clearinghouse is the discovery source. The manifest records the
  actual ArcGIS download endpoint.
- An acquisition is not complete until it can be reproduced through a
  documented, scripted process rather than an undocumented browser workflow.
- The ArcGIS item ID identifies the official dataset. The acquisition timestamp
  and SHA-256 checksum identify the exact snapshot used by SiteSignal.
- Do not use mirrors or repackaged copies.

## Raw-file policy

- Preserve the downloaded file exactly as received.
- Never manually edit raw source data.
- Apply cleaning and corrections through visible, repeatable code.
- Do not commit raw GIS files to Git.
- Git tracks ingestion code, schema, and documentation.
- PostgreSQL stores dataset-manifest and load-run records.
- Store derived or cleaned files separately from raw files.

## Provenance fields

Every acquisition is recorded in `dataset_manifest` with:

- filename
- SHA-256 checksum
- acquisition timestamp
- source CRS
- source vintage
- source URL
- record count

A changed checksum represents a different dataset snapshot and requires a new
manifest entry. Downstream analysis results will reference the relevant
dataset manifest or load run so SiteSignal can identify which source snapshot
produced them.

## V1 extraction boundary

The exact V1 municipality or geographic subset remains unresolved until parcel
counts are compared with NWI wetland and FEMA regulatory-floodway coverage.

The final rule must be reproducible from source attributes or a documented
spatial boundary. It must not depend on manually selecting parcels in a map.

## Known limitations

- Parcel geometry is intended for planning and general-use analysis.
- It is not a legal boundary survey.
- Temporal or assessment changes may have occurred after publication.
- Geometry and attribute completeness must be validated during ingestion.

## Related documentation

See [Oswego parcel field mapping](./oswego-parcel-field-map.md) for the
normalized schema contract, excluded fields, parcel identity strategy, and
observed data-quality findings.

See [Oswego parcel ingestion rules](./oswego-parcel-ingestion-rules.md) for
identity, validation, exclusion, duplicate handling, and pagination policies.
