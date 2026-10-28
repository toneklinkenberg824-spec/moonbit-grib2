# Round14 finite review closure

One hypothesis was investigated: alternating scan traversal endpoint versus
opposite rectangular corner in header validation. No new feature was proposed.

| Question | Evidence / disposition |
|---|---|
| Can the two locations differ mathematically? | Independent dimensions/orientation examples in REFERENCE.json: row-even3x2 and column-even2x3. Their proposed final traversal coordinates differ from the opposite corner. |
| What does the current product do? | New report-local observer check/run succeeds on JS/Wasm-GC. Both header variants return InvalidGrid at the last-coordinate check, before selection/sampling/export. This is diagnostic behavior, not positive format acceptance. |
| Is this a reproduced valid-input bug? | Not confirmed. Primary sources and inspected implementations did not establish the conformity premise. The ECMWF iterator assumes non-alternating rows; NOAA contains ambiguity handling. PRIMARY-REVIEW.md states the bounded inference. |
| What changed? | Only delivery/review documentation and evidence records. All existing MoonBit sources, configuration and API hashes remain identical. No old test,13 consumer or scientific/download chain was repeated; no new product unit tests. |

The new observer is solely a report-local diagnostic, not a delivered decoder
extension or actual CSV export acceptance. Fresh JS/Wasm observer binaries and
the compiled library graph are pinned under probe-workspace/_build.
Earlier successful product/consumer validations remain historical evidence.

Unconfirmed question is retained for future authoritative samples or explicit
normative clarification, without required implementation work in this finite
audit. No permission to widen the scope, no release/publication/submission.
