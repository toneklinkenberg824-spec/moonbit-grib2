# Round17 self-owned file-to-CSV host example

## Scenario, gap and ecosystem
Existing examples embed bytes; the README delegates byte acquisition to a
host. A user with a supported GRIB file and station JSON array must currently
write that host glue. Add a small independent example module. moonbitlang/x/fs
already supplies generic file reading; official MoonBit/Node docs establish
host ABI and local filesystem APIs. No filesystem/parser novelty is claimed
and no third-party implementation/dependency is imported.

## Contract and compatibility
- examples/node-file17 is an independent Node/JavaScript executable using
  installed core JSON parsing plus the existing GRIB2 public API. Node22.3+
  required; actual host24.11.0. It is not a browser/Wasm filesystem program.
  Main library/API/dependencies and previous examples remain byte-identical.
- Args: GRIB_PATH STATIONS_JSON OUTPUT_CSV FIELD_INDEX. Explicit zero-based
  field index selects one decoded field, with identity/product in success
  summary. All input fields still pass read_fields validation; no unsupported
  field is silently skipped or new templates/grids accepted.
- Station JSON is the existing id/latitude/longitude representation in an array.
  UTF8 with optional leading BOM. Parse/validate the complete table and selected
  field before writing. Invalid geographic coordinates retain legacy missing
  rows and typed stderr diagnostics; malformed JSON/schema, bad field index,
  decode or host-read errors fail before CSV creation.
- Emit the existing11-column CSV with all station rows/order, original product/
  origin/contributors, UTF8 and CRLF. Use the same typed sampler; available
  samples are reused. For failed stations call the legacy wrapper to retain its
  exact representation (failure checks repeated, no whole-pipeline speed claim).
- Output is exclusive-create. Existing file is an error and stays unchanged.
  No overwrite flag or user approval loop, no upload/network service added.
  IO errors remain host errors; no crash/disk-full atomicity guarantee.

## Acceptance
Compile/check the actual independent module against unchanged local sources.
Run8 new filesystem cases: two explicit real-file field selections, empty
station table, malformed station schema, invalid field index, corrupted GRIB,
missing input file and existing-output sentinel. Read actual output file bytes
with strict Python CSV/JSON, including Unicode/spaces in paths, Unicode/multiline
IDs and BOM station input. Reuse archived real point expectations, not a new
scientific/download run. Invalid-input cases create no CSV and existing output
readback remains exact. Pin all input bytes and actual JS executable/core files.
No root unit test,16 routing suite,15 extreme,13 parser,12 laziness or14 variants
rerun. One clean relevant file-boundary verification then docs/ZIP/pins.

Inputs, decoded grid, station list, samples and full CSV remain materialized.
No new format, async/backpressure/RSS/latency/whole-input-streaming guarantee.
