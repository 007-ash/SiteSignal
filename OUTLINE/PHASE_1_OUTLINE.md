# SiteSignal — Abridged Phase 1 Build Outline

## Product sentence

**SiteSignal subtracts mapped wetlands and FEMA regulatory floodway from official parcel geometry, measures the usable land that remains, and ranks the bounded parcel set deterministically.**

## Current status

- Milestone 0: complete
- Milestone 1: complete locally; pending final commit, push, and green CI
- Milestone 2: next
- Milestones 3–4: not started

The next product behavior is constraint subtraction—not more parcel-ingestion infrastructure.

---

## Phase 1 boundary

Phase 1 supports one bounded vertical slice:

- Oswego County, New York
- Municipality: New Haven
- official Oswego parcel polygons
- USFWS NWI wetland polygons
- FEMA regulatory-floodway polygons
- deterministic PostGIS analysis
- a small persisted FastAPI workflow
- deployment, documentation, and freeze

Explicitly deferred:

- other counties or municipalities
- generalized ingestion frameworks
- automatic geometry repair
- raster slope and land-cover work
- grid, substation, transmission, hosting-capacity, or NYISO scoring
- zoning and ORES analysis
- multi-parcel assemblages
- frontend or map UI
- LLM or agent workflows
- production-scale workers, storage, caching, observability, and optimization

## Delivery rules

1. Define the exit test before implementation.
2. Build only what the exit test consumes.
3. Prefer explicit bounded code over generalized architecture.
4. Reject invalid source geometry rather than building a repair system.
5. Keep detailed teaching notes outside production modules.
6. Stop when the proof passes.
7. Cut optional work before extending a timebox.

The same input, code, configuration, database state, and source versions must produce the same result.

---

# Milestone 0 — Reproducible foundation

**Status: complete**

## Goal

Prove that the API, PostGIS database, migrations, tests, and deployment-oriented configuration can support real spatial work.

## Completed

- Python 3.13
- FastAPI
- PostgreSQL 18 and PostGIS 3.6
- Docker Compose
- SQLAlchemy 2.0 and GeoAlchemy2
- Alembic and shared SQLAlchemy `Base`
- `/health` and `/ready`
- pytest, Ruff, mypy, and GitHub Actions
- Railway-oriented configuration
- first migration and PostGIS integration proof

## Exit proof

The API starts, SQLAlchemy reaches PostGIS, migrations apply, health and readiness pass, real spatial operations execute, and local validation and CI pass.

No more Milestone 0 architecture is required.

---

# Milestone 1 — Bounded parcel ingestion and provenance

**Status: complete locally; pending final commit, push, and green CI**

## Goal

Load one reproducible New Haven subset of official Oswego County parcel polygons into PostGIS with provenance, validation, reprojection, calculated acreage, visible rejection counts, and idempotent reload behavior.

Wetlands and floodway ingestion belong to Milestone 2.

## Locked dataset contract

- Dataset: Oswego County Active Tax Parcels
- ArcGIS item ID: `b15088eeef32423b890e4e50b03775d6`
- Layer: `parcelsActive`
- Query: `MUNI = 'New Haven'`
- Source count: 1,636
- Source CRS: EPSG:2261
- Analysis CRS: EPSG:6535
- Idempotency key: ArcGIS `GlobalID`
- Business parcel ID: `rpsjoin`, duplicates allowed
- Source `ACRES`: QA only
- `gross_acres`: calculated from transformed geometry
- Owner, mailing, bank, escrow, and deed fields: excluded

## Completed

- [x] Source, field-map, ingestion-rule, privacy, and CRS documentation
- [x] Countywide identity and data-quality inspection
- [x] `dataset_manifest`, `load_run`, and `parcel` models and migrations
- [x] Alembic protection for PostGIS-managed tables
- [x] unique `source_global_id` enforcement and required indexes
- [x] deterministic New Haven ArcGIS extraction
- [x] approved-field and geometry-only requests
- [x] source-count and unique-GlobalID validation
- [x] deterministic identity and full-snapshot hashes
- [x] Esri-ring conversion and EPSG:2261 → EPSG:6535 transformation
- [x] invalid-source-geometry rejection without repair
- [x] attribute normalization and calculated acreage
- [x] provenance and load-run statistics
- [x] idempotent Postgres upsert by `GlobalID`
- [x] documented local ingestion command
- [x] retrospective in `decisions.md`

## Acceptance proof

Two runs against the same snapshot each produced:

```text
rows_read=1636
rows_loaded=1635
rows_rejected=1
```

Snapshot SHA-256:

```text
e62c60fbbc1756cf4096f9de6c465ae00cd65db6db4f947fb2036306d81fe940
```

Rejected source feature:

```text
GlobalID: 55ee8287-f7f8-4d91-af9a-9ed7a7f7b183
Reason: source ring self-intersection
```

Final database state:

```text
parcel_count=1635
unique_global_ids=1635
invalid_geometries=0
wrong_srids=0
nonpositive_acres=0
```

Two successful load runs exist, and the second run created no duplicates.

## Final closeout

- [ ] Format the two reported files.
- [ ] Pass Ruff lint and format checks.
- [ ] Pass mypy, pytest, and Alembic checks.
- [ ] Confirm UTF-8 documentation.
- [ ] Review `git diff --check`, `git diff`, and `git status`.
- [ ] Commit, push, and confirm green CI.

## Hard stop

Do not add a generalized ingestion framework, rejection table, automatic repair engine, countywide expansion, bulk-loader abstraction, or performance work.

Focused loader regression tests can be added during Milestone 4 validation without reopening Milestone 1.

---

# Milestone 2 — Constraint ingestion and usable-area engine

**Status: next**

**Timebox: 6–8 focused hours**

## Goal

Load only the NWI wetland and FEMA regulatory-floodway geometry needed for the New Haven analysis area, subtract the combined constraints, and calculate usable land.

```text
parcel geometry
− union of wetlands and regulatory floodway
= usable geometry
```

## Required work

### Sources and loading

- [ ] Pin official NWI and FEMA source URLs, vintages, IDs, classifications, and CRSs.
- [ ] Define the exact bounded extraction rule.
- [ ] Retrieve only geometry needed for the New Haven parcel extent.
- [ ] Preserve source IDs and classifications.
- [ ] Record manifests and load runs.
- [ ] Transform accepted geometry to EPSG:6535.
- [ ] Reject invalid source geometry.
- [ ] Prove idempotent reloads and stable counts.

Create only the schema needed to preserve source identity, provenance, classification, geometry, and spatial indexing. Do not build a universal constraint warehouse.

### Spatial engine

For each parcel:

1. select intersecting wetland and floodway features;
2. clip them to the parcel;
3. union overlaps;
4. subtract the union from the parcel;
5. split the usable result into connected components;
6. calculate gross, per-source constrained, union-constrained, total usable, and largest contiguous acreage;
7. calculate usable percentage and contiguous share;
8. return exact reasons and diligence flags.

Core PostGIS operations:

```text
ST_IsValid
ST_Intersects
ST_Intersection
ST_UnaryUnion
ST_Difference
ST_Dump
ST_Area
```

Use `ST_MakeValid` only for a narrow documented overlay-output case, not as a general repair system.

### Required tests

- [ ] no overlap
- [ ] partial overlap
- [ ] full coverage
- [ ] overlapping constraint layers
- [ ] disconnected usable fragments
- [ ] exact threshold
- [ ] invalid input
- [ ] missing required source

## Exit test

Milestone 2 is complete when:

1. one documented command loads both bounded constraint sources;
2. reruns create no duplicates;
3. one hand-calculated synthetic parcel produces the expected spatial metrics;
4. at least one real New Haven parcel runs through the same engine;
5. provenance and load counts are visible;
6. focused tests and repository validation pass.

## Hard stop

Do not add ranking, API orchestration, more constraint sources, or deployment work.

---

# Milestone 3 — Deterministic ranking and persisted API

**Status: not started**

**Timebox: 4–6 focused hours**

## Goal

Turn the bounded usable-area calculation into a persisted screening run and deterministic API result.

## Required API

- [ ] `POST /screening-runs`
- [ ] `GET /screening-runs/{run_id}`
- [ ] `GET /parcels/{parcel_id}`
- [x] `GET /health`
- [x] `GET /ready`

## Required behavior

- [ ] accept requested MW;
- [ ] calculate required acreage from one versioned acres-per-MW assumption;
- [ ] reject unsupported geography or missing source loads;
- [ ] persist request, configuration version, and source manifest IDs;
- [ ] run the bounded usable-area engine;
- [ ] persist deterministic ordered results.

Ranking inputs:

1. eligibility;
2. largest contiguous usable acreage relative to required acreage;
3. usable percentage of gross acreage;
4. largest contiguous percentage of total usable acreage;
5. stable parcel-ID tie-breaker.

Every result exposes raw values, units, contribution, configuration version, and source versions.

Tiers:

- Investigate
- Marginal
- Avoid

These are triage categories, not permit, construction, interconnection, or investment predictions.

## Exit test

A documented request creates a persisted screening run, returns an ordered shortlist, exposes one parcel’s full spatial metrics and provenance, and produces identical ordering for identical inputs.

## Hard stop

Do not add a frontend, another geography, LLM explanation, or extra scoring datasets.

---

# Milestone 4 — Validate, deploy, document, and freeze

**Status: not started**

**Timebox: 4–6 focused hours**

## Goal

Ship a small system that can be cold-demonstrated, inspected, and defended in an interview.

## Required work

### Validation

- [ ] focused loader regression tests
- [ ] ranking and configuration-boundary tests
- [ ] PostGIS integration tests for the usable-area workflow
- [ ] one reproducible real-data screening
- [ ] deterministic rerun proof
- [ ] complete repository validation

### Deployment

- [ ] deploy FastAPI and PostGIS to Railway
- [ ] apply migrations
- [ ] load bounded parcel and constraint data
- [ ] configure health and readiness
- [ ] run the deployed screening workflow
- [ ] record useful logs and duration

### Documentation

- [ ] update README to match the implemented system
- [ ] document exact source versions and refresh commands
- [ ] add one-command startup and validation
- [ ] add one sample request and response
- [ ] add one architecture or request-flow diagram
- [ ] add deployed screenshots
- [ ] document known limitations
- [ ] rehearse architecture, ingestion, CRS, transaction, spatial, and ranking explanations

## Exit test

The deployed system accepts requested MW, persists and returns a deterministic ranked result, exposes spatial metrics and provenance, repeats the same ordering, passes validation, and can be explained clearly.

## Freeze rule

After blocking defects are resolved, freeze Phase 1. Do not add more geography, layers, scoring domains, frontend work, LLM features, generalized architecture, or speculative optimization.

The next priority is interview mastery, applications, and the next defined portfolio project.

---

# Phase 1 definition of done

A reviewer can reproduce:

```text
load 1,635 valid New Haven parcels
→ load bounded NWI and FEMA floodway geometry
→ subtract combined constraints in PostGIS
→ calculate total and largest contiguous usable acreage
→ submit requested MW
→ receive the same persisted ranking for the same inputs
→ inspect exact metrics and provenance
```

SiteSignal does not need to solve every solar-development problem. It needs to prove one distinctive backend and spatial-data workflow completely.

---

# Roadmap after the frozen release

Future possibilities—not Phase 1 commitments:

- slope, land cover, existing use, access, and infrastructure proximity
- verified zoning and NYISO context
- multi-parcel and preliminary layout analysis
- additional validated county adapters
- scheduled refreshes, object storage, caching, and change monitoring
- cited diligence summaries with human review