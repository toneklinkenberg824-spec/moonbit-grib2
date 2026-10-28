# Actual Unicode JSONL consumer19 artifacts

These matched files were produced by the unchanged frozen18 Node executable
for one new19 input, then read by the final repaired optional Python consumer.
They are executed artifacts, not a replacement for an unrun workflow.

regional.grib2 is the first existing forecast09 synthetic constant111 message,
with its bitmap gap; it is not weather observation or an operational forecast.
All three stations are outside its regional extent. IDs contain U+0085,
U+2028 and U+2029. diagnostics.jsonl has three LF-delimited UTF8 JSON objects;
the literal Unicode separators inside strings are not JSONL record boundaries.
CSV preserves every ID. The original input ordinals0/1/2 and outside-grid
causes identify the matching logical data records after the CSV header.

From the project root:

    python examples/node-file17/join_diagnostics.py testdata/jsonl19/stations.json testdata/jsonl19/result.csv testdata/jsonl19/diagnostics.jsonl

joined.expected.json is the actual final stdout captured through the default
Windows GBK pipe. ASCII JSON Unicode escapes preserve the original decoded
string values. The output also matches the UTF8/CRLF-boundary check. Truncated
JSON remains rejected. VALIDATION.json pins these actual files and outcomes;
the separate19 report retains before failures, all commands and source/build
identity. The optional helper requires matching original, unreordered files
from a successful producer run. No18/17 suite or scientific reference rerun.

Framing references: Python str.splitlines documentation
(https://docs.python.org/3/library/stdtypes.html#str.splitlines) and the NDJSON
specification (https://github.com/ndjson/ndjson-spec). Standard JSON and CSV
parsers are reused; no new parser/format or novelty claim.
