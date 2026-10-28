# Round15 bounded numerical repair closure

One public-input correctness bug is confirmed: finite extreme polar means can
overflow in ordinary weighted accumulation and be returned as None. No new API
or optional status feature is added. Round14 scan questions stay report-only.

| Acceptance | Actual evidence |
|---|---|
| Valid public-input reproduction | Confirmed11x2 simple-packed field uses ordinary E=-28,D=-300. Decoded-node MAX assertion passes, then the old pole sample fails None versus Some(MAX); before-js.stdout.txt. Initial D=-308 candidate failed decoding and is explicitly not the reproduction. |
| Minimum numerical correction | Only sampling.mbt changes among old implementation files. Original ordinary/subnormal arithmetic retained, followed by a nonfinite-result-only unit-magnitude recomputation and represented-weight normalisation. Public API identity exact. |
| Independent extreme means |4 new tests cover8 encoded fixtures: positive constants11/17/100 longitudes, negative south constants11/17, varying near-limit100-row, missing neighbour and wind policy. Fraction means/half-bands are independent of floating reduction. Constant pole results compare exactly; other new numerical comparisons use declared4e-15 relative tolerance. |
| Relevant existing behavior |12 affected subnormal/ordinary regressions and2 existing polar/missing-policy regressions pass per target. No other prior consumer/laziness/scientific/download set rerun. |
| Actual output/consumer |New synthetic cmd/extreme emits8 CSV rows per target:4 finite extreme values,4 spatial gaps. Independent external public-API batch consumer emits JSON. Python strict CSV/JSON plus exact Fraction normalised contributor means verify values/provenance/metadata without overflowing the reader's own sum. |

JS/Wasm-GC each pass18 relevant tests and actual new CSV/external consumer runs.
Old sampler's finite ordinary path retains normal rounding; the observed south
band differs by3 ULPs from a constant contributor, within the declared tolerance.
The initial independent verifier required an unsupported exact bound there;
VERIFIER-NOTE.json records its correction without product changes or repeated
passed JS commands. Exact pole assertions and finite/Fraction checks remain.

Contributor weights/algorithm labels/CSV schema are unchanged. The fallback
normalises represented weights to keep a finite convex result; downstream code
recomputing extreme means needs stable arithmetic rather than naive sum(w*v).
No general precision/RSS/performance guarantee, decoder or supported-format change.

The optional missing-cause status idea remains a report-only need. Bounded
MoonMissingness README/diagnose API review supplies context; it operates on
nullable tables, whereas the proposed spatial cause labels need execution
context. No ecosystem code/dependency imported or absence/novelty claim.
