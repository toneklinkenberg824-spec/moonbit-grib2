# Round12 bounded workflow closure

No existing correctness bug was established. One authorised extension closes
the gap between validated field selection and lazy station CSV consumption.

| Uncovered need | Closure and actual evidence |
|---|---|
| Preview requires sampling every station first | Pre-edit JS control materializes10000 samples before a two-record prefix. New factory has its only sample call inside data next(), after the header return. Both targets consume header+one station from10000 prepared stations, intentionally leaving later records unconsumed. Source/functional evidence, not measured allocations. |
| Selection failure must precede export | All requests resolved at factory creation. Empty/duplicate names, missing/ambiguous fields, malformed reference time and earlier-error precedence pass with zero/nonzero stations. Seven existing request contracts pass after private resolver extraction. |
| Selected identities and CSV compatibility | Captured keys/fields survive replacement of original arrays. Empty input, fused exhaustion and independent iterators pass. Synthetic12-row output equals the old materialized pipeline; Python strict CSV reads actual complete-record iterators, multiline Unicode and JSON metadata/contributors. Real8-row cmd/direct equals frozen10 CSV bytes on both targets. Independent public-API workspaces read full and prefix outputs. |

JS/Wasm-GC each pass11 final relevant tests:4 new and7 affected existing.
The old boundary control is a separate pre-edit1-test JS observation.
All pre-existing public function signatures and CSV schema remain.
Only field_requests.mbt and station_csv.mbt changed among old implementation
files. Decoder, sampler, fixtures and unchanged full test/download sets were
not rerun.

Same-day CSV registry and NyaCSV API evidence is reused read-only with hashes.
No novelty claim for CSV or iteration, no ecosystem code/dependency imported.
Value is deferred sampling with this library's validated selection/provenance.

GRIB input, decoded fields and station lists remain prepared. Selection state
scales with requests, and one polar record can contain a whole contributor row.
Keep stations unchanged during consumption. Whole-input streaming, constant
memory, GC/RSS, speed and latency remain outside this extension.
