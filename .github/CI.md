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
- A stable root message-span index and exact-byte decoder receiver run on JS and
  Wasm-GC against51 pre-frozen literal framing vectors. Checks include mixed
  supported/unsupported messages, unsigned bounds, section boundaries, payload
  magic, original span context and unchanged slice-local decoder identities.
- A Node binary file receiver extracts original messages from a961-byte mixed
  container, exclusively creates output, verifies physical readback and hashes,
  and hands NOAA/IFS/multi-field outputs to existing inventory/11-column CSV hosts.
  Filesystem/error controls include an externally injected readback mismatch.
- A Node named query-file receiver applies the same external JSON recipe to
  NOAA/IFS inputs with opposite field order, then independently reads all eleven
  CSV columns, exact labels, original identities and known archived values.
  Real processes check omission/null/zero/negative lead, all encoded filters,
  distinct raw surfaces, integral numeric input, unknown keys, late selection
  failures, empty inputs, nonfinite station gaps and no-clobber output handling.
  This is a new JSON/filesystem boundary; old query/scientific fixtures are reused
  without rerunning their external reference generators.
- A fixed-unit forecast valid-time gate compares51 pre-frozen calendar cases and
  a43-field raw file through an independent public workspace on JS/Wasm-GC, plus
  a Node arbitrary-file JSON receiver. Python datetime and independent Section1/4
  reads check Gregorian bounds, century/leap carries, negative and wide leads,
  explicit time errors, unchanged raw metadata and encoded query distinctions.
  This opt-in fixed86400-second-day policy does not model leap seconds or add
  calendar/local units, external weather references or new template support.
- A paired revision station comparison gate checks30 public comparisons per
  target and a complete two-file Node receiver. Independent original packed bits
  and Fraction stencils check both full sampling outcomes, provenance, missing
  reasons, signed differences and overflow. Encoded parameter/table/surface and
  existing valid-time compatibility, different grids and pre-output failures are
  checked without changing the old sampler/calendar or adding a physical model.
  An initial fixture-scale error is retained in the separate R08 report; corrected
  finite large inputs must still produce an explicit subtraction overflow.
- A singleton regular-grid axis gate checks43 small fields through JS/Wasm-GC,
  four targeted root regressions per backend and the unchanged real Node file
  receiver. Original bytes, integer node directions and Fraction weights verify
  all scan modes for each line orientation, masks/points/full sample provenance,
  crops, narrow support and old positive-step/polar/budget/error behavior.
  It accepts0/missing increments only on an endpoint-consistent singleton axis,
  never infers unused coverage or extrapolates off that represented point/line.
- A diagnostic receiver gate freshly builds the unchanged Node file adapter and
  consumes four actual CSV rows with positive/negative nested5002-digit ancillary
  integers. It verifies all11columns, exact source values, standard JSON numeric
  output, strict coordinate/NaN rejection and the unchanged global integer limit.
  Only the optional Python station JSON parser changes; no coordinate, grid or
  core-library range is extended by this gate.
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
