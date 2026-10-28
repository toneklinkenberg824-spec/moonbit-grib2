# Chosen extension: explicit multi-layer station requests

The subnormal sampling repair passed35 related tests on each target before this
extension began (REPAIR-VERIFICATION.json and pinned repair source/build files).

## Real user task and gap
A station service reads one GRIB stream containing temperature at2m,850hPa,
1000hPa and several forecast runs. It needs named results from the exact layer
and run, with existing masks/weights/source provenance. Current select_fields
filters parameter and forecast unit/integer only; callers must inspect surfaces,
reference time and origin themselves and may silently pick the first match.

## Candidate comparison
1. **Choose:** typed product/layer/reference filters, unique-match enforcement,
   and an atomic batch of named field/station requests. Useful with current4.0
   metadata, independently testable, additive and small.
2. Defer polygon/area aggregates: correct cell intersections and geographic
   weighting would require a broader numerical contract.
3. Defer cached station stencils: useful for repeated forecasts but polar masks
   and per-field validity require a separate compatibility/performance study.

## Ecosystem check (2026-10-28)
- Installed moon search grib returned no modules; weather returned10, including
  weatherquery0.1.1, moonaerowx0.1.0, MoonMet0.1.0 and moonwind0.2.0. Logs retained.
  Their registry summaries describe weather queries, aviation text/timelines,
  meteorological calculations and winds-aloft flight planning respectively;
  these are adjacent inputs/calculations rather than evidence of a GRIB layer
  station-selection API. GitHub repository search
  grib2 language:MoonBit returned trkbt10/grib2_mbt; bounded search is not proof
  that no other package exists.
- Its public README/current generated API(blob e5802a56e396bf671b2e01938c22a115d217dc0b)
  expose decoder/record metadata, CLI matching and JS extraction; sample/station
  code search returned no hits. It is the attributed decoder source, not a
  competitor to relabel. This extension adds a MoonBit station workflow with
  typed layer/run identity, unique selection and existing contributors/nulls.
- ECMWF cfgrib already demonstrates filtering heterogeneous GRIB using metadata
  keys. The idea of metadata filtering is not novel. Here the deliverable is an
  additive dependency-free MoonBit API joining exact identity checks to this
  library's provenance-bearing station samples.

Sources: https://github.com/trkbt10/grib2_mbt ,
https://github.com/ecmwf/cfgrib , mooncakes-search-*.log and ECOSYSTEM-RAW.json.

## Contract and acceptance
- FieldQuery.new requires numeric discipline/category/parameter and accepts
  optional centre/subcentre/table versions, six reference components, original
  forecast unit/integer and first/second Surface. Optional filters are wildcards;
  supplied surfaces compare exact encoded kind/scale/value, without unit or
  calendar conversion. A supplied reference-time array is copied and must have6
  components when used. Missing forecast cannot be explicitly requested apart
  from wildcard; existing raw metadata remains available.
- select_unique_field returns the sole match or InvalidRequest on zero/multiple
  matches; never picks an arbitrary first field.
- sample_requested_fields resolves every request before sampling; each key must
  be nonempty and unique. Any unresolved/ambiguous request fails the whole batch.
  Results retain request order, key, field origin/product and per-station Sample.
  Existing missing/outside values stay None/JSON null. Zero requests returns[];
  zero stations still retains each selected field's identity.
- Add no template, decoder dependency, time interpolation, vector conversion or
  implicit layer equivalence. Existing public signatures/behavior are retained.
- Acceptance: independently encoded multi-layer/run fields, typed query ambiguity
  and failure cases, exact raw surface distinctions, copied metadata, missing
  stations, both targets' check/build/tests, runnable cmd/layers and independent
  external workspace JSON consumer. Preserve repair evidence; rerun only checks
  affected by the new source/API/example.
