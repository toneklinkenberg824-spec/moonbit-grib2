# Round13 actual MoonBit CSV downstream example

## Need and ecosystem difference
Existing provenance CSV tests use Python downstream readers. A MoonBit
application needs a runnable, pinned consumer that preserves identifier text,
reads empty numeric values differently from0 and decodes the nested product/
contributor JSON. NyaCSV already provides general CSV parsing, multiline
quoted fields and trim_spaces=false; its public interface and source were
reviewed at current commit19ab9ca861f13a0663dc6e168b764507fa0e76ba. Its Int32 source cannot compile under the fixed SDK. The preceding pre-Int32 commit fe4448e1e45a25f6fca151320c766519e80162c9 declares0.3.3 and passes a multiline Unicode probe; lock this source without editing upstream.
No new generic CSV parser or GRIB2 public API is needed. Deliver a standalone
example module using this existing package and core JSON/number parsers.

## Contract and compatibility
- New examples/nyacsv13 module depends on NyaCSV source declaring0.3.3 at the fixed compatible commit and this local
  library, bound by a report-local moon.work. The main library's core-only
  dependency contract, all existing sources/signatures and prior examples stay
  byte-identical. A fixed GitHub workspace supplies the parser; no registry install is claimed and no global registry/SDK updated.
- Consume sample_requested_csv_records output, taking its first item as the
  fixed11-column header. Pass header+one complete logical data record to
  CSV::parse_string with explicit multiline=true and trim_spaces=false.
  Check header/schema and exactly one data row before using cells. Do not split
  records by physical newline or use CSV::to_string as a lossless byte writer.
- The input is trusted producer records, not arbitrary fragmented/untrusted
  CSV. NyaCSV's public parser has no Result/error return; this example is not a
  strict general CSV validator. Host IO, UTF8 transport and framing stay outside.
- Retain request/station strings including whitespace, commas, quotes, CR/LF,
  emoji, leading zeros and empty identifiers. Empty value -> JSON null;
  nonempty numeric value -> parsed Double. Parse product/contributor JSON with
  the core parser. Output one application JSON object per consumed record.
- Support an explicit maximum consumed-data-record count checked before
  requesting the next item. A preview consumes one row; header-only input
  consumes none. Do not repeat12's sampling laziness or frozen-byte checks.

## Acceptance and limits
Run check/build/run on JS/Wasm-GC for the actual isolated module. Independently
verify emitted semantic rows for licensed NOAA/IFS inputs with new labels and
two station locations: expected4 rows,2 numeric values and2 domain gaps.
Use an explicitly synthetic0-reference-value fixture derived from forecast09
to distinguish None from numeric0 and missing forecast from exact0. Verify
one-row preview and header-only consumption and parse nested metadata/weights.
No root test rerun: root implementation/API/dependencies are unchanged, proven
by source hashes and moon info/fmt/API identity. Check and pin the exact workspace source, license and compilation artifacts. Retain the current0.3.4 compile failure.

Record-wise application parsing avoids collecting an entire CSV/parsed table,
but input grids/stations remain prepared, one record can be large, and the
example prints serial application output. No arbitrary-byte streaming parser,
constant memory, RSS, latency or speed guarantee. Preserve prior archives,
update accurate README/PROPOSAL, package and read back every file once.
