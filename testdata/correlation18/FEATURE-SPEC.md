# Round18 explicit station locator for downstream retry

## Established need and existing capability
Station IDs may be duplicated or empty. The new baseline has5 stations,
including one available duplicate and4 failures. Two outside diagnostics are
identical and ID matching also selects the available row. Consumers can already
join diagnostics to missing CSV records by order; do not claim correlation is
impossible or a sampling bug. The small usability need is directly locating
the original input station without reconstructing missing-record ordering.

## Ecosystem difference
NyaCSV separates headers from Array data rows; MoonMissingness already exposes
complete-case and row-index operations. Row addressing/CSV/nullable-table
processing are established concepts. Add only the producer's input ordinal
and a tiny standard-library CSV consumer example, not a new parsing/batching
framework, package or public GRIB2 API. Public API receipts are pinned.

## Contract and compatibility
- Add station_index (zero-based original station-array index) only to Node file
  adapter phase=sample stderr diagnostics. It counts available rows too.
- It addresses CSV logical data record index, excluding the header; it is not
  a physical file line. Preserve ID exactly, including duplicates/empty IDs.
- Existing phase/station_id/code values, output summary, CSV bytes/column schema,
  selection/decode failures and all library APIs/causes remain unchanged.
  This adds a JSON key; strict diagnostic-schema consumers must allow it.
- Provide join_diagnostics.py STATIONS_JSON OUTPUT_CSV STDERR_JSONL as an
  optional standalone consumer. It joins each failure to original station and
  actual CSV data record using station_index, checking correspondence and
  completeness, and outputs those records for application retry filtering.
  Requires matching input/output plus UTF8 diagnostics from a successful run.
- Old logs without the locator remain readable by custom positional joins;
  this helper deliberately does not guess and reports missing station_index.

## Acceptance
Execute actual changed Node program and actual Python CSV consumer on3 new
cases: interleaved available/failing duplicate+empty IDs; all-available duplicate
IDs; all-failing duplicate multiline ASCII IDs. Verify exact index->station->
CSV record join, reasons, original IDs/order and unchanged CSV bytes against
the frozen17 executable for the mixed case. Check legacy-log helper error.
No17 Unicode/BOM/no-clobber,16 routing or old numeric/scientific cases rerun.
Pin all source/binaries and actual file readbacks, then docs/ZIP readback once.

Only Node/JS adapter metadata and optional Python consumer change. Main library
source/API, existing cause contracts and IO/no-streaming/no-transaction limits
remain. No new data formats/grids, input restrictions, global SDK/dependency or
performance claims. This is an integration improvement, not a defect score.
