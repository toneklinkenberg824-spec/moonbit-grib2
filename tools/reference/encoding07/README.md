# Encoding/message07 reference generation
Run `python tools/reference/encoding07/generate_encoding.py` from the project root.
Python standard library suffices for manually encoded fixtures, exact Fraction
angular-unit expectations and encoding07_test.mbt. Add --eccodes with the pinned
environment from ../requirements.txt to capture external accessor observations.
Those observations explicitly retain UInt32/all-one forecast differences and
do not override the WMO raw-byte oracle. Captured observations are distributed
in testdata/encoding07/REFERENCE.json. Generation writes local reference/synthetic
bytes and root tests; run moon info/fmt before testing. No network/download or
product decoder supplies expected values. Static tests need no Python/ecCodes.
