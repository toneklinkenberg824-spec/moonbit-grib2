Run `python tools/reference/export10/generate_csv10.py` from the root.
Only Python standard library is used. It regenerates CSV contract tests and
cmd/export from existing licensed fixtures, preserving existing data hashes and
reusing captured SciPy point expectations in oracle_test.mbt. No download or
reference-tool rerun. Run moon info/fmt before tests; static tests need no Python.
The independent csv/json readback evidence is in the separate round10 report.
