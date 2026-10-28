# Bounded audit06: promises and evidence

| Current promise | Review/evidence | Outcome |
|---|---|---|
| Basic-angle3.0 geometry, exact valid nodes | Independently encode default1e-6,1e-9 and1/4e9-degree steps; integer angular ticks/Fraction oracle; all9 node round trips including reversed scan | F01 reproduced and fixed |
| Closed BBox node extraction, zero-width meridian | Exact node boxes, multi-row closed east edge, empty sub-cell intervals and dateline | F02 reproduced and fixed |
| No extrapolation/positive-weight missing | Near-boundary outside queries, isolated southeast valid node, missing neighbour, fine-grid inverse coordinates beyond Int32 | New cases pass; no nearest-node tolerance widening |
| Periodic seams/huge finite longitude/poles |11 related regressions: duplicate seam/masks/vector policy, basic-angle dateline, independent SciPy/provenance, JSON missing, scalar polar continuity, prior05 interior-node and longitude fixes | Retested only affected sampling/crop paths |
|0–32-bit scale/header/bitmap/selection/state semantics | Current reader/headers/types/vendor code inspected; hashes identical to verified05. Reuse05 exact Fraction, scan/mask, time-unit/budget and external isolation evidence | No decoder/API edits; no repeat of unchanged74-case set or24-field download suite |

Primary source: NOAA template3.0 note1 explicitly defines angular unit as basic-angle/subdivisions and permits units other than1e-6. https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_temp3-0.shtml . Regressions use independent integer geometry and API invariants, not product-generated numeric truth.

Investigation stopped after identifying these two related domain-boundary causes and their in-scope consequences. No template expansion, speculative refactor, global SDK change, remote publication or old report/ZIP edits.
