# Direct requested-field sampling into CSV records

## Need and bounded ecosystem review
A preview/download client wants the header and first station without first
allocating a Sample for every station of every selected field. The existing
station_csv_records API only defers serialization of already materialized
FieldSamples. This is a documented workflow gap, not a correctness bug.
Same-day registry CSV research and the NyaCSV public API receipt are reused with
hashes. Generic CSV encoding and iteration already exist; this extension ties
this library's unique field resolution and provenance-bearing sample schema to
on-demand station sampling. No ecosystem code or runtime dependency is imported.

## Contract and compatibility
- sample_requested_csv_records(fields,requests,stations) returns
  Result[Iter[String],GribError]. Resolve ALL named queries at factory creation;
  empty/duplicate keys, absent/ambiguous fields and malformed query references
  fail before an iterator/output is returned, including with zero stations.
- Snapshot selected field references and request keys, preserving the old
  per-request error precedence. Caller may replace request/field array entries
  after creation; selected identities stay stable. Keep stations unchanged while
  consuming. No asynchronous IO or input-stream parser is added.
- First next() yields only the existing CSV header. Each later next() samples
  exactly its next requested station and serializes one complete CRLF record.
  Request-major/station-minor order, missing data, raw product metadata and
  contributors equal sample_requested_fields -> station_results_csv.
- Empty requests/stations produce header only. Separate factory states are
  independent; exhaustion remains fused; consumers may stop after any item.
- Existing public signatures, error messages/precedence and11-column CSV bytes
  remain. A shared private request resolver prevents selection rules drifting.

## Memory statement
Decoded fields, GRIB input and station list remain materialized. Additional
retained selection state is one key/field pair per request; sampling and CSV
buffers are created for the current record only. A polar sample may contain a
whole row of contributors, so even one record can be large. No whole-pipeline
streaming, constant-memory, GC/RSS, speed or latency guarantee is claimed.

## Acceptance
Demonstrate the old10000-Sample eager boundary before editing. New tests compare
full synthetic output to the existing materialized pipeline, cover missing/0/
positive/negative forecast identity, multiline Unicode labels, early selection
errors, snapshot behavior, empty input, exhaustion and independent prefix use.
Consume only header+one station from10000 prepared stations, without creating
FieldSamples or collecting later CSV records. Verify source control flow rather
than treating length or runtime as an allocation measurement. Check old request
workflow regressions after resolver extraction. Both JS/Wasm-GC must pass relevant
checks/builds/tests, actual NOAA/IFS cmd/direct bytes must equal frozen export10,
and independent workspace/Python csv+json consumers must accept prefix and full
records. Preserve old reports, pin source/API/builds and read back every ZIP file.
