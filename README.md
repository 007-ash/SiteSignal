# SiteSignal

**Fail weak solar sites early. Focus diligence where it can still change the answer.**

SiteSignal is a deterministic geospatial screening engine for early-stage solar development. Given a project size and a supported county, it ranks candidate parcels, shows how much land remains usable after preliminary constraints, explains the factors behind each score, and recommends the next diligence step.

The deterministic layer computes every eligibility decision, metric, score, tier, and flag. The language model explains the completed result; it cannot change it.

> **Status:** Phase 1 design is complete. Implementation begins with St. Lawrence County, New York.

## Why this exists

Early-stage renewable development is a portfolio problem. Developers must investigate many possible sites while knowing that most proposed projects will never reach operation.

Berkeley Lab's *Queued Up: 2026 Edition* reports that, at the end of 2025:

- more than 2,060 GW of generation and storage was actively seeking grid interconnection;
- only 13% of capacity entering queues from 2000–2020 had reached commercial operation;
- projects completed in 2025 spent a median of more than five years between interconnection request and operation.

Queue data does not prove why any individual project fails. It does show why developers cannot afford to spend deeply on every candidate. SiteSignal addresses one early, inexpensive part of that problem: identify obvious land constraints, rank the survivors, expose uncertainty, and point to the next action that can remove the most risk.

## The question SiteSignal answers

> For a proposed project of this size, which parcels deserve investigation first, what reduced their usable area, what risks remain, and what should a developer verify next?

SiteSignal is a desktop pre-development screen. It is not a legal determination, engineering study, wetland delineation, interconnection study, survey, permit, or investment recommendation.

## Phase 1 workflow

```text
Project specification
(requested MW + supported county)
        |
        v
Candidate tax parcels
        |
        v
Preliminary constraint geometry
(PAD-US classes, NWI, FEMA floodway, excessive slope)
        |
        v
Constraint subtraction
        |
        v
Largest contiguous usable area
        |
        +---- insufficient for requested MW ----> ELIMINATED
        |
        v
Five deterministic suitability scores
        |
        v
Ranked shortlist + tier + conditional flags
        |
        v
Bounded explanation
(strengths, risks, limitations, next diligence action)
```

## The central design decision

SiteSignal does **not** eliminate an entire parcel merely because one constraint touches it.

Instead:

```text
gross parcel geometry
- configured protected-area exclusions
- preliminary wetland constraint geometry
- conservative regulatory-floodway exclusion
- excessive-slope geometry
= potentially usable geometry
```

The parcel is eliminated only when its **largest qualifying contiguous usable area** is below the configured acreage required for the requested project size.

This matters because real solar projects can avoid, redesign around, mitigate, or investigate constraints that affect only part of a larger site.

## Phase 1 decision model

### Preliminary constraint geometries

| Constraint | Initial source | Phase 1 treatment |
|---|---|---|
| Protected or conserved land | USGS PAD-US | Subtract only explicitly configured protection classes |
| Mapped wetland habitat | USFWS National Wetlands Inventory | Preliminary constraint area + field-delineation flag |
| Regulatory floodway | FEMA NFHL | Conservative SiteSignal exclusion area |
| Excessive slope | Slope derived from USGS 3DEP elevation | Subtract area above configured threshold |

### Final eligibility test

| Test | Meaning |
|---|---|
| Largest contiguous usable acreage | Must meet the configured acreage requirement for the requested MW |

The acres-per-MW assumption, slope threshold, minimum contiguous patch size, and selected PAD-US classes are versioned configuration—not hidden constants.

### Five weighted suitability factors

| Factor | Initial source | What it means |
|---|---|---|
| Distance to qualifying substation | Pinned public infrastructure layer | Proximity proxy, not capacity |
| Distance to qualifying transmission | Pinned public infrastructure layer | Proximity proxy, not a viable route or interconnection result |
| 1% annual-chance floodplain exposure | FEMA NFHL | Added engineering, permitting, and design risk |
| Land-cover suitability | USGS National Land Cover Database | Relative suitability of the surviving land |
| Existing land-use compatibility | NYS ORPTS property-class data | Current-use proxy; explicitly not zoning |

Every factor returns its raw metric, units, score, source version, and missing-data state.

### Conditional and experimental flags

Flags remain separate from the composite when the evidence is incomplete or the item requires deeper review:

- desktop wetland screen requires field delineation and jurisdictional review;
- floodplain development review may be required;
- municipal zoning is unknown until verified from an authoritative local source;
- source data is stale, missing, or outside supported coverage;
- NYISO queue or likely-point-of-interconnection context is experimental until a defensible parcel-to-grid mapping is validated.

## Output

A parcel result will resemble:

```json
{
  "parcel_id": "example",
  "eligible": true,
  "requested_mw": 5,
  "gross_acres": 82.4,
  "usable_acres": 61.8,
  "largest_contiguous_usable_acres": 54.2,
  "constraints": {
    "nwi_acres": 7.1,
    "floodway_acres": 0.0,
    "steep_slope_acres": 4.8,
    "protected_acres": 0.0
  },
  "raw_metrics": {},
  "subscores": {},
  "composite_score": 81,
  "tier": "investigate",
  "flags": [
    "desktop_wetland_screen_only",
    "zoning_unknown"
  ],
  "next_diligence_action": "Verify municipal solar law and commission a wetland delineation.",
  "data_versions": {}
}
```

## Tiers

Phase 1 uses three operational tiers:

- **Investigate** — strong enough to justify the next diligence spend.
- **Marginal** — potentially viable, but the next identified risk should be tested before broader spend.
- **Avoid** — surviving parcel is weak relative to alternatives, even if no automatic elimination fired.

The tiers are portfolio-triage recommendations, not permit predictions.

## Validation strategy

SiteSignal uses two kinds of tests.

### Synthetic tests

Controlled geometry fixtures prove exact behavior:

- touching versus overlapping;
- partial and complete constraint coverage;
- overlapping constraint layers;
- invalid geometries;
- disconnected usable fragments;
- exact threshold boundaries;
- missing data;
- deterministic ranking and tie-breaking.

### Real-project regression cases

Public ORES matters test whether the complete system produces plausible, disciplined output:

| Project | Matter | Use in validation |
|---|---|---|
| Rich Road Solar | 22-02969 | Permitted case; must not be falsely declared impossible because constraints affect part of a project area |
| Cider Solar | 21-01108 | 500 MW permitted cross-county case; exercises parameterized data interfaces |
| Moss Ridge Solar | 24-03042 | Withdrawn contextual case; withdrawal is not treated as a low-score label |
| Shepherd's Run Solar | 24-03041 | Active/contested case; exercises floodplain, wetland, local-law, and uncertainty flags |

Real outcomes are never scoring inputs. Permit or withdrawal status does not automatically mean that every associated parcel must score high or low.

## Phase 1 scope

### Included

- one fully supported county: St. Lawrence County, New York;
- parameterized county ingestion;
- parcel-level screening;
- preliminary environmental and terrain constraints;
- five deterministic suitability factors;
- ranked shortlist and parcel detail;
- reproducible data provenance;
- bounded diligence memo;
- synthetic and real-project regression tests.

### Deliberately excluded

- multi-parcel assemblage optimization;
- legal wetland or jurisdictional determinations;
- detailed solar-array layout;
- title, easement, and landowner willingness;
- municipal zoning conclusions without authoritative local data;
- hosting-capacity or power-flow modeling;
- CESIR, cluster-study, or interconnection-cost prediction;
- project finance, offtake, federal policy, and supply-chain risk;
- permit probability.

New York currently publishes standardized public parcel polygons for a subset of counties under one common schema. County parameterization therefore means the pipeline can support additional counties through validated adapters; it does not mean every county is automatically supported.

## API target

```text
POST /screening-runs
GET  /screening-runs/{run_id}
GET  /screening-runs/{run_id}/parcels
GET  /parcels/{parcel_id}
GET  /health
GET  /ready
```

A screening run persists its requested MW, county, configuration version, source versions, candidate counts, timing, and ordered results.

## Architecture

```text
FastAPI routers
      |
Application services
      |
Pure geospatial/domain functions
      |
Repository interfaces
      |
SQLAlchemy 2.0 + GeoAlchemy2
      |
PostgreSQL + PostGIS
```

Cross-cutting components:

- Alembic migrations;
- append-only dataset manifests and load runs;
- idempotent source adapters;
- Pydantic v2 contracts;
- structured logging and timing;
- pytest unit, integration, and regression suites;
- Claude Messages API for the bounded Phase 1 explanation layer.

## Why the language model does not score

A screening result should be reproducible from:

1. the same parcel geometry;
2. the same source-layer versions;
3. the same configuration;
4. the same deterministic code.

The model receives the completed result and may explain:

- what helped the parcel;
- what reduced usable acreage;
- what remains uncertain;
- what the developer should verify next.

It cannot modify the score, tier, metrics, constraints, flags, or source versions. A model failure does not block access to the deterministic result.

## Roadmap

### Phase 2 — Grid depth and preliminary design

Replace simple proximity with stronger evidence:

- utility hosting-capacity data where available;
- route-to-point-of-interconnection analysis;
- versioned NYISO queue snapshots and process-regime tagging;
- basic buildable-area and conceptual layout checks;
- project archetypes such as environmental-heavy, permitting-heavy, or capacity-constrained;
- next-step recommendations based on the cheapest action that removes the most uncertainty.

Queue information becomes a score only after parcel-to-electrical-location mapping and outcome validation are defensible.

### Phase 3 — Agentic permitting and diligence research

Introduce the Claude Agent SDK for work that genuinely requires tools and iterative research:

- retrieve municipal solar laws, zoning ordinances, moratoria, and special-use rules;
- inspect town-board minutes and ORES/DPS filings;
- distinguish current rules from superseded versions;
- extract structured requirements with citations;
- propose a development plan while preserving human approval;
- monitor selected sources for material changes.

The agent organizes unstructured evidence. Deterministic services continue to own calculations and final structured fields.

### Phase 4 — Statewide and portfolio scale

Move from one supported county to portfolio-scale operation:

- validated county adapters and support matrix;
- multi-parcel assemblage generation;
- batch screening jobs and worker queues;
- object storage for raw geospatial sources;
- pre-clipped county tiles and precomputed overlays;
- GiST indexes, query-plan analysis, caching, and incremental refreshes;
- portfolio comparison, saved searches, and reruns when datasets change;
- observability for ingest failures, stale layers, run duration, and ranking drift.

The scaling goal is not merely more traffic. It is processing larger and more varied geospatial data while retaining provenance and reproducibility.

### Phase 5 — Continuous development engine

Expand from a one-time site screen into a continuously updated development system:

- ingest new filings, reports, correspondence, and design revisions;
- update risk states, next actions, timelines, and budget assumptions;
- maintain an auditable project history;
- require human approval for external submissions and material decisions;
- estimate portfolio-level development exposure rather than pretending every project succeeds;
- add configurable templates for storage, data-center power, and off-grid microgrid siting.

This phase generalizes the architecture without pretending that one solar score applies unchanged to every infrastructure type.

## Stack

- Python
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- GeoAlchemy2
- PostgreSQL + PostGIS
- Alembic
- GeoPandas / GDAL / Rasterio for ETL
- pytest
- Claude Messages API in Phase 1
- Claude Agent SDK in Phase 3
- Railway deployment target

## Research basis

The V1 product and roadmap were reviewed against:

- Berkeley Lab, *Queued Up: 2026 Edition*;
- Paces, *Pre-Development at Scale: Modeling Risk in Early-Stage Solar Development*;
- Paces, *The One-Person, Billion-Dollar Power Development Company*;
- Charles Bai, *Why Builders Thrive at Startups*;
- Offgrid AI, *Fast, Scalable, Clean, and Cheap Enough*;
- NYS GIS parcel documentation;
- NYS ORES permit records;
- FEMA floodplain-management rules;
- USFWS National Wetlands Inventory limitations;
- USGS PAD-US documentation;
- NYS ORPTS property-class documentation.

## Core sentence

**SiteSignal does not predict that a project will be built. It finds land worth investigating, shows its work, and identifies the next uncertainty that should be removed before more capital is committed.**

## Development

- See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch workflow, commit standards, validation steps, pull-request process, and secret-handling rules.
