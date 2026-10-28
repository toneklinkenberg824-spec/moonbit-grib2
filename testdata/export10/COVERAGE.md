# Round10 bounded end-to-end export review

No prior implementation correctness defect was established. The accepted
extension is a fixed station-row view of the existing named results; generic
CSV syntax is not claimed as novel. RFC4180 quoting/CRLF conventions and the
installed registry CSV search inform the small private adapter. No runtime
dependency or generic parser added.

| Workflow | Evidence/outcome |
|---|---|
| Layer/run/three-state selection to CSV |Synthetic missing/analysis0 requests retain blank numeric gaps, raw product JSON, messages/byte offsets and exact labels |
| CSV text/number semantics |Independent Python csv(strict=True) then json reader checks commas/multiple quotes/CRLF/Chinese/emoji/whitespace/empty IDs; zero and signed subnormal bit patterns preserved |
| Empty dimensions/input immutability |No samples gives exactly header; original nested results and selected-field identity remain untouched |
| Actual NOAA/IFS5.0-derived field chain |Current reader→full product query/forecast filter→batch station sampling→CSV→Python readback;8 rows,4 finite values within1e-9 of captured independent SciPy expectations and4 domain gaps |
| External consumer |Separate workspace on each target changes provider/station labels to quoted multiline Unicode, then repeats real CSV/JSON readback with origins/contributor weights |

3 new MoonBit contract cases per target are accompanied by independent parser
assertions for all synthetic cases and real/external outputs. All pre-existing
MoonBit sources except generated API are byte-identical; no old full24-field
suite/download or unchanged decoder/sampler tests rerun. Actual examples reuse
the existing licensed8x6 repacked5.0 bytes and archived SciPy point expectations,
not new original5.3/5.42 support or a fresh reference download.
