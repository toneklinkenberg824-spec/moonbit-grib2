# Actual NaN-coordinate identity consumer26 artifacts

regional.grib2 is the existing synthetic constant111 field, not weather or a
new scientific reference. The unchanged producer accepts special Double JSON
strings per the installed SDK: original input0 has NaN latitude, input1 NaN
longitude, input2 ordinary outside-grid coordinates. All3 original rows remain;
causes are invalid-station, invalid-station, outside-grid. The old helper falsely
rejected the matching NaN row. joined.expected.json is final actual CLI stdout.

From the project root:

    python examples/node-file17/join_diagnostics.py testdata/nan26/stations.json testdata/nan26/result.csv testdata/nan26/diagnostics.jsonl

The output preserves original coordinate strings/types, IDs and all CSV cells.
It matches two NaNs only for record identity; no NaN sample becomes valid.
control-* uses ordinary finite and Infinity-string rows, with final stdout
byte-identical to the frozen helper. wrong-kind.csv deliberately changes a NaN
CSV coordinate to Infinity while leaving original input untouched; it must fail
with coordinate mismatch, proving NaN is not a wildcard.

VALIDATION.json pins actual matching artifacts and3 final cases. The separate26
report retains old failure, independent Node readers, source/cache/runtime/reused
compiled identities and repair diff.25 serialization helpers/main are untouched
and their old3 cases are not rerun. No new format, precision or performance
capability; original invalid-station policy and strict errors remain.
