# Real-file message delivery and old receiver controls

EXPECTED.json fixes four original messages, lengths185/251/268/257 and manual
offsets0/185/436/704 before the extractor implementation. Acceptance constructs
one961-byte file in its private temporary work directory from those committed
originals, then physically writes/reads selected output files through the new CLI.
No duplicate weather download or reference generator is run.

The unsupported and multi-field originals are the accepted R04 synthetic bytes.
The NOAA/IFS originals and their attribution remain in testdata/LICENSES.md and
THIRD_PARTY.md. The two sample values are reused from the accepted archived
consumer13 reference, not recomputed by this extractor. This is file handoff and
receiver compatibility evidence, not new scientific validation or native
compression support. The multi-field second value6 at(0,10.5) follows hand nodes
5 and7 at weights0.5; original field identity must survive.

Independent acceptance covers Unicode paths, exact bytes/sha256/original span,
unsupported message delivery, retained multi-fields, existing inventory and
11-column CSV receivers, Int syntax/range, all-input late-framing validation,
existing/same-input/directory/missing-path output guards, and an external Node
filesystem preload which corrupts only the returned readback buffer. The latter
must prevent a false success summary; it adds no production test flag or hook.
