# Round15 finite convex-mean overflow repair

## Confirmed reproduction
Supported3.0/4.0/5.0 public input,11x2 scalar grid at90/89 degrees. Every
decoded node equals finite Double.MAX (explicit first assertion passes).
Sampling the pole returns None because ordinary weighted summation overflows,
although the exact mean of identical finite values is that same value.
before-js.stdout.txt records the actual failing sample assertion.

The first extreme-scale candidate failed decoding and did not prove this bug;
it and its logs are retained as unproven. The confirmed fixture uses the
existing ordinary E=-28,D=-300 path, not a change to scale decoding.

## Minimum correction
Leave ordinary and existing subnormal arithmetic byte-identical. Only after
the original accumulated result is nonfinite, find the maximum absolute
contributor value, sum unit-magnitude weighted values and represented weights,
divide, clamp the unit result to[-1,1] and rescale. A finite convex mean is then
kept finite instead of being mistaken for a spatial/missing-data gap.
Existing missing stencil/vector-pole rejection still happens before this step.
No status API, schema, GRIB/template, unit/calendar or query changes.

## Acceptance
Use independent Fraction arithmetic over decoded binary64 input values for
polar means and adjacent-band interpolation. Cover positive/negative extreme
constants, varying near-limit rows, both poles, bitmap missing neighbours,
vector-pole policy and ordinary-scale controls. Keep public signatures exact.
Prove actual new extreme station CSV rows are finite with preserved metadata/
contributors and a real external public-API consumer on JS/Wasm-GC.
Run relevant new and affected numerical regressions once after final formatting,
not prior13/12 CSV scenarios or old downloads.

## Deferred need
The existing outside-or-missing label conflates causes. A typed diagnostic
extension was researched but remains report-only: the reproduced numerical
bug takes priority and no extra public API is necessary for this correction.
MoonMissingness diagnoses/imputes nullable tabular input; it supplies general
missingness tooling, not this decoder's spatial-policy execution context.
No ecosystem code/dependency imported or broad novelty/absence claim made.
