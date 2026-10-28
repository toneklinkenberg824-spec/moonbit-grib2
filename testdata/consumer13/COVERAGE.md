# Round13 bounded downstream closure

No GRIB2 correctness defect was found. Actual ecosystem consumption was missing
from the existing Python-only readback evidence; one standalone application
example closes that integration gap without extending the library API.

| Hypothesis / scenario | Actual acceptance |
|---|---|
| MoonBit parser may interpret multiline/Unicode records differently | NyaCSV pre-Int32 fixed source parses original producer records one at a time. New quoted CRLF/Chinese/emoji/whitespace labels, leading-zero and empty identifiers survive raw11-cell readback on JS/Wasm-GC. Header schema and one parsed row are checked before use. |
| Empty numbers and nested metadata need explicit application conversion | Independent Python verifies9 application JSON rows per target:4 real NOAA/IFS rows,4 numeric synthetic rows and1 preview row. Empty numeric -> null versus numeric0, missing forecast key versus exact0, parsed products/contributors and weights all pass. A synthetic R=0 fixture is independently derived from forecast09; not a new scientific reference run. |
| Preview/header-only output must be consumable by this parser | Consumer limits before requesting another data record. One-row preview matches the first real application row, and header-only consumes0. These are new parser/application acceptance cases, not12's lazy-sampling or frozen-CSV equality tests. |

Current NyaCSV0.3.4 source fails this fixed SDK because Int32 is undefined.
The immediately preceding pre-Int32 source fe4448e1e45a25f6fca151320c766519e80162c9
declares0.3.3 and is bound through a local workspace, without changing global SDK,
registry, upstream parser implementation or GRIB2 dependencies. Registry
installation is not claimed. Failed probes and exact source/license pins remain.

All pre-existing MoonBit source/config/API hashes are identical. The new module
is independent; root tests and unchanged12 acceptance/download checks were not
rerun. Relevant consumer check/build/run passed once on each target after setup.
Actual JS/Wasm binaries and dependency cores are pinned in final-workspace/_build.

The consumer accepts trusted complete producer records, not arbitrary byte
fragments or untrusted CSV. NyaCSV has no public Result/error-return parser.
Per-record parsing still materializes the current header+row and parsed cells;
input grids/stations and potentially wide polar provenance remain prepared.
No constant-memory/RSS/latency/whole-input-streaming claim, IO or parser rewrite.
