# Round17 actual file-host workflow closure

No library defect was claimed. Existing examples embed GRIB bytes; this
standalone host module connects actual input files and explicit field selection
to existing sampling/CSV without changing library source/API/dependencies.

| Acceptance | Actual file evidence |
|---|---|
| Self-owned supported GRIB and station file | Mixed licensed NOAA/IFS repacked5.0 bytes read from a Unicode/space path; UTF8 BOM station JSON read with multiline identifiers. Explicit indices0/1 select correct message/product/offset. Archived values verify read/select/write integrity, not a new scientific run. |
| Existing CSV behavior | Two success outputs each retain3 stations (1 finite,1 outside,1 invalid). Python strictly reads actual UTF8/CRLF files, original11 cells, labels, product JSON, offsets and contributors. Empty table produces header-only output with identity in success summary. |
| Error boundary before output | Malformed station schema, invalid field index, corrupted GRIB and absent input each fail with no CSV created. Corrupt input is not skipped merely because selected index0 would precede it; complete read_fields validation remains. |
| Existing output protection | Exclusive-create rejects the sentinel path. Readback equals its exact original bytes. No overwrite option or global approval loop. |
| Actual standalone consumer | New module info/fmt/check/build passes with fixed SDK; runs through both moon run and the actual compiled Node executable.8 fresh filesystem cases pass. Node24.11.0 tested, Node22.3+ documented. |

All prior MoonBit implementation/config/API hashes remain byte-identical.
No previous root test,16 cause routing,15 numerical suite,13 parser,12 lazy or14
metadata variant was rerun. New actual JS/core outputs are pinned under the
report external-workspace/_build; this is not a Wasm filesystem implementation.

Generic filesystem support already exists in moonbitlang/x; official FFI/Node
docs underpin the small host binding. No third-party implementation, dependency,
filesystem/parser novelty or registry compatibility claim. The valuable gap
closed is a ready own-file workflow retaining legacy rows and typed stderr causes.

The application fully materializes input, decoded fields, stations, samples
and CSV. It does not provide network/async IO, crash/disk-full transactional
writes or memory/performance bounds. NonFiniteResult remains the existing
unreproduced guard, not a new numeric defect. Original GRIB support limits stay.
