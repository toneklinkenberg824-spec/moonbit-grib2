# Actual strict JSON downstream consumer25 artifacts

These are three real matching file sets produced by the unchanged Node binary
before the Python-only serialization repair. regional.grib2 is the existing
synthetic constant111 regional message, not observation or a new scientific
reference. Sidecar metadata is application data; station coordinates are
ordinary finite values and IDs are ASCII. The original sidecars use valid
numeric tokens1e400/-1e400, nested objects and a quoted Unicode/emoji label.

Run the optional helper from the project root with stations.json, result.csv
and diagnostics.jsonl in this directory. joined.expected.json is actual final
stdout, accepted by Node JSON.parse and a strict Decimal JSON reader. It keeps
original numeric tokens/types and indices0/1 rather than Infinity/null/strings.

The finite-* set uses ordinary finite sidecar values; its final stdout is
byte-identical to frozen-before helper output. The sparse-* set inserts an
available station1 between failures0/2, verifying source-fragment lookup uses
original input positions. Expected output remains ASCII-safe while preserving
the original Unicode label and original CSV/cause/index metadata.

The separate25 report retains the original producer0/helper0/strict-Node1
failure, all commands and raw logs, exact Decimal oracles, source/runtime and
reused compiled identities. No failed original was changed/deleted, no old
accepted suite rerun. VALIDATION.json pins all matching files. The CLI preserves
valid JSON representation; it does not add arbitrary-precision arithmetic or
change join() in-memory Python numeric semantics. Inputs must remain matched
and stable. Existing strict CSV/JSON errors and inventory24 stay intact.
