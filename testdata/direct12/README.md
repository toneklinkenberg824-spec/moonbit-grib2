# Direct sampling into CSV records
Resolve all requests before returning records, then sample the current station
on next(). Input fields and station lists stay prepared. Prefix counts and
source control-flow review do not measure allocations, RSS or latency.
cmd/direct equals ../export10/NOAA-IFS-stations.csv. Data attribution remains
in ../export10/LICENSES.md and ../SOURCES.json. Licensed repacked5.0 fixtures
and scientific goldens are unchanged. Synthetic tests reuse forecast09 data.
Raw logs, external workspace pins and ecosystem receipts are in the12 report.
