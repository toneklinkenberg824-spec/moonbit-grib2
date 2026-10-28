# Explicit three-state forecast matching

## Scenario and bounded finding
One parameter/layer/run can include a reserved missing forecast, analysis0,
forecast6 and a negative lead. Round08 correctly documents forecast_time=None
as wildcard, so a client cannot request missing-only through that API. This is
a real supported-input workflow gap, not an undocumented08 correctness defect.
Users currently need an extra manual scan after decoding. Existing unique-match
rejection remains correct and must not become pick-first.

## Selected small extension
Add ForecastTimeFilter with AnyTime, MissingTime and ExactTime(Int), and a copied
query builder with_forecast_time_filter. Keep FieldQuery.new's exact signature
and semantics. The forecast_time_filter() accessor records the full criterion;
legacy forecast_time stays Some(v) forExactTime(v),None otherwise. The builder
does not mutate the original query and preserves all layer/run/centre filters.
Named batches, metadata and spatial missing policies keep their08 contract.

## Ecosystem and alternatives
The same-day08 Mooncakes grib/weather logs and upstream API snapshot are reused
read-only: no registry GRIB module found in that bounded search; adjacent weather
packages cover aviation text, calculations, API queries and flight planning.
No ecosystem-wide absence or originality claim. ECMWF cfgrib provides dictionary
metadata filtering; current GitHub search pinned cfgrib1d11c7b919e9e87ebae50282fec62da441a1f76b
abc.py/xarray_store.py/xarray_plugin.py confirms that general precedent. This
extension's difference is an explicit typed distinction between wildcard,
encoded-missing and exact integer in the existing MoonBit station/provenance API.

CSV export was considered but deferred: the current JSON/typed output already
supports downstream consumers, while this missing-state gap prevents selecting
a valid input at all. No new output format, GRIB template or calendar arithmetic.

Sources: prior08 ECOSYSTEM-RAW.json and mooncakes-search logs;
https://github.com/ecmwf/cfgrib/blob/1d11c7b919e9e87ebae50282fec62da441a1f76b/cfgrib/abc.py ;
https://codes.ecmwf.int/grib/format/grib2/regulations/92.1.4 missing-code rule.
Existing recorded ecCodes all-one forecast accessor divergence is not reopened.

## Acceptance
1. Independently encode four otherwise identical4.0 fields with raw forecast
   all-one/0/6/sign-magnitude-6; preserve byte hashes and decoded expected values.
2. Demonstrate the old wildcard ambiguity and exact0 behavior before changes.
   MissingTime selects only the all-one field; ExactTime matches zero/positive/
   negative; AnyTime stays ambiguous. Criterion transitions are immutable and
   preserve reference/layer filters and backward-compatible constructor calls.
3. Named batch keeps Unicode labels, byte/message provenance, missing metadata
   and independent bitmap missing values. Include an all-or-error ambiguous case.
4. Both targets check/build/new and affected08 workflow tests, runnable example,
   independent workspace JSON readback, additive API/source/build identity and
   new ZIP readback. Do not rerun unchanged sampler/decoder/download suites.
