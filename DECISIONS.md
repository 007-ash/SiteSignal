# decisions.md — SiteSignal V1

Format: **Chose X over Y because Z.**

These decisions are written to be defended aloud. They separate source facts, product policies, engineering tradeoffs, and open assumptions.

## Product boundary

1. **Chose parcel-triage support over permit or construction prediction** because public desktop data can identify constraints and comparative suitability, but it cannot replace field studies, legal review, grid studies, landowner negotiations, or project finance.

2. **Chose “rank parcels and prescribe the next diligence action” over “produce one magic viability score”** because early development is a sequence of uncertainty-reduction decisions. The useful output is not only which parcel looks strongest, but which inexpensive next step can most change confidence.

3. **Chose one fully supported county over nominal statewide coverage** because a smaller validated data pipeline is more valuable than broad claims built on inconsistent parcel availability and untested source adapters.

4. **Chose St. Lawrence County as the Phase 1 county over an arbitrary county** because standardized public parcel polygons are available and the county contains public ORES matters that can support realistic regression analysis. Those matters are context cases, not automatic high/low labels.

5. **Chose individual tax parcels as the Phase 1 unit of analysis over multi-parcel project assemblages** because parcel-level screening is a tractable first product. The limitation is explicit: Phase 1 identifies promising components of a site but does not optimize land assembly.

## Decision architecture

6. **Chose deterministic, versioned geospatial rules over LLM-involved scoring** because the same geometry, source versions, configuration, and code should reproduce the same eligibility result and score.

7. **Chose a bounded Claude Messages API call over the Claude Agent SDK for Phase 1 explanation** because the model performs one structured transformation and uses no tools. The Agent SDK is reserved for Phase 3, when ordinance and permitting research requires retrieval, iteration, citations, and tool execution.

8. **Chose direct immutable result input over having the model call SiteSignal’s public API** because an internal network loop adds latency, authentication, duplicate contracts, and failure modes without improving the Phase 1 explanation.

9. **Chose synchronous SQLAlchemy database access over async for Phase 1** because the immediate performance risks are spatial-query design, data volume, and ETL throughput—not demonstrated high-concurrency I/O. Async will be reconsidered only after profiling shows a real concurrency bottleneck.

10. **Chose thin routers, application services, pure domain functions, and repositories over route-owned business logic** because HTTP, orchestration, deterministic calculation, and persistence should be independently testable.

## Eligibility model

11. **Chose constraint-area subtraction followed by a contiguous-usable-acreage test over whole-parcel elimination on first intersection** because a wetland, floodway, protected area, or steep section may affect only part of a parcel.

12. **Chose largest contiguous usable area over total leftover acreage alone** because multiple disconnected fragments can add up to enough acres while still failing to support a coherent project layout.

13. **Chose requested MW multiplied by a versioned acres-per-MW configuration over one fixed minimum-acreage threshold** because project size changes the land requirement and the assumption must be visible and replaceable.

14. **Chose configurable PAD-US classifications over treating every PAD-US polygon as prohibited** because PAD-US records varied ownership, management intent, access, and protection status. SiteSignal must state which classes it excludes.

15. **Chose NWI as a preliminary constraint and diligence flag over a jurisdictional wetland determination** because NWI is a desktop habitat inventory and does not establish the legal presence, absence, or extent of regulated wetlands.

16. **Chose regulatory floodway as a conservative SiteSignal exclusion over attempting engineering-level floodway review** because potential encroachment may require hydraulic analysis, no-rise evidence, local approval, or map revision beyond an early desktop screen. This is a product-risk policy, not a claim that all floodway development is universally impossible.

17. **Chose 1% annual-chance floodplain exposure as a weighted penalty plus explicit flag over automatic elimination** because development may remain possible but can require additional engineering, permitting, design, and cost.

18. **Chose slope derived from a pinned USGS 3DEP elevation source over an undefined “USGS slope” dataset** because slope is a reproducible transformation whose source resolution, method, units, threshold, and output version must be recorded.

## Suitability scoring

19. **Chose five defensible Phase 1 sub-scores over forcing six factors into the composite** because a smaller set of clearly defined metrics is more auditable than an extra signal whose mapping and meaning are unresolved.

20. **Chose substation and transmission distance as explicit proximity proxies over calling them interconnection viability** because geometry can measure closeness, while actual capacity, upgrade cost, route feasibility, and study results require deeper grid evidence.

21. **Chose FEMA floodplain exposure, land-cover suitability, and existing land-use compatibility as the remaining Phase 1 factors over broader development-risk claims** because they can be computed from documented parcel-level sources.

22. **Chose existing land-use compatibility over “zoning compatibility” for ORPTS property-class data** because property class describes use for assessment purposes and does not establish the governing zoning district or permission for utility-scale solar.

23. **Chose verified zoning as a future sourced flag or research result over inferring it from parcel class** because local laws, maps, moratoria, and special-use provisions require authoritative municipal evidence.

24. **Chose NYISO queue context as an experimental flag over a weighted Phase 1 score** because queue records do not yet provide a validated mapping from a parcel to a likely point of interconnection or a clean causal measure of congestion.

25. **Chose raw metric + units + score + missing-data state over returning a score alone** because an auditor or interviewer should be able to reconstruct what the score represents.

26. **Chose explicit missing/stale-data flags over silently substituting neutral scores** because absence of evidence is not evidence of average suitability.

## Data and ETL

27. **Chose ETL as a core product capability over treating it as invisible plumbing** because the domain problem is fragmented, differently formatted, differently projected, and frequently updated public data.

28. **Chose append-only dataset manifests and load-run records over replacing files without history** because reproducibility requires the source, retrieval time, version, checksum, license, field mapping, CRS, repair policy, and rejection counts used by each screening run.

29. **Chose idempotent source adapters over one-off import scripts** because the same source must be refreshable, testable, and safe to rerun without duplicating records.

30. **Chose retaining source metadata plus normalized analysis geometry over discarding source context** because provenance and correct area/distance calculations are both required.

31. **Chose county-specific projected analysis coordinates, beginning with the appropriate St. Lawrence County projection, over measuring acres or distance in latitude/longitude** because geographic degrees are not reliable units for metric geometry.

32. **Chose an explicit county support matrix over assuming FIPS parameterization means universal support** because standardized public parcel polygons and source quality vary by county.

33. **Chose pinned infrastructure-layer vintages over an unversioned live dependency** because public transmission and substation layers can be stale, moved, or archived. Phase 1 must record exactly which data was used and describe it as a proximity proxy.

## Testing and validation

34. **Chose synthetic geometry tests plus real-project regressions over either approach alone** because synthetic fixtures prove exact edge behavior while public project records test whether the whole system behaves plausibly.

35. **Chose ORES outcomes as contextual evidence over automatic training or test labels** because a permitted project can contain major constraints and a withdrawn project can stop for reasons unrelated to parcel quality.

36. **Chose documented case-specific assertions over “permitted must score high” and “withdrawn must score low”** because valid regressions check whether known constraints and uncertainty are surfaced without inventing causality.

37. **Chose configuration sensitivity analysis over calibrating thresholds to make one famous project pass** because reverse-engineering one outcome would hide overfitting rather than validate the model.

38. **Chose deterministic tie-breaking and versioned score bands over unstable ranking** because repeated runs with unchanged inputs should return the same ordered shortlist.

## Delivery and scaling

39. **Chose an early Railway/PostGIS deployment spike over waiting until final deployment** because local success does not prove the target environment supports the required database extension, migrations, and spatial queries.

40. **Chose synchronous screening runs first with persisted run records over premature distributed orchestration** because correctness, reproducibility, and measurable query behavior come before worker infrastructure.

41. **Chose phased scaling—grid depth, agentic permitting, statewide portfolios, then a continuous development engine—over adding unrelated AI features** because each phase expands the same customer workflow and data model.

42. **Chose the Claude Agent SDK for Phase 3 permitting research over using it merely to satisfy a job-description keyword** because tool use becomes technically justified when the system must retrieve, compare, cite, and monitor unstructured local rules.

43. **Chose human approval for external submissions and material state changes over autonomous filing** because an auditable development assistant should accelerate expert work without silently committing legal, financial, or permitting actions.

## Open configuration decisions

These items must be resolved through official metadata review, domain research, and sensitivity testing before the associated scorer is locked:

- selected PAD-US protection classes;
- slope units, derivation method, and threshold;
- gross or usable acres-per-MW assumption;
- minimum contiguous patch and shape-quality rules;
- floodplain exposure metric and bands;
- land-cover class mapping;
- land-use class mapping;
- composite weights and tier boundaries;
- qualifying transmission-voltage filter;
- exact St. Lawrence analysis CRS;
- infrastructure-source selection and freshness acceptance;
- supported-county data-quality thresholds.

## Interview summary

> SiteSignal V1 is a deterministic parcel-triage engine. It subtracts preliminary constraint geometry, tests whether enough contiguous usable land remains for the requested MW, scores survivors on five documented parcel-level proxies, and returns the next diligence action. The LLM explains an immutable result. It does not decide. Deeper grid analysis, real zoning research, multi-parcel assembly, and continuous project management arrive in later phases because those require different evidence and system behavior.