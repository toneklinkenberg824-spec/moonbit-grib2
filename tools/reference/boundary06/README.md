# Boundary06 reference
Run `python tools/reference/boundary06/generate_boundary.py` from the project root.
Only Python standard-library modules are required. The script independently
encodes3.0/4.0/5.0 fields with exact Fraction angular units and regenerates
boundary06_test.mbt plus local REFERENCE.json/fixture.grib2. No network, ecCodes
or product decoder is used to create expected results. API node round trips,
closed interval membership and hand-packed values1..9 provide the contract.
Static MoonBit tests do not require Python. Run moon info/fmt before testing.
