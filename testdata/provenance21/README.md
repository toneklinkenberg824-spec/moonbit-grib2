# Actual large-provenance CSV consumer21 artifacts

One new supported3.0/4.0/5.0 synthetic constant111 field has1440 columns at
0.25-degree longitude spacing, two latitude rows90/89 and bitmap255. Its
zero-bit constant/product sections reuse the existing forecast09 fixture.
GRID-CONSTRUCTION.json records the exact generated geometry and source hashes.
This is a file-consumer example, not observation or operational forecast data.

The unchanged frozen18 Node executable, preserved through20, produced the
matching actual files once. The available pole row contains all1440 source
contributors in one164381-character JSON CSV cell. The next station is outside
the grid and gets its existing empty-value row plus input index1 diagnostic.
The old Python default field limit131072 rejects the otherwise valid file.
PowerShell Import-Csv/ConvertFrom-Json independently reads the full provenance;
its receipt is included. No provenance was shortened to make parsing succeed.

From the project root:

    python examples/node-file17/join_diagnostics.py testdata/provenance21/stations.json testdata/provenance21/result.csv testdata/provenance21/diagnostics.jsonl

joined.expected.json is actual final CLI stdout: only input1/outside-grid is
returned, with its original station and logical CSV record. The consumer must
still read the available row's complete large cell first. VALIDATION.json pins
all matched files and results. The separate21 report retains before failure,
independent parser logs, strict malformed CSV/limit-restoration probes and
source/runtime/reused compiled identities. No20/19/18 or older suite rerun.

The helper uses the current UTF8 file's byte count as a temporary CSV field
bound and restores the prior csv module limit in finally. It still materialises
the full local CSV; no new encoding, general concurrent parser isolation,
streaming, arbitrary-size memory or performance guarantee is provided. Parser
errors, original IDs/integers/causes/indices and existing format remain.
