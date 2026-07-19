# decisions.md — SiteSignal bounded V1

Format: **Chose X over Y because Z.**

This document supersedes the original broad Phase 1 plan. The previous decisions remain available in Git history.

## Scope reset

1. **Chose a bounded technical vertical slice over the original nine-milestone product plan** because SiteSignal’s portfolio value comes from demonstrating real spatial-data engineering, not from approximating an entire renewable-development platform before applications begin.

2. **Chose one supported county and a reproducible parcel subset over county-wide or statewide ingestion** because a smaller validated dataset can prove PostGIS, provenance, geometry handling, ranking, persistence, and deployment without spending most of the schedule on data coverage.

3. **Chose a deployed API over a frontend** because the distinctive engineering work is in the spatial database, ingestion, geometry calculations, deterministic logic, and tests. A map interface would consume time without materially strengthening that signal.

4. **Chose two real vector constraint layers over four environmental and terrain sources** because NWI wetlands and FEMA regulatory floodway data are enough to prove multi-source spatial intersection, overlap handling, subtraction, and provenance. Raster-derived slope is deferred.

5. **Chose a small transparent ranking model over five suitability factors** because a reconstructable score based on usable geometry is more defensible than several hurried proxies requiring additional datasets and calibration.

6. **Chose to defer NYISO, infrastructure, zoning, ORES regressions, multi-parcel assembly, and agentic research** because each requires a separate evidence model and would dilute the bounded V1’s technical focus.

## Product boundary

7. **Chose parcel-triage support over permit or construction prediction** because public desktop data can identify constraints and comparative usable land, but it cannot replace field studies, legal review, engineering, grid studies, landowner negotiations, or project finance.

8. **Chose individual tax parcels as the unit of analysis over multi-parcel assemblages** because parcel-level screening is sufficient to demonstrate the spatial workflow while keeping the result interpretable.

9. **Chose requested MW multiplied by a versioned acres-per-MW assumption over one fixed acreage threshold** because project size changes the land requirement and the assumption must remain visible and replaceable.

10. **Chose exact flags and next diligence needs over unsupported certainty** because the useful output is what the data shows, what remains unknown, and what should be verified next.

## Spatial decision model

11. **Chose constraint subtraction over whole-parcel elimination on first intersection** because a mapped wetland or floodway may affect only part of a parcel.

12. **Chose largest contiguous usable acreage over total usable acreage alone** because disconnected fragments can sum to enough land while failing to support one coherent project area.

13. **Chose unioning overlapping constraints before subtraction over summing each layer independently** because independently summed intersections can double-count the same constrained land.

14. **Chose NWI as a preliminary mapped-wetland constraint and diligence flag over a jurisdictional wetland determination** because NWI is a desktop habitat inventory and does not establish legal wetland boundaries.

15. **Chose FEMA regulatory floodway as a conservative early-screen constraint over an engineering-level legal conclusion** because potential encroachment can require hydraulic analysis, local approval, or map revision beyond this product.

16. **Chose projected analysis coordinates over measuring acres in latitude and longitude** because geographic degrees are not reliable area units.

17. **Chose an explicit geometry repair-or-reject policy over silently accepting invalid geometry** because overlay results must be reproducible and provenance must reveal when source geometry was altered.

## Ranking

18. **Chose eligibility, contiguous-acreage surplus, usable percentage, and fragmentation as the initial ranking inputs over external suitability proxies** because these metrics are directly derived from the spatial result and can be independently reconstructed.

19. **Chose raw metric, units, score contribution, configuration version, and source versions over returning a score alone** because the ranking must be auditable.

20. **Chose explicit missing-data and diligence flags over neutral-score substitution** because missing evidence is not average suitability.

21. **Chose deterministic tie-breaking over unstable ordering** because identical inputs and source versions must produce the same shortlist.

22. **Chose versioned bands and weights over hidden constants** because future calibration should not erase which rules produced an earlier result.

## Data and provenance

23. **Chose ETL as a product capability over invisible one-off import work** because fragmented public geospatial data is a central part of the engineering problem.

24. **Chose append-only dataset manifests and load-run records over replacing sources without history** because each screening result must be traceable to the source URL, date, checksum, CRS, mapping, repair policy, and load statistics used.

25. **Chose idempotent source adapters over disposable scripts** because the same bounded data must be safe to reload during development, testing, and deployment.

26. **Chose retaining source IDs and classifications alongside normalized geometry over discarding source context** because reproducibility requires both analysis-ready geometry and original source meaning.

27. **Chose GiST indexes and PostGIS-native spatial queries over loading all geometry into application memory** because the project is intended to demonstrate spatial-database design and reproducible query behavior.

## Application architecture

28. **Chose FastAPI, SQLAlchemy 2.0, GeoAlchemy2, Alembic, PostgreSQL, and PostGIS over a generic CRUD-only stack** because the project’s differentiator is a persisted API around real spatial operations and schema evolution.

29. **Chose synchronous SQLAlchemy access over async for V1** because the immediate risks are spatial-query correctness, data quality, and deployment—not demonstrated high-concurrency I/O.

30. **Chose a focused package structure over pre-creating router, service, domain, repository, model, and schema layers with no behavior** because architecture should follow real responsibilities rather than create empty ceremony.

31. **Chose thin HTTP handlers and an application service over route-owned orchestration** because request validation, screening workflow, persistence, and spatial calculation should remain independently testable.

32. **Chose PostGIS for production geometry operations and small synthetic fixtures for exact tests** because the deployed behavior should exercise the database while controlled tests make edge cases understandable.

## Validation and delivery

33. **Chose synthetic geometry tests plus one bounded real-data workflow over a full ORES regression suite** because synthetic fixtures prove exact spatial behavior and one reproducible public-data run proves end-to-end plausibility within the schedule.

34. **Chose an early Railway/PostGIS proof over waiting until final deployment** because local spatial success does not prove the target environment supports the extension, migrations, storage behavior, and health checks.

35. **Chose a deployed API, sample response, screenshots, and limitations over extensive styling** because inspectable technical evidence is more valuable than presentation work that hides an incomplete core.

36. **Chose to freeze Phase 1 after the bounded vertical slice is validated and deployed over continuously expanding the roadmap** because portfolio breadth and interview preparation have higher marginal value after the core spatial system is complete.

37. **Chose an optional bounded diligence memo only after the deterministic core works over making the LLM part of the critical path** because the memo should explain an immutable result, never delay or alter it.

## Runtime and packaging

38. **Chose separate SiteSignal release and Python runtime declarations over using one version number for both** because `project.version` identifies the SiteSignal application release (`0.1.0`), while `requires-python` defines the supported interpreter range (`>=3.13,<3.14`). The exact local development interpreter is pinned separately in `.python-version` (`3.13.0`) because SiteSignal and Python releases evolve independently.

39. **Chose `pyproject.toml` as the Python dependency and tool-configuration source of truth over manually maintaining duplicate dependency lists** because competing files can drift and cause local, CI, and deployment environments to install different packages.

40. **Chose PostgreSQL 18 with PostGIS 3.6 using `postgis/postgis:18-3.6` over an unversioned `latest` image** because the selected PostGIS line supports PostgreSQL 18, while pinning the database and extension version lines prevents an upstream major or minor change from altering compatibility, storage behavior, or spatial-extension behavior without review.

## County and subset selection

41. **Chose Oswego County over St. Lawrence County for the bounded V1** because official Oswego parcel polygons are publicly available, NWI provides downloadable New York wetland data, and FEMA publishes a countywide Oswego NFHL package (`36075C-NFHL`). This gives both required constraint sources a documented coverage path without manufacturing missing data.

42. **Chose a reproducible parcel subset defined before scoring over hand-picked demonstration parcels** because the same pinned source snapshot and documented query should produce the same candidate IDs regardless of the results. The exact municipality or extent remains open until parcel quality and nonzero NWI and floodway coverage are verified.

### Static typing for environment-backed settings

43. Use Pydantic's mypy plugin because `Settings()` loads required values such as `DATABASE_URL` from environment configuration at runtime. Do not add fake defaults solely to satisfy static type checking; required configuration should continue to fail fast when missing.

44. For the bounded single-instance V1, the API container runs alembic upgrade head before starting Uvicorn. This guarantees that the database schema is current at startup. A multi-instance deployment would move migrations into a separate release step to avoid concurrent migration attempts.

## Open configuration decisions

These items must be resolved through official metadata review, domain research, or controlled fixtures before their associated behavior is locked:

- exact Oswego parcel source snapshot, municipality or extent, and deterministic subset rule;
- exact NWI and FEMA NFHL source vintages;
- confirmation that the selected subset extent contains nonzero NWI and regulatory-floodway geometry;
- exact Oswego analysis CRS;
- geometry repair-versus-reject policy;
- gross or usable acres-per-MW assumption;
- minimum contiguous patch rule;
- ranking bands, weights, and tier boundaries;
- source-freshness acceptance;
- Railway API build strategy and Python patch-version handling.

## Documentation boundaries for parcel ingestion

### Decision

Parcel-ingestion documentation is separated by responsibility:

- `docs/data-sources/oswego-parcels.md` documents the source itself:
  publisher, official dataset identity, acquisition policy, provenance,
  source vintage, limitations, and the V1 extraction boundary.

- `docs/data-sources/oswego-parcel-field-map.md` documents how the source
  schema maps into SiteSignal:
  approved source fields, normalized field names, parcel identity,
  intentionally excluded fields, and observed data-quality findings.

- `docs/data-sources/oswego-parcel-ingestion-rules.md` documents loader
  behavior:
  validation, idempotency, duplicate handling, quarantine rules, acreage
  policy, privacy restrictions, pagination, and geometry-processing rules.

- `docs/crs-policy.md` documents spatial-coordinate behavior:
  source CRS preservation, validation, reprojection, analysis CRS, area
  calculations, and output transformations.

### Rationale

Keeping these concerns separate makes each document answer one clear question:

1. Where did the data come from?
2. What does each field become inside SiteSignal?
3. What must the ingestion code do?
4. How are spatial coordinates handled?

This prevents source facts, database mapping decisions, loader behavior, and
spatial policy from becoming mixed together in one large document.

### Consequence

When the source changes, update the source and field-map documents. When loader
behavior changes, update the ingestion-rules document. When coordinate-system
behavior changes, update the CRS policy.

Code changes that alter one of these contracts must update the corresponding
document in the same pull request.

## Reusable architecture does not mean universal county support

### Decision

SiteSignal's normalized parcel schema, provenance model, PostGIS workflow, and
spatial-analysis engine are designed to be reusable across jurisdictions.

The source adapter is not universal. Each county may publish different field
names, identifiers, formats, coordinate systems, licenses, and update
procedures. Supporting another county therefore requires a county-specific
source adapter, field map, CRS validation, and ingestion test.

Phase 1 supports only the documented New Haven subset inside Oswego County.
The API and ingestion command must reject unsupported jurisdictions rather
than implying nationwide compatibility.

### Rationale

This preserves an extensible architecture without falsely claiming that one
loader can ingest every county parcel dataset in the United States.

### Consequence

Adding another county is an explicit development task, not merely a
configuration change. The reusable core remains unchanged where possible, but
the new source must pass its own preflight, mapping, provenance, validation,
and idempotency checks.

## Milestone 1 retrospective: scope became too broad

Milestone 1 took longer and became harder to reason about because it combined
too many distinct responsibilities:

- source research and field inspection;
- privacy and identity decisions;
- CRS policy;
- provenance schema design;
- migrations;
- extraction;
- geometry conversion and validation;
- attribute normalization;
- idempotent database loading.

Although the completed result is useful, the milestone stopped feeling like
one coherent unit of work.

Future milestones must have:

- a hard scope boundary;
- an explicit exit test before implementation begins;
- a fixed timebox;
- only the work consumed by that milestone;
- optional abstraction cut before extending the schedule.

The accepted Milestone 1 result is intentionally bounded to the official
New Haven parcel subset: 1,636 source records, 1,635 valid parcels loaded,
one invalid source geometry rejected, and repeatable idempotent reloads.
