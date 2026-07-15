# SiteSignal — Phase 1 Build Outline V1

## Working protocol

For each implementation step:

1. State the intended behavior in plain language.
2. Write the first code draft from memory where practical.
3. Use official source documentation before interpreting fields, classifications, CRS, regulatory meaning, or legal status.
4. Review the change PR-style.
5. Explain it aloud in sixty seconds.
6. Record material tradeoffs in `decisions.md`.
7. Commit a coherent increment.

The browser-closed drill applies to code recall and architectural explanation. It does not apply to source metadata or regulatory interpretation.

## Definition of done for Phase 1

A user can submit requested MW and a supported county, receive a reproducible ranked parcel shortlist, inspect constraint subtraction and score components, see source versions and uncertainty flags, and generate a bounded diligence memo.

The same request against the same database, configuration, and source versions produces the same ordered result.

---

## Milestone 0 — Reproducible environment and skeleton

### Goal

Prove that the application, database, migrations, tests, and target deployment can execute real spatial operations before domain logic begins.

### Tasks

- [ ] Initialize the repository.
- [ ] Add `README.md`, `decisions.md`, and this outline.
- [ ] Add `.gitignore`, `.env.example`, and a minimal contribution/workflow note.
- [ ] Pin the Python version.
- [ ] Pin compatible PostgreSQL and PostGIS versions.
- [ ] Create Docker Compose services for the API and PostGIS.
- [ ] Create the FastAPI application.
- [ ] Add thin router, application-service, domain, repository, model, and schema packages.
- [ ] Configure SQLAlchemy 2.0 and GeoAlchemy2.
- [ ] Add Alembic and create the first migration.
- [ ] Add `/health` and `/ready`.
- [ ] Add pytest and a PostGIS integration-test fixture.
- [ ] Add linting/type-check commands and CI.
- [ ] Create a first dataset-manifest table and load-run table.
- [ ] Write `docs/crs-policy.md` with source-metadata, storage, and analysis rules.
- [ ] Perform an early Railway/PostGIS deployment proof.

### Exit test

From a clean checkout:

1. start the services;
2. run migrations;
3. connect through SQLAlchemy;
4. execute `SELECT PostGIS_Full_Version();`;
5. insert two test polygons;
6. assert `ST_Intersects`;
7. calculate a known area in a projected CRS;
8. run the same proof in CI and the target deployment environment.


---

## Milestone 1 — Parcel ingestion

### Goal

Create the first idempotent, versioned geospatial ingestion pipeline using St. Lawrence County parcels.

### Tasks

- [ ] Confirm official St. Lawrence public polygon availability and license.
- [ ] Accept county FIPS as the loader parameter.
- [ ] Save source URL metadata, source date, retrieval time, and checksum.
- [ ] Validate required columns and source CRS.
- [ ] Map source fields into a normalized parcel schema.
- [ ] Reproject according to the CRS policy.
- [ ] Repair or reject invalid geometry under a documented rule.
- [ ] Preserve source parcel ID and county FIPS.
- [ ] Calculate gross acreage in the analysis CRS.
- [ ] Create spatial indexes.
- [ ] Make reruns idempotent.
- [ ] Record read, loaded, updated, duplicate, repaired, and rejected counts.
- [ ] Add an internal parcel-count/sample endpoint only if it helps validate ingestion; do not confuse it with the final product API.

### Exit test

- the same file can be loaded twice without duplicate parcels;
- accepted geometry is valid and has the expected SRID;
- gross acreage matches an independently calculated fixture;
- county query counts are stable;
- load-run provenance is queryable.

---

## Milestone 2 — Constraint-source adapters

### Goal

Normalize four preliminary constraint sources without yet deciding parcel eligibility.

### Sources

- [ ] USGS PAD-US;
- [ ] USFWS National Wetlands Inventory;
- [ ] FEMA NFHL floodway and 1% annual-chance floodplain as separate classes;
- [ ] USGS 3DEP elevation used to derive slope.

### Tasks

For each vector source:

- [ ] pin source version and checksum;
- [ ] preserve source IDs and classifications;
- [ ] clip to supported extent;
- [ ] normalize CRS;
- [ ] repair or reject invalid geometry;
- [ ] load idempotently;
- [ ] create spatial indexes;
- [ ] record ETL statistics and manifest metadata.

For terrain:

- [ ] pin DEM product, date, and resolution;
- [ ] derive slope with a documented method;
- [ ] select and record degrees or percent rise;
- [ ] produce a thresholded steep-slope mask only after the configuration is approved;
- [ ] checksum the derived output and link it to its source load.

### Exit test

- each source has a completed manifest and load record;
- floodway and floodplain remain distinguishable;
- synthetic known geometries intersect the expected classes;
- slope derivation is reproducible from the same DEM and parameters.

---

## Milestone 3 — Usable-area engine

### Goal

Implement the core product: subtract constrained geometry and test the largest contiguous usable area.

### Tasks

- [ ] Create versioned configuration for selected PAD-US classes.
- [ ] Create versioned configuration for slope threshold.
- [ ] Create versioned acres-per-MW and minimum-patch assumptions.
- [ ] Calculate required usable acreage from requested MW.
- [ ] Union and clip each relevant constraint to the parcel.
- [ ] Avoid double-counting overlapping constraint layers.
- [ ] Subtract configured constraints from parcel geometry.
- [ ] repair overlay output when necessary under a documented policy.
- [ ] split multipolygon results into connected components.
- [ ] calculate gross acres, per-source constrained acres, union-constrained acres, total usable acres, and largest contiguous usable acres.
- [ ] return eligibility and exact elimination reason.
- [ ] return uncertainty and diligence flags separately.

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
- [ ] missing source layer.

### Exit test

A hand-calculated synthetic parcel produces the expected constrained areas, largest contiguous component, and eligibility result within an agreed numerical tolerance.

---

## Milestone 4 — Suitability-source adapters

### Goal

Load the sources required for five transparent Phase 1 suitability factors.

### Sources

- [ ] pinned public substation data;
- [ ] pinned public transmission-line data;
- [ ] FEMA 1% annual-chance floodplain;
- [ ] USGS NLCD;
- [ ] NYS ORPTS property-class attributes.

### Tasks

- [ ] document infrastructure-layer age, license, completeness, and limitations;
- [ ] define qualifying substation and transmission classes;
- [ ] define the transmission-voltage filter;
- [ ] preserve raw classifications;
- [ ] normalize vector and raster sources;
- [ ] define floodplain exposure calculation on usable geometry;
- [ ] map NLCD classes to a versioned suitability table;
- [ ] map property classes to a versioned existing-land-use table;
- [ ] return `zoning_status = unknown` unless a verified zoning source exists.

### Exit test

For a synthetic parcel and small real sample, each raw metric can be calculated independently and traced to one source version.
---

## Milestone 5 — Deterministic scoring and ranking

### Goal

Convert raw metrics into auditable scores without hiding uncertainty.

### Five sub-scores

1. qualifying-substation distance;
2. qualifying-transmission distance;
3. floodplain exposure;
4. land-cover suitability;
5. existing land-use compatibility.

### Tasks

- [ ] define raw metric, units, direction, and missing-data behavior for each factor;
- [ ] define lower-inclusive, upper-exclusive score bands;
- [ ] return raw value and score together;
- [ ] validate that weights sum to 1.0;
- [ ] calculate the composite;
- [ ] define Investigate, Marginal, and Avoid bands;
- [ ] add deterministic secondary sorting;
- [ ] retain configuration and data versions with each result;
- [ ] create a recommended next diligence action from deterministic rules before involving the LLM.

### Tests

- [ ] every band boundary;
- [ ] every tier boundary;
- [ ] missing and stale data;
- [ ] exact composite arithmetic;
- [ ] tie-breaking;
- [ ] deterministic next-action selection.

### Exit test

A table of controlled fixtures reproduces every raw metric, score, composite, tier, and next action exactly.

---

## Milestone 6 — Screening workflow and API

### Goal

Turn the domain engine into a reproducible persisted workflow.

### API

- [ ] `POST /screening-runs`
- [ ] `GET /screening-runs/{run_id}`
- [ ] `GET /screening-runs/{run_id}/parcels`
- [ ] `GET /parcels/{parcel_id}`
- [ ] `GET /health`
- [ ] `GET /ready`

### Tasks

- [ ] validate requested MW;
- [ ] validate county support;
- [ ] verify required source loads and freshness;
- [ ] persist run configuration and data versions;
- [ ] select candidate parcels;
- [ ] apply eligibility engine;
- [ ] score survivors;
- [ ] rank results;
- [ ] persist timing and candidate counts;
- [ ] paginate shortlist results;
- [ ] return clear errors for unsupported county, missing source, and stale-data policy failures.

### Exit test

On a fresh database, one command sequence loads data, creates a screening run, retrieves a ranked shortlist, and inspects one parcel without manual SQL changes.

Repeating the run with identical inputs produces the same order.

---

## Milestone 7 — Validation and explanation

### Goal

Prove exact behavior with synthetic tests, test plausibility with public cases, and add a bounded narrative layer.

### Real-project regressions

- [ ] Rich Road Solar, Matter 22-02969;
- [ ] Cider Solar, Matter 21-01108;
- [ ] Moss Ridge Solar, Matter 24-03042;
- [ ] Shepherd's Run Solar, Matter 24-03041.

For each case:

- [ ] document exact geometry source;
- [ ] document source versions;
- [ ] identify official-record constraints relevant to SiteSignal;
- [ ] write case-specific assertions;
- [ ] avoid automatic permitted=high or withdrawn=low labels.

### Explanation layer

- [ ] define immutable `ScreeningResult`;
- [ ] send the completed result to the Claude Messages API;
- [ ] require structured output;
- [ ] include summary, strengths, constraints, flags, limitations, and next action;
- [ ] prohibit unsupported permit conclusions;
- [ ] verify all numbers against the input object;
- [ ] keep deterministic results available if the model fails;
- [ ] write schema and adversarial tests.

### Agent preparation

- [ ] whiteboard the raw agent loop;
- [ ] document why Phase 1 is not agentic;
- [ ] create the Phase 3 ordinance-research tool contract without implementing the full agent yet.

### Exit test

A fixed result yields a valid memo that preserves every score and flag, adds no unsupported factual claim, and fails safely.

---

## Milestone 8 — Deployment, observability, and demo

### Goal

Ship a small, honest system that can be cold-demonstrated and inspected.

### Tasks

- [ ] deploy FastAPI and PostGIS to Railway;
- [ ] run Alembic migrations during deployment;
- [ ] load a bounded demo dataset;
- [ ] configure health and readiness checks;
- [ ] add structured logs;
- [ ] record screening duration and stage timings;
- [ ] inspect query plans for major spatial queries;
- [ ] document source versions and refresh procedure;
- [ ] finalize README and decisions;
- [ ] add one-command local startup;
- [ ] add one-command test execution;
- [ ] expose API documentation or a minimal phone-friendly interface.

### Exit test

From a clean deployed system:

1. submit requested MW and county;
2. receive a screening-run ID;
3. retrieve a ranked shortlist;
4. inspect usable-area math and sub-scores;
5. generate a diligence memo;
6. verify the source and configuration versions;
7. repeat the run and receive the same ordering.


---

# Product roadmap after Phase 1

## Phase 2 — Grid depth and preliminary design

- hosting-capacity sources where available;
- route-to-POI analysis;
- append-only NYISO queue snapshots;
- process-regime and cluster-cohort tagging;
- basic site design and access-path constraints;
- risk archetypes;
- evidence-based next-step sequencing.

## Phase 3 — Agentic permitting research

- Claude Agent SDK;
- municipal ordinance and moratorium retrieval;
- town-minute and ORES/DPS research;
- source citation and version comparison;
- structured permitting requirements;
- human-approved development plans;
- monitored source changes.

## Phase 4 — Statewide and portfolio scale

- county support matrix and adapters;
- multi-parcel assemblages;
- batch jobs and workers;
- object storage and tiled source processing;
- precomputed overlays and caches;
- GiST/query-plan optimization;
- portfolio reruns and ranking-drift monitoring;
- operational observability.

## Phase 5 — Continuous development engine

- project-event ingestion;
- evolving risk, timeline, budget, and next-action state;
- audit history;
- human approval gates;
- portfolio exposure and expected-outcome modeling;
- configurable project templates for solar, storage, data-center power, and off-grid microgrids.
