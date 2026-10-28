# Lazy station CSV record view

## Need and ecosystem difference
A client with thousands of selected station samples wants to write or preview
records without building another full CSV String. Round10's fixed schema and
metadata/provenance are suitable; keep them exactly. Same-day registry CSV
research is reused. moonbit-community/NyaCSV public API is additionally inspected
for generic CSV capabilities; no novelty claim for iteration or CSV encoding.
This API is a lazy view of this library's named station results and11-column
schema, not a generic parser/writer or replacement for ecosystem CSV packages.
Preserve the existing core-only runtime dependency contract.

## Contract
- station_csv_records(results) returns Iter[String]. First item is the current
  header, followed by one complete quoted CSV record per Sample in group/station
  order; each item endsCRLF and may contain quoted internal CR/LF.
- CSV records serialize on next(). Do not prebuild the complete CSV string.
  Existing FieldSamples input arrays stay materialized and must remain unchanged
  while the iterator is consumed. Additional serialization buffers are per
  record; no whole-pipeline memory/RSS or performance guarantee is claimed.
- Skip empty groups, return one header even for no samples, remain exhausted,
  and maintain independent state for separately created iterators. Early stop
  is allowed. A fresh factory call starts a fresh iterator.
- station_results_csv keeps its exact signature/output. Share its private header
  and row formatting with the iterator to prevent schema/escaping drift.
- No storage/network/async IO, no CSV parser, no scientific or selector change.

## Acceptance
Independent readers verify multiline records and fixed11 columns. Concatenation
equals current full CSV on Unicode/missing and real licensed NOAA/IFS data; old10
CSV contract cases still pass. Test empty groups, exhaustion, interleaved
independent iterators and prefix/full traversal of a10000-station batch without
collecting serialized output. Record measured count/maximum record string units
with no RSS/latency claim. Provide cmd/stream and independent workspace/Python
streaming CSV+JSON readback on JS/Wasm-GC. Reuse old download/scientific goldens,
pin API/source/builds and preserve old reports/ZIPs.
