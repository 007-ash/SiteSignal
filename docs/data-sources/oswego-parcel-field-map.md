# Oswego Parcel Field Mapping

## Source layer

- Layer: `parcelsActive`
- Geometry type: polygon
- Source CRS: EPSG:2261
- Maximum records per request: 2,000
- Observed record count: 59,510

## Normalized field mapping

| Source field | SiteSignal field | Purpose | Treatment |
|---|---|---|---|
| `GlobalID` | `source_global_id` | Publisher-managed feature identifier | Preserve and use as the source-feature uniqueness key |
| `rpsjoin` | `source_parcel_id` | County parcel identifier | Preserve, but allow duplicate values |
| `OBJECTID` | `source_object_id` | ArcGIS extraction and debugging identifier | Do not use as a permanent business identifier |
| `PRINT_KEY` | `print_key` | Human-readable tax-map identifier | Preserve for display |
| `SWIS` | `swis_code` | Assessing-jurisdiction code | Preserve as text |
| `MUNI` | `municipality` | Municipality name | Required for the bounded V1 extraction |
| `TAX_STATUS` | `tax_status_date` | Taxable-status date | Parse into a date |
| `ACRES` | `source_acres` | Publisher-provided assessment acreage | Preserve only for quality comparison |
| `PRP_CLS_CODE` | `property_class_code` | Current property-class code | Preserve |
| `PROP_CLASS` | `property_class` | Property-class description | Preserve |
| ArcGIS polygon | `geometry` | Parcel boundary | Reproject from EPSG:2261 to EPSG:6535 |
| Calculated from geometry | `gross_acres` | SiteSignal analysis acreage | Calculate after reprojection and use for spatial analysis |

## Parcel identity strategy

`GlobalID` is SiteSignal's source-feature uniqueness key. The inspected layer
contains 59,510 records and 59,510 distinct, non-null `GlobalID` values.

`rpsjoin` is preserved as the county parcel identifier but is not unique. The
layer contains 59,488 distinct `rpsjoin` values across 59,510 records, including
18 duplicated identifier groups.

Multiple source features may therefore share one `rpsjoin`.

`OBJECTID` is retained only for extraction, pagination, and debugging. It is
not treated as a permanent parcel identifier because ArcGIS object IDs may
change if the service is republished.

## Fields intentionally excluded

SiteSignal does not ingest owner names, mailing addresses, escrow information,
bank information, deed information, or other personal fields that are
unnecessary for parcel screening.

Examples include:

- `OWNER1`
- `OWNER2`
- `MAIL_ADDR`
- `MAIL_CITY`
- `MAIL_STATE`
- `MAIL_ZIP`
- `ZIP_4`
- `BANK_CODE`
- `BANK_NAME`
- `DEED_BOOK`
- `DEED_PAGE`

## Observed data-quality findings

- Total records: 59,510
- Distinct non-null `GlobalID` values: 59,510
- Missing `GlobalID` values: 0
- Distinct `rpsjoin` values: 59,488
- Missing `rpsjoin` values: 0
- Repeated `rpsjoin` groups: 18
- Records missing both municipality and taxable-status date: 29
- Records missing assessment acreage: 37
- Records with nonpositive assessment acreage: 21,711
- Records with a March 1, 2025 taxable-status date: 59,481

The repeated `rpsjoin` records have distinct `GlobalID` values but matching
business attributes in the inspected fields. SiteSignal preserves them during
extraction because geometry has not yet been compared closely enough to prove
that the features are redundant.

Because many `ACRES` values are missing, zero, or negative, SiteSignal does not
use the source acreage as the authoritative analysis value. It calculates
`gross_acres` from geometry after reprojection into EPSG:6535.

## Open decisions

- Compare repeated-identifier geometries.
- Lock the exact V1 municipality or spatial boundary.
- Define geometry repair-versus-rejection rules.
- Define acceptable differences between `source_acres` and calculated
  `gross_acres`.
  