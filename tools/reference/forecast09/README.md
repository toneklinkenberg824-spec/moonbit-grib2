Run `python tools/reference/forecast09/generate_forecast09.py` from the root.
Only Python standard library is used. It independently encodes four forecast
states, preserves a legacy-constructor compatibility control, generates four
new workflow tests and cmd/forecast, and writes local reference/synthetic bytes.
Run moon info/fmt before testing. Static tests need no Python/network. Raw WMO
missing/sign-magnitude semantics supply expected metadata; illustrative constants
and bitmap supply independent sample expectations.
