# Reproducible validation

The workflow runs on ordinary Ubuntu 24.04 GitHub runners with a 15/20 minute
job limit and read-only repository permissions. It does not install anything
on a developer's global SDK or use paid services.

- MoonBit compiler: `0.10.12+1634b282e` (moon `0.1.20260904`). The installer uses
  the official binary/core archive layout and bundling commands from
  <https://cli.moonbitlang.com/install/unix.sh>. Both archive SHA256 values are
  fixed in `scripts/setup-moonbit.sh`; the SDK checksum was published alongside
  the official archive, and the core digest was measured from its official URL.
- Node.js: `24.11.0`; Python: `3.14.4`. Official checkout/setup action commits
  are pinned in the workflow.
- Core jobs run real `moon check`, `moon build`, `moon test` and public examples
  separately for `js` and `wasm-gc`.
- The file-consumer job builds the two independent Node modules in a temporary
  local workspace, then reads a real inventory, selects forecast 6, produces
  CSV and joins diagnostics. Committed expectations cover metadata, missing
  values, the NaN identity repair, strict JSON number representation, later-field
  decode failures and preservation of an existing output file.
  A separate real-process selection contract checks malformed Int arguments,
  all observed accepted integer spellings, literal diagnostics, original
  decode/IO failures and absent/pre-existing output guards.
- A public FieldQuery catalogue consumer runs on both JS and Wasm-GC. Its
  independent raw-section oracle checks a six-field/five-message fixture,
  complete original identities, matching flags, encoded time/surface distinctions,
  original unique/batch error contracts and detached metadata snapshots.
- A public regional-node iterator consumer runs on JS and Wasm-GC. Independent
  raw bits and hand-written node tables check dateline boxes, duplicate endpoints,
  scan identities, null/zero values, old crop/error compatibility and pull cursors;
  a million-point constant field is consumed only for its first two nodes.
- The NyaCSV job uses the unchanged public dependency at commit
  `fe4448e1e45a25f6fca151320c766519e80162c9`, never a floating registry version.
  Both backends compile and run the real consumer; independent fixture
  expectations check values, zero/missing, forecast metadata, labels and JSON
  cells. See `testdata/consumer13/REFERENCE.json` for reference provenance and
  `THIRD_PARTY.md` / `testdata/LICENSES.md` for attribution and data terms.

The source tests are offline. The CI job downloads its pinned toolchain and
NyaCSV source, but does not redownload weather forecasts or rerun the external
ecCodes/SciPy scientific-reference generation. A passing run proves these
commands and cases for that exact commit; it is not all-GRIB compatibility,
performance certification, a Mooncakes release or contest acceptance.
