# Diagnostic/input/CSV correlation18
These are actual matching artifacts from the new mixed-ID scenario, not a
synthetic stand-in for an unexecuted consumer. regional.grib2 is the existing
forecast09 first synthetic constant111 message (not weather observation data).
stations.json permits duplicate and empty IDs. New station_index resolves
failures to input/data records1,2,3,4; outside retry is1,3, not valid duplicate0.
Run the optional examples/node-file17/join_diagnostics.py with stations.json,
result.csv and diagnostics.jsonl. joined.expected.json is the actual readback.
CSV is byte-identical to the frozen17 baseline for this new18 input. Root API
and sampling code are unchanged. Full logs, before observation, actual JS graph
and interpreter/source identities are in the separate18 report.
