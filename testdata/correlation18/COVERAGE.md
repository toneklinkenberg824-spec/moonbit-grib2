# Round18 diagnostic locator closure

This is a small integration improvement, not a claimed numerical/format bug.
IDs were already allowed to be duplicate or empty. Old diagnostics can be
joined through missing CSV row order; the new ordinal makes direct input
selection possible without reconstructing that positional missing-row join.

| Acceptance | Actual evidence |
|---|---|
| Concrete standalone retry need | Read-only frozen17 binary ran only the new18 mixed input:5 stations/4 failures, two identical outside events, and ID lookup would include available row0. BEFORE-OBSERVATION.json explicitly retains the older positional workaround. |
| Correct original index, not failure index | Mixed available/failing duplicate+empty IDs yield indices1,2,3,4. Actual consumer joins station/coordinates/CSV logical data record and selects outside retry indices1,3, never available duplicate0. |
| Legal identifiers stay accepted | All-available duplicate/empty IDs produce3 CSV rows and no diagnostics/joined failures. No new identity validation. |
| Logical records, not physical lines | All-failing duplicate ASCII IDs contain embedded newlines; the actual CSV has more physical lines than records, but indices0,1,2 join correctly. This is a new correlation scenario, not17's Unicode/BOM suite. |
| Compatibility | Mixed CSV exactly equals the frozen17 baseline bytes. Projecting away station_index leaves the old diagnostics unchanged; success summary values except the output filename remain equal. Only sample-phase diagnostics gain the key. |
| Actual consumer boundary |3 actual Node producer +3 Python CLI consumer scenarios pass. The helper also rejects the actual pre-change log with missing station_index rather than guessing by ID. |

Main library/config/API remain byte-identical. Only the existing Node example
main changes among old MoonBit files, plus a new optional standard-library
Python consumer. Actual Node JS/core artifacts and interpreter/source identity
are pinned. No root unit test or17 Unicode/BOM/no-clobber,16 routing,15 numeric
or earlier scientific/download suites repeated.

station_index is zero-based within one invocation's original station array and
addresses the corresponding logical CSV data row after the header. It is not
a global station ID or physical file line. The helper requires matched,
unreordered files and a successful run's UTF8 diagnostics. Strict existing
diagnostic schemas need to allow the additive JSON key; old fields remain.
No new CSV column, format/grid, IO durability/streaming/performance promise.
