# SiteSignal — Phase 1 Build Outline V2

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

## Phase 1 product boundary

Phase 1 is a bounded, technically distinctive vertical slice—not a statewide development platform.

A user submits requested MW for a supported Oswego County dataset. SiteSignal:

1. loads real parcel and constraint geometry into PostGIS;
2. subtracts configured constraints;
3. calculates gross, constrained, total usable, and largest contiguous usable acreage;
4. determines whether the parcel can satisfy the configured land requirement;
5. ranks the bounded parcel set using transparent deterministic metrics;
6. persists the run, ordered results, configuration version, and source provenance;
7. exposes the result through FastAPI.

The same request against the same database, configuration, code, and source versions must produce the same ordered result.

## Deferred from Phase 1

- frontend or map interface;
- statewide or county-wide production ingestion;
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
- [ ] Pin compatible PostgreSQL and PostGIS versions.
- [ ] Create Docker Compose services for the API and PostGIS.
- [ ] Create the FastAPI application with a focused package structure.
- [ ] Configure SQLAlchemy 2.0 and GeoAlchemy2.
- [ ] Add Alembic and create the first migration.
- [ ] Add `/health` and `/ready`.
- [ ] Add pytest and a PostGIS integration-test fixture.
- [ ] Add minimal Ruff, mypy, and test commands.
- [ ] Add CI that runs the available validation.
- [ ] Create `dataset_manifest` and `load_run` tables.
- [ ] Write `docs/crs-policy.md`.
- [ ] Perform an early Railway/PostGIS deployment proof.

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
9. repeat the proof in CI and the target deployment environment.

---

## Milestone 1 — Bounded data ingestion and provenance

### Goal

Load a reproducible subset of official Oswego County parcels and two real vector constraint layers through idempotent, versioned adapters.

### Initial data scope

- [ ] reproducible subset of official Oswego County parcel polygons;
- [ ] USFWS National Wetlands Inventory polygons;
- [ ] FEMA National Flood Hazard Layer regulatory floodway polygons.

The exact parcel source snapshot, selection rule, geographic extent, and constraint-source vintages must be pinned before implementation. The subset must be produced by a documented query defined before scoring—not by hand-picking parcels based on attractive results.

### County preflight

- [ ] Extract an Oswego parcel sample and measure null IDs, duplicate IDs, geometry types, invalid-geometry rate, source CRS, and acreage-field completeness.
- [ ] Clip NWI data to the candidate extent and confirm a nonzero wetland-polygon count.
- [ ] Inspect the Oswego County FEMA NFHL package and confirm a nonzero regulatory-floodway count in the candidate extent.
- [ ] Choose a deterministic subset rule using source fields and an official geographic boundary, with any acreage threshold documented before scoring.
- [ ] Rerun the subset query and confirm it produces the same ordered source parcel IDs from the same source snapshot.

### Tasks

- [ ] Confirm official availability, license, and source metadata.
- [ ] Record source URL, source date, retrieval time, checksum, license, and original CRS.
- [ ] Validate required fields and source geometry types.
- [ ] Map source fields into normalized parcel and constraint schemas.
- [ ] Preserve source record IDs and classifications.
- [ ] Transform geometry according to `docs/crs-policy.md`.
- [ ] Repair or reject invalid geometry under a documented rule.
- [ ] Calculate parcel gross acreage in the analysis CRS.
- [ ] Create GiST spatial indexes.
- [ ] Make every load safe to rerun without duplicate records.
- [ ] Record read, loaded, updated, duplicate, repaired, and rejected counts.
- [ ] Link each normalized record set to its dataset manifest and load run.

### Exit test

- the same bounded source can be loaded twice without duplicate records;
- accepted geometry is valid and has the expected SRID;
- gross acreage matches an independently calculated fixture;
- parcel and constraint counts remain stable across reruns;
- the documented subset query reproduces the same parcel IDs from the pinned source snapshot;
- the selected extent contains nonzero NWI and regulatory-floodway geometry;
- provenance is queryable from the database.

---

## Milestone 2 — Usable-area spatial engine

### Goal

Implement the technical core: subtract real constraint geometry and measure the largest contiguous usable area.

### Core PostGIS operations

The implementation should exercise and explain real uses of:

```text
ST_Transform
ST_MakeValid
ST_Intersects
ST_Intersection
ST_UnaryUnion
ST_Difference
ST_Dump
ST_Area
```

### Tasks

- [ ] Create versioned acres-per-MW and minimum-patch configuration.
- [ ] Calculate required usable acreage from requested MW.
- [ ] Select constraints that intersect each parcel.
- [ ] Clip each source to the parcel.
- [ ] Union overlapping constraint geometry before subtraction.
- [ ] Avoid double-counting overlap between constraint sources.
- [ ] Subtract the combined constraint geometry from the parcel.
- [ ] Repair overlay output only under the documented geometry policy.
- [ ] Split multipolygon output into connected components.
- [ ] Calculate gross acres.
- [ ] Calculate per-source intersected acres.
- [ ] Calculate union-constrained acres.
- [ ] Calculate total usable acres.
- [ ] Calculate largest contiguous usable acres.
- [ ] Calculate fragmentation ratio.
- [ ] Return eligibility and an exact elimination reason.
- [ ] Return uncertainty and diligence flags separately from eligibility.

### Synthetic tests

- [ ] no overlap;
- [ ] boundary touch only;
- [ ] partial overlap;
- [ ] full coverage;
- [ ] overlapping constraints;
- [ ] hole inside a parcel;
- [ ] disconnected leftover fragments;
- [ ] multipolygon parcel;
- [ ] exact acreage threshold;
- [ ] invalid input geometry;
- [ ] missing constraint source.

### Exit test

A hand-calculated synthetic parcel produces the expected constrained acreage, total usable acreage, largest connected component, fragmentation ratio, and eligibility result within an agreed numerical tolerance.

---

## Milestone 3 — Deterministic ranking and persisted API

### Goal

Turn the spatial engine into a reproducible screening workflow and ranked API result.

### Ranking inputs

The initial ranking should remain small and reconstructable:

1. eligibility;
2. largest contiguous usable acreage relative to required acreage;
3. usable acreage as a percentage of gross acreage;
4. largest contiguous acreage as a percentage of total usable acreage;
5. stable parcel-ID tie-breaking.

Exact score bands and weights must be versioned and tested before release.

### API target

- [ ] `POST /screening-runs`
- [ ] `GET /screening-runs/{run_id}`
- [ ] `GET /screening-runs/{run_id}/parcels`
- [ ] `GET /parcels/{parcel_id}`
- [ ] `GET /health`
- [ ] `GET /ready`

### Tasks

- [ ] Validate requested MW.
- [ ] Validate the supported dataset and county.
- [ ] Verify required source loads.
- [ ] Persist requested MW, configuration version, and source versions.
- [ ] Select the bounded candidate parcel set.
- [ ] Run the usable-area engine.
- [ ] Calculate transparent ranking metrics.
- [ ] Return each raw metric with units and score contribution.
- [ ] Define simple Investigate, Marginal, and Avoid tiers.
- [ ] Add deterministic secondary sorting.
- [ ] Persist ordered parcel results.
- [ ] Persist timing and candidate counts.
- [ ] Return clear errors for unsupported input or missing source data.
- [ ] Prove that identical inputs produce identical ordering.

### Exit test

On a fresh database, one command sequence loads the bounded data, creates a screening run, retrieves an ordered shortlist, and inspects one parcel without manual SQL changes.

---

## Milestone 4 — Validate, deploy, document, and freeze

### Goal

Ship a small system that can be cold-demonstrated, inspected, and defended in an interview.

### Required tasks

- [ ] Add focused unit tests for ranking and configuration boundaries.
- [ ] Add PostGIS integration tests for the spatial workflow.
- [ ] Run one reproducible bounded real-data screening.
- [ ] Deploy FastAPI and PostGIS to Railway.
- [ ] Run Alembic migrations during deployment.
- [ ] Load the bounded demo dataset.
- [ ] Configure health and readiness checks.
- [ ] Add structured logs and screening duration.
- [ ] Document exact source versions and refresh steps.
- [ ] Add one-command local startup.
- [ ] Add one-command test execution.
- [ ] Add a sample request and response to the README.
- [ ] Add architecture and request-flow diagrams.
- [ ] Add screenshots of the deployed API and result.
- [ ] Document known limitations.
- [ ] Rehearse the architecture, request flow, CRS policy, and spatial-query choices.
- [ ] Freeze Phase 1 after blocking defects are resolved.

### Optional only after the deterministic core is deployed

- [ ] Generate a bounded diligence memo from an immutable result.
- [ ] Require structured output.
- [ ] Verify every number against the input result.
- [ ] Preserve deterministic results when the model fails.
- [ ] Prohibit permit, legal, engineering, or investment conclusions.

### Exit test

From the deployed system:

1. submit requested MW;
2. receive a screening-run ID;
3. retrieve a ranked shortlist;
4. inspect gross, constrained, usable, and largest contiguous acreage;
5. inspect ranking inputs, score, tier, flags, and provenance;
6. repeat the run and receive the same ordering.

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
