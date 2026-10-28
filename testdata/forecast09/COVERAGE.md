# Round09 bounded workflow review and outcome

| Hypothesis/use case | Evidence | Result |
|---|---|---|
| Encoded missing forecast cannot be requested explicitly by08 constructor |Four otherwise identical manually encoded4.0 fields(all-one/0/6/sign-magnitude-6); before JS control shows wildcard ambiguity and exact0=second message |Stated capability gap confirmed, not a newly invented08 bug |
| Query refinement preserves layer/run and original query |New tagged criterion getter/builder; missing→exact0→any; unchanged original, wrong unit/layer no-match controls |Pass both targets; original constructor signatures and semantics preserved |
| Missing-only unique/all-or-error batch |Absent and duplicate missing cases; ambiguous wildcard request in batch |Pass; no pick-first fallback or implicit missing→zero |
| Real downstream identity/Unicode |Both old/new examples and independent workspace consumer; JSON parsing, message offsets, nodes3/4 at0.5, quoted/newline Chinese labels |Pass both targets; Product None key omission and Sample.value null remain distinct |

No new implementation correctness defect was confirmed in these bounded paths.
This round closes the explicit missing-filter limitation through an authorised
small feature.4 new feature tests +1 old-API capability control +7 affected08
workflow tests =12 per target. Reader, numeric decoder, sampler and old data are
byte-identical to08; old numeric/scan/full24-field/download checks are not rerun.

Research: same-day08 Mooncakes/upstream snapshot reused with hashes; current
cfgrib metadata-filter source search pinned1d11c7b919e9e87ebae50282fec62da441a1f76b
(abc.py,xarray_store.py,xarray_plugin.py) supplies the generic dictionary-filter
precedent. WMO92.1.4/5 supplies missing/sign-magnitude semantics. No claim of
first-ever filtering or exhaustive ecosystem absence. See FEATURE-SPEC.md and
REUSED-ECOSYSTEM.json for scenario, alternatives, compatibility and boundaries.
