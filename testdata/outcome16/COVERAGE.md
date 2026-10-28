# Round16 typed sampling outcome closure

No prior correctness defect was claimed. The established integration need is
routing distinct station failures that all appear as legacy None. One additive
Result method supplies that context without changing the legacy representation.

| Acceptance | Evidence |
|---|---|
| Invalid station / outside grid / true missing / unsupported polar vector | New runtime tests cover nonfinite/out-of-range coordinates, regional bounds, bitmap gaps, all-missing scalar pole, wind pole, zero-weight pole exclusion, periodic longitude and success provenance. |
| First blocker, not every cause | South nonpolar missing row precedes later unsupported polar row; invalid coordinate precedes wind policy. Existing evaluation order and policy preserved. |
| Decode and selection remain separate | Declared unsupported template gives outer UnsupportedTemplate; absent/ambiguous queries give outer InvalidRequest. CLI emits3 outer-phase events and6 station events; not relabelled MissingData. |
| Public codes and consumer routing | All5 SampleFailure JSON string encodings checked. External application matches typed variants and routes5 actual cases; independent Python checks routes, sample111, source indices3/4, weights0.5 and metadata. |
| Legacy and numerical compatibility | All old public function signatures preserved. types.mbt and CSV writer unchanged; legacy failure samples retain None/empty contributors/outside-or-missing, success Sample JSON matches. Original numerical block including15 retry is byte-identical, with hashes. |
| Relevant regression boundary | JS/Wasm-GC each pass4 new tests and2 existing stencil/polar tests. No15 extreme,13 consumer,12 laziness,14 variants or scientific/download reruns. |

Actual CLI/external module check/build/run pass both targets. Exact source,
API and actual JS/Wasm/core consumer artifacts are pinned.

NonFiniteResult labels the retained final numerical guard. Its JSON encoding
and source branch mapping are reviewed; no public-input runtime reproduction
is claimed. This does not manufacture a numerical failure or weaken15.
The new method is per station, not a batch/CSV-reason format. Existing raw CSV
cannot retroactively recover a cause after field execution context is lost.
No aggregate multi-cause diagnosis, imputation or memory/performance promise.
