# Alternating endpoint hypothesis: not established as a required repair

NOAA flag3.4 defines alternating traversal and direction of its first row/column.
Template3.0 calls La2/Lo2 the last gridpoint, but that wording alone does not
resolve the opposite-corner convention used by producers and geometry libraries.
NOAA's wgrib2 scan documentation describes the plow order; its new_grid workaround
changes data order/scan flag without prescribing endpoint-header edits.
The current NOAA-EMC wgrib2 geo.c regular2ll derives domain edges using La1/La2,
Lo1/Lo2 and increment-validity/alternation checks rather than blindly selecting
the last data-array coordinate. These sources do not justify replacing our
accepted corner convention and rejecting historical supported fixtures.

No reader or prior fixture changed. This is a bounded negative finding, not a
claim that every producer convention is settled. A future investigation should
start with an independently produced rectangular3.0 alternating message whose
header/endpoints and intended geometry are both documented. No field download
or existing16-scan suite rerun was needed for this unchanged path.

Sources checked2026-10-28:
- https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_table3-4.shtml
- https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/scan.html
- https://www.cpc.ncep.noaa.gov/products/tools/wgrib2/new_grid.html
- https://raw.githubusercontent.com/NOAA-EMC/wgrib2/develop/src/geo.c

## Confirmed numeric issue
Exact Fraction sums show that scaling a subnormal value by fractional weights
before summing loses increments unnecessarily. Bilinear and polar fixtures
reproduce nine failures out of12; a power-of-two headroom shift for all-subnormal
stencils preserves those finite results. Normal stencils retain prior arithmetic.
