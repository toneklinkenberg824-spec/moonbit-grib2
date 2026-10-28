# Fixed provenance-bearing station CSV export

## Scenario and value
A script already uses typed layer/run/forecast-state selection and station
sampling, then needs one row per station/field for downstream ingestion.
Current nested JSON is complete, but every client must flatten it, distinguish
None from0 and quote labels independently. Add one core-only string formatter
for the existing FieldSamples results; no file IO or generic CSV parsing API.

## Ecosystem/source review
Installed moon search csv returned20 modules, including maria/csv_parser0.1.0,
sikadi123/moonbit-csv0.1.1 and moonbit-community/NyaCSV0.3.4. CSV parsing/writing
already exists; this is not a new generic serializer claim. Previous same-day
GRIB ecosystem review/upstream API is reused. Upstream wgrib2-style CLI exports
grid CSV; this feature is a fixed view of named, uniquely selected station
samples with raw product and contributor provenance. Preserve the existing
no-external-runtime-package contract with a small private quoting helper.
RFC4180 section2 supplies quoting/doubled-quotes/CRLF rules; charset isUTF-8.
https://www.rfc-editor.org/rfc/rfc4180

Alternative: structured query mismatch reports were considered, but current
unique/absent errors are actionable and the export is a complete pipeline end.
No extra formatter, parser or temporal feature is added alongside it.

## Contract
- station_results_csv(results) returns String. Header has11 columns:
  request_key,station_id,latitude,longitude,value,algorithm,message,field,
  byte_offset,product_json,contributors_json.
- One row for each Sample, preserving group then station order. Use each
  Sample's own product/origin, the group's key, original station coordinates,
  value and contributors. Product JSON retains existing None-key omission;
  contributors retain the current structured values/weights/source indices.
- Quote every CSV cell, double embedded quotes, preserve embedded CR/LF, use
  CRLF record endings and one final CRLF. No BOM or label transformation.
- None sample values are empty numeric cells; real0 is"0". Empty groups produce
  no rows, and no samples yields header only. Original FieldSamples unchanged;
  use nested output when selected-field identity with zero stations is needed.
- Intended input is the existing sampler's FieldSamples; no scientific
  recalculation, external storage, calendar/unit conversion or generic parsing.

## Acceptance
Check RFC escaping/empty dimensions/missing vs0/subnormal numeric round trip;
export actual NOAA/IFS licensed8x6 repacked5.0 fields through layer/run/three-state
selection and stations, compare serialized values with already captured SciPy
expectations, preserve spatial gaps and source origins. Both targets check/build,
new tests and runnable cmd/export plus independent workspace/Python csv+json
readback. Pin source/build/API and package every file with archive readback.
