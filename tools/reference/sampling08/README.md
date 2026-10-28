# sampling08 reference generation
Run `python tools/reference/sampling08/generate_sampling08.py` from the project root.
The Python standard library creates manually encoded synthetic fixtures and
independent expected values; static MoonBit tests need no Python/network.
For requests08 add --eccodes in the pinned reference environment to capture
external decode/metadata observations. Captured data live in testdata/requests08.
Generation rewrites its root test source and local references; requests08 also
regenerates cmd/layers. Run moon info/fmt before testing.
