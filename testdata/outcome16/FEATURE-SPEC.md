# Round16 typed per-station sampling failure

## Scenario and ecosystem difference
Monitoring consumers need to route invalid coordinates, outside coverage,
bitmap/stencil missingness and unsupported polar-vector operations differently.
Existing Sample(None)/outside-or-missing merges them. Decoder and selection
errors already return GribError in an earlier phase and remain separate.
Live Mooncakes grib query found no modules (not a global absence claim).
MoonMissingness README/diagnose API operate on nullable tables for summaries
and imputation; that does not recover this sampler's spatial execution context.
Prior13 NyaCSV evidence already establishes generic CSV parsing. No parser,
imputation dependency or generic error framework is imported or invented.

## Contract and compatibility
- Add sample_result(Station)->Result[Sample,SampleFailure] on GriddedField.
- SampleFailure variants: InvalidStation,OutsideGrid,MissingData,
  UnsupportedPolarVector,NonFiniteResult. Stable ToJson strings:
  invalid-station,outside-grid,missing-data,unsupported-polar-vector,
  nonfinite-result.
- Report the first blocker in existing evaluation order, not every cause.
  Coordinate validation precedes coverage. Zero-weight stencils cannot fail.
  Reached polar-vector policy precedes polar mask checks; a prior nonpolar
  missing stencil may precede a later unsupported polar row.
- NonFiniteResult labels only the existing final numeric guard. No malformed
  field is invented to exercise it; no public-input runtime reproduction for
  that defensive tag is claimed.
- Old sample uses the same kernel and converts failure to the exact legacy
  None/empty-contributors/outside-or-missing result. Old Sample structure/JSON,
  selectors, GribError, batch interfaces and11-column CSV remain.
- Keep the entire ordinary/subnormal/15 overflow numeric block byte-identical.
  No new format/grid, loosened input, units/calendar or CSV status column.
  The new result is per station and does not absorb decode/selection errors.

## Acceptance
Four new tests cover regional outcomes, wrap/zero weights, scalar/vector and
all-missing poles, first-blocker semantics, outer failure phases and stable
public failure JSON codes. Run the2 existing stencil/polar policy regressions
affected by the helper return type. Actual CLI and external typed consumers
route failures, with independent JSON/provenance readback on JS/Wasm-GC.
Verify old public signatures and exact numeric block identity. Do not rerun15
extreme,13 consumer,12 laziness or14 unconfirmed metadata variants. One clean
relevant verification pass, then accurate docs/ZIP/all-file readback and pins.
No memory/performance/whole-input-streaming promise.
