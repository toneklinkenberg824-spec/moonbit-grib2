# Actual own-file inventory24 workflow

forecast.grib2 is the unchanged existing forecast09 four-field synthetic file,
not weather observation or a new scientific reference. Actual inventory.json
lists flat indices0..3; forecast states are omitted/missing,0,6,-6. Each grid is
2x3 and regional; source offsets are independently derived from original bytes.

Run the example using ../../examples/node-inventory24/README.md. The actual
consumer selected time6 from that JSON and passed emitted index2 to the old
unchanged file producer, yielding selected.csv and diagnostics.jsonl for the
matching stations.json. The2 records hold333 and a gap, with input1/outside-grid.
Inventory origin/product, actual selected CSV and original diagnostic agree.

later-unsupported.grib2 and later-truncated.grib2 are intentional failure
fixtures with a valid first field. The new command must report an explicit
decode error and empty stdout for each, not a partial inventory. Unsupported
declaration is not a claim that original5.3 packing is supported. VALIDATION.json
pins all actual files and expected outcomes. Full raw stdout/stderr, independent
raw expected catalog, source/build identities and failed research are in the
separate24 report. No old accepted suite was rerun or counted as this feature's
acceptance.
