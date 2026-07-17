# SiteSignal — Abridged Phase 1 Build Outline V3

## Working protocol

For each implementation increment:

1. State the intended behavior in plain language.
2. Write the first code draft from memory where practical.
3. Use official documentation before interpreting source fields, classifications, CRS, regulatory meaning, or deployment behavior.
4. Review the change PR-style.
5. Explain the request or data flow aloud in sixty seconds.
6. Record material tradeoffs in `decisions.md`.
7. Commit one coherent, validated increment.

The browser-closed drill applies to code recall and architectural explanation. It does not apply to source metadata, compatibility research, or regulatory interpretation.

## Abridged delivery rule

Phase 1 must remain a small, complete vertical slice.

- Build only what is required by the current milestone exit test.
- Prefer explicit loaders for the three supported datasets over a generalized ingestion framework.
- Support one municipality-sized subset inside Oswego County.
- Reject and record invalid source geometry instead of building a general repair engine.
- Defer expansion until the bounded workflow is deployed and documented.
- Do not add new milestone requirements unless they are necessary to pass the current exit test.

## Phase 1 product boundary

Phase 1 is a bounded, technically distinctive vertical slice—not a statewide development platform.

A user submits requested MW for one supported Oswego County municipality dataset. SiteSignal:

1. loads real parcel, wetland, and regulatory-floodway geometry into PostGIS;
2. subtracts configured constraints;
3. calculates gross, constrained, total usable, and largest contiguous usable acreage;
4. determines whether each parcel can satisfy the configured land requirement;
5. ranks the bounded parcel set using transparent deterministic metrics;
6. persists the run, ordered results, configuration version, and source provenance;
7. exposes the result through FastAPI.

The same request against the same database, configuration, code, and source versions must produce the same ordered result.

## Deferred from Phase 1

- frontend or map interface;
- countywide or statewide production ingestion;
- reusable multi-county adapter framework;
- automatic geometry-repair engine;
- raster-derived slope processing;
- transmission, substation, hosting-capacity, or NYISO scoring;
- five-factor suitability modeling;
- municipal zoning conclusions;
- ORES regression suite;
- multi-parcel assemblage optimization;
- Claude Agent SDK or permitting agent;
- worker queues, object storage, and production-scale ETL;
- advanced observability and performance optimization.

---

## Milestone 0 — Reproducible foundation

### Goal

Prove that the API, PostGIS database, migrations, tests, and target deployment can execute real spatial operations before product logic begins.

### Tasks

- [x] Initialize the repository.
- [x] Add `README.md`, `decisions.md`, and this outline.
- [x] Add `.gitignore`, `.env.example`, and `CONTRIBUTING.md`.
- [x] Pin the Python development version and compatible runtime range.
- [x] Pin compatible PostgreSQL and PostGIS versions.
- [x] Create Docker Compose services for the API and PostGIS.
- [x] Create the FastAPI application with a focused package structure.
- [x] Configure SQLAlchemy 2.0 and GeoAlchemy2.
- [x] Add Alembic and create the first migration.
- [x] Add `/health` and `/ready`.
- [x] Add pytest and a PostGIS integration-test fixture.
- [x] Add minimal Ruff, mypy, and test commands.
- [x] Add CI that runs the available validation.
- [x] Complete and merge the Milestone 0 branch.

### Initial package shape

Create packages only when they have a real responsibility.

```text
app/
├── main.py
├── api/
├── db/
├── models/
├── repositories/
├── schemas/
└── services/

tests/
```

Add a separate `domain/` package when pure spatial or ranking logic exists.

### Exit test

From a clean checkout:

1. start the API and database;
2. run migrations;
3. connect through SQLAlchemy;
4. execute `SELECT PostGIS_Full_Version();`;
5. insert two test polygons;
6. assert `ST_Intersects`;
7. calculate a known area in a projected CRS;
8. pass `/health`, `/ready`, and the PostGIS integration test;
9. repeat the proof in CI.

**Status: complete.**

---

## Milestone 1 — Bounded parcel ingestion and provenance

### Goal

Load one reproducible municipality-sized subset of official Oswego County parcel polygons into PostGIS with provenance, validation, reprojection, calculated acreage, and idempotent reload behavior.

Milestone 1 does **not** ingest wetlands or floodway geometry. Those constraint layers move to Milestone 2, where they are loaded directly for the usable-area calculation that consumes them.

### Locked source decisions

- [x] County: Oswego County, New York.
- [x] Official dataset: Oswego County Active Tax Parcels.
- [x] ArcGIS item ID: `b15088eeef32423b890e4e50b03775d6`.
- [x] Layer: `parcelsActive`.
- [x] Source geometry type: polygon.
- [x] Source CRS: EPSG:2261.
- [x] Analysis CRS: EPSG:6535.
- [x] Source-feature uniqueness key: `GlobalID`.
- [x] County business identifier: `rpsjoin`, duplicates allowed.
- [x] Source `ACRES` is QA-only; `gross_acres` is calculated from normalized geometry.
- [x] Owner, mailing, bank, escrow, and deed fields are excluded.

### Completed preflight and contracts

- [x] Inspect the official service and published schema.
- [x] Measure total rows, missing identifiers, duplicate identifiers, source CRS, municipality counts, taxable-status values, and acreage completeness.
- [x] Confirm 59,510 distinct, non-null `GlobalID` values across 59,510 records.
- [x] Confirm `rpsjoin` is not unique and document repeated identifier groups.
- [x] Document the parcel source and acquisition policy.
- [x] Document the source-to-SiteSignal field map.
- [x] Document privacy exclusions and ingestion rules.
- [x] Create `dataset_manifest` and `load_run` models and migration.
- [x] Write `docs/crs-policy.md`.
- [x] Protect Alembic autogeneration from PostGIS-owned tables.

### Remaining tasks

- [ ] Lock one municipality-sized extraction boundary.
  - Candidate: New Haven.
  - Confirm that it has nonzero NWI and FEMA coverage before locking it.
  - If it fails that check, choose another municipality and document the reason.
- [ ] Record the exact ArcGIS query used for the subset.
- [ ] Rerun the query and confirm the same ordered `GlobalID` values are returned.
- [ ] Create the normalized `Parcel` model and Alembic migration.
- [ ] Add a unique constraint on `source_global_id`.
- [ ] Add a GiST index on parcel geometry.
- [ ] Link each parcel to its dataset manifest or load run.
- [ ] Build one scripted ArcGIS extractor for the selected municipality.
- [ ] Request only the approved fields and geometry.
- [ ] Handle the service's 2,000-record response limit.
- [ ] Transform EPSG:2261 geometry to EPSG:6535.
- [ ] Validate required fields and polygon geometry.
- [ ] Reject or quarantine missing required values and invalid geometry.
- [ ] Do not build an automatic geometry-repair engine.
- [ ] Calculate `gross_acres` from geometry in EPSG:6535.
- [ ] Insert or update records using `GlobalID`.
- [ ] Record read, accepted, rejected, and final-status counts.
- [ ] Make the load safe to rerun without duplicate parcel records.
- [ ] Add focused transformation, validation, acreage, idempotency, SRID, and row-count tests.
- [ ] Add one documented local ingestion command.

### Exit test

From a migrated local database:

1. run one documented command;
2. create a dataset-manifest and load-run record;
3. retrieve the deterministic municipality subset;
4. load accepted parcels into PostGIS;
5. record rejected parcels or counts visibly;
6. confirm every accepted geometry is valid and uses EPSG:6535;
7. confirm calculated gross acreage against a known fixture;
8. rerun the same command;
9. confirm the final parcel count and unique `GlobalID` set remain unchanged;
10. pass Ruff, mypy, pytest, and Alembic checks.

---

## Milestone 2 — Constraint ingestion and usable-area engine

### Goal

Load only the USFWS wetlands and FEMA regulatory-floodway features needed for the selected municipality, subtract them from parcel geometry, and calculate total and contiguous usable acreage.

### Initial constraint scope

- [ ] USFWS National Wetlands Inventory polygons intersecting the selected municipality.
- [ ] FEMA National Flood Hazard Layer regulatory-floodway polygons intersecting the selected municipality.

No countywide or nationwide constraint warehouse is required.

### Constraint preflight

- [ ] Pin the official NWI source URL, source vintage, license, and original CRS.
- [ ] Pin the official FEMA NFHL source URL, source vintage, license, and original CRS.
- [ ] Confirm a nonzero NWI polygon count in the selected municipality.
- [ ] Confirm a nonzero FEMA regulatory-floodway polygon count in the selected municipality.
- [ ] Document the exact extraction or clipping rules.
- [ ] Record manifests and load runs for both constraint sources.

### Minimal constraint ingestion

- [ ] Create only the constraint schema required by the spatial engine.
- [ ] Preserve source record IDs and source classifications.
- [ ] Transform accepted geometry into EPSG:6535.
- [ ] Add GiST spatial indexes.
- [ ] Reject and record invalid source geometry.
- [ ] Make each constraint load safe to rerun.
- [ ] Confirm stable feature counts across reruns.

### Core spatial operations

The implementation should exercise and explain focused uses of:

```text
ST_Transform
ST_IsValid
ST_Intersects
ST_Intersection
ST_UnaryUnion
ST_Difference
ST_Dump
ST_Area
```

Use `ST_MakeValid` only if a narrow, documented overlay-output rule becomes necessary. Do not build a general repair framework.

### Spatial-engine tasks

- [ ] Create versioned acres-per-MW and minimum-patch configuration.
- [ ] Calculate required usable acreage from requested MW.
- [ ] Select constraints that intersect each parcel.
- [ ] Clip each constraint source to the parcel.
- [ ] Union overlapping constraint geometry before subtraction.
- [ ] Avoid double-counting overlap between wetlands and floodway.
- [ ] Subtract the combined constraint geometry from the parcel.
- [ ] Split multipolygon output into connected components.
- [ ] Calculate gross acres.
- [ ] Calculate per-source intersected acres.
- [ ] Calculate union-constrained acres.
- [ ] Calculate total usable acres.
- [ ] Calculate largest contiguous usable acres.
- [ ] Calculate fragmentation ratio.
- [ ] Return eligibility and an exact elimination reason.
- [ ] Return uncertainty and diligence flags separately from eligibility.

### Focused synthetic tests

- [ ] no overlap;
- [ ] partial overlap;
- [ ] full coverage;
- [ ] overlapping constraints;
- [ ] disconnected leftover fragments;
- [ ] exact acreage threshold;
- [ ] invalid input geometry;
- [ ] missing constraint source.

### Exit test

A hand-calculated synthetic parcel produces the expected constrained acreage, total usable acreage, largest connected component, fragmentation ratio, and eligibility result within an agreed numerical tolerance.

At least one real parcel in the selected municipality runs through the same engine using real NWI and FEMA geometry.

---

## Milestone 3 — Deterministic ranking and persisted API

### Goal

Turn the bounded spatial engine into a reproducible screening workflow and ranked API result.

### Ranking inputs

Keep the initial ranking small and reconstructable:

1. eligibility;
2. largest contiguous usable acreage relative to required acreage;
3. usable acreage as a percentage of gross acreage;
4. largest contiguous acreage as a percentage of total usable acreage;
5. stable parcel-ID tie-breaking.

Exact score bands and weights must be versioned and tested before release.

### API target

Required:

- [ ] `POST /screening-runs`
- [ ] `GET /screening-runs/{run_id}`
- [ ] `GET /parcels/{parcel_id}`
- [ ] `GET /health`
- [ ] `GET /ready`

Optional only if the required endpoints are complete:

- [ ] `GET /screening-runs/{run_id}/parcels`

The screening-run response may contain the ordered shortlist directly; do not create extra endpoints solely for architectural symmetry.

### Tasks

- [ ] Validate requested MW.
- [ ] Validate the one supported dataset and municipality.
- [ ] Verify required parcel and constraint loads.
- [ ] Persist requested MW, configuration version, and source versions.
- [ ] Select the bounded candidate parcel set.
- [ ] Run the usable-area engine.
- [ ] Calculate transparent ranking metrics.
- [ ] Return each raw metric with units and score contribution.
- [ ] Define simple Investigate, Marginal, and Avoid tiers.
- [ ] Add deterministic secondary sorting.
- [ ] Persist ordered parcel results.
- [ ] Return clear errors for unsupported input or missing source data.
- [ ] Prove that identical inputs produce identical ordering.

### Exit test

On a fresh database, one documented command sequence loads the bounded data, creates a screening run, retrieves an ordered shortlist, and inspects one parcel without manual SQL changes.

---

## Milestone 4 — Validate, deploy, document, and freeze

### Goal

Ship a small system that can be cold-demonstrated, inspected, and defended in an interview.

### Required tasks

- [ ] Add focused unit tests for ranking and configuration boundaries.
- [ ] Add PostGIS integration tests for the bounded spatial workflow.
- [ ] Run one reproducible real-data screening.
- [ ] Deploy FastAPI and PostGIS to Railway.
- [ ] Run Alembic migrations during deployment.
- [ ] Load the bounded demo data.
- [ ] Configure health and readiness checks.
- [ ] Add useful structured logs and screening duration.
- [ ] Document exact source versions and refresh commands.
- [ ] Add one-command local startup.
- [ ] Add one-command test execution.
- [ ] Add a sample request and response to the README.
- [ ] Add one architecture/request-flow diagram.
- [ ] Add screenshots of the deployed API and result.
- [ ] Document known limitations.
- [ ] Rehearse the architecture, request flow, CRS policy, ingestion flow, and spatial-query choices.
- [ ] Freeze Phase 1 after blocking defects are resolved.

### Explicitly not required before freezing Phase 1

- generalized ingestion framework;
- additional counties or municipalities;
- frontend;
- agent-generated memo;
- advanced monitoring;
- performance optimization beyond obvious blocking defects.

### Exit test

From the deployed system:

1. submit requested MW;
2. receive a screening-run ID and ranked result;
3. inspect gross, constrained, usable, and largest contiguous acreage;
4. inspect ranking inputs, score, tier, flags, and provenance;
5. repeat the run and receive the same ordering.

---

# Roadmap after the bounded V1

## Next spatial depth

- add one infrastructure-proximity factor only after a defensible source is pinned;
- add slope from a pinned elevation source;
- add land-cover and existing-use inputs;
- expand the validated parcel set.

## Broader product depth

- verified municipal ordinance and zoning research;
- NYISO and point-of-interconnection context;
- multi-parcel assemblage analysis;
- project-layout and access constraints;
- agentic diligence research with citations and human approval.

## Scale

- validated county adapters;
- batch jobs and workers;
- object storage and tiled source processing;
- precomputed overlays and caching;
- portfolio reruns, monitoring, and ranking-drift detection.
