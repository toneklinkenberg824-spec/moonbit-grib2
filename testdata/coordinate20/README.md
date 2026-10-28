# Actual numeric-coordinate consumer20 artifacts

These are actual matched files from one new20 input executed by the unchanged
frozen18 Node producer (reused via frozen19), followed by the repaired Python
consumer. regional.grib2 is the existing forecast09 first synthetic constant111
message with its bitmap gap, not observation or operational forecast data.

All IDs are ASCII. Coordinates include positive/negative integer2^53+1 as
finite longitudes, integer2^53+1 as an invalid latitude, and ordinary decimals.
The producer takes Double: at2^53 spacing is2, so the halfway integer rounds
to even2^53. CSV keeps that existing representation. Python retains the exact
original integer in station; the helper compares only in the producer's numeric
domain and never rewrites the original station object.

From the project root:

    python examples/node-file17/join_diagnostics.py testdata/coordinate20/stations.json testdata/coordinate20/result.csv testdata/coordinate20/diagnostics.jsonl

joined.expected.json is actual final stdout. Four joined records preserve the
original input, CSV and ordinals0/1/2/3; causes are outside-grid, outside-grid,
invalid-station, outside-grid. The report preserves the original false mismatch
failure and the final success plus two real coordinate-mismatch errors. Next
representable longitude and changed latitude remain rejected. VALIDATION.json
pins actual files and independent expectations. No19 encoding/Unicode,18
correlation or older scientific suite repeated; parser errors are not swallowed.

The helper still requires same-run original input, unreordered CSV and UTF8
diagnostics from successful production. This is not an arbitrary-precision
coordinate input mode or a producer precision fix.
