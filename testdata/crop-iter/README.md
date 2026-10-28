# Pull-based regional node extraction fixtures

These are synthetic contract fixtures, not observations or forecasts. regions.grib2
contains three messages: a copy of this project's bitmap.grib2 with longitudes
changed to 359,0,1; a closed global 5-column grid derived from outcome16/regional.grib2
with hand-set 8-bit integer values and equal duplicate endpoints; and the unchanged
scan240.grib2 (column-major, reversed directions, alternating columns, bitmap gaps).
Original sample provenance and licenses remain in testdata/LICENSES.md.

EXPECTED.json lists hand-written canonical nodes and original scan identities.
Bounding-box membership is listed explicitly, rather than calculated with the
product's predicate. Values 0 and 9999 remain valid; missing cells remain nodes
with null values; polar rows contain raw values without scalar interpolation.

large-prefix.grib2 is a 179-byte synthetic zero-bit constant field with 1024x1024
decoded points (value7), derived from the same project constant fixture. Only two
nodes are pulled from it. This proves the public early-stop consumer path runs;
it is not a throughput or constant-total-memory benchmark. Decoding remains eager.
