# Primary-source review: endpoint interpretation

The review distinguishes rectangular extremes from the final stored position
in an alternating traversal. Their coordinates can differ for an even number
of traversed rows/columns. This mathematical difference does not by itself
establish the required GRIB header convention.

- Template3.0 describes first/last grid coordinates. The inspected text does not
  explicitly settle the proposed parity interpretation for this review:
  https://codes.ecmwf.int/grib/format/grib2/templates/3/0/
- Flag table3.4 defines alternating row direction and first-row orientation.
  This establishes traversal flags, not an independently validated new message:
  https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_table3-4.shtml
- The inspected ECMWF Latlon iterator explicitly assumes non-alternating rows.
  Its coordinate output is therefore unsuitable as proof for this question:
  https://github.com/ecmwf/eccodes/blob/1ab79d05145abed0b461566b0c1d593acf1ad66f/src/eccodes/geo/iterator/Latlon.cc
- NOAA wgrib2 regular2ll derives geographic extremes/increments and contains
  alternating-row ambiguity handling. Its inspected implementation does not
  establish acceptance of the proposed endpoint variants:
  https://github.com/NOAA-EMC/wgrib2/blob/46676e16bcb800044da412abe1135927758aed24/src/geo.c

Conclusion is an inference bounded to these inspected sources: no conforming-
message premise was established for the proposed variants. Current rejection
cannot be classified as a GRIB2 correctness defect from this evidence.
Do not expand or tighten validation based on the unresolved interpretation.
No claim is made that all possible alternating encodings were audited.
Primary retrieval receipts are preserved in PRIMARY-SOURCES.json.
