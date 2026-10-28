# Literal framed-message handoff contracts

These are synthetic bytes, not forecasts. The Section1/3/4 literal headers use
this project's existing3x2 supported layout. Five8-bit values are hand-set with
bitmap011111: [null,0,2,4,6,8]. No scanner generated EXPECTED.json.

The supported and unsupported messages are185bytes each; the only unsupported
change is Section3 template1. Both original concatenation orders have manual
spans (0,185),(185,185). SHA-256 pins cover each complete literal input. The
multi-field message is257bytes with two fields but one message span; its second
forecast is12 with [null,1,3,5,7,9]. The198-byte payload case has a Section2 whose
opaque bytes contain GRIB7777. No payload markers establish message boundaries.

All51 cases and exact error offsets were frozen before production implementation.
The10 accepted framing vectors include deliberately incomplete or incorrectly
ordered semantic sections, which the old decoder must reject. Framing success
is not complete GRIB semantic, template or meteorological validity.

The41 failures cover empty/garbage/partial headers, edition, short and unsigned64
oversized lengths, bad tails, empty/truncated sections, unsigned32 section lengths,
invalid/first section numbers, residual bytes, declared cuts and late failures.
No successful partial list is returned. Selected bytes and their original span
remain separate from decoded slice-local Origin. Existing parsers are unchanged.
