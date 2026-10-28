# Deep repair05 reference generation
Run `python generate_deep.py` then `python generate_contract.py` in this directory
with the pinned NumPy dependency from ../requirements.txt. The scripts use the
existing constant.grib2 fixture, exact Python Fraction arithmetic and independent
NumPy scan transformations; no network or product decoder is used as an oracle.
They regenerate root deep_* tests and local REFERENCE.json. The deep generator
also writes an illustrative external mutation-consumer source locally; it does
not run it. The actual before/after independent workspace logs remain in the
separate deep-repair-05-20261028 report. Static MoonBit tests need no Python.
