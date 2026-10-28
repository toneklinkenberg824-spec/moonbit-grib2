# Data attribution for the station CSV example

Source code is Apache-2.0. The following weather data retain their own terms.
NOAA/NWS source is public domain unless otherwise noted; original policy:
https://www.weather.gov/disclaimer .
ECMWF IFS Open Data are attributed toECMWF underCC-BY-4.0 and ECMWF terms:
https://www.ecmwf.int/en/forecasts/datasets/open-data .

Original source fields were cropped to8x6 nodes and repacked to5.0 with ecCodes;
this example further selects fields and performs scalar coordinate-bilinear
station interpolation, representing uncovered locations as empty CSV values.
The output is derived, not an unmodified original forecast or live service.

Original source: https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20260221/00/atmos/gfs.t00z.pgrb2.1p00.f000

Input derivative: noaa-gfs-repacked.grib2; SHA256 e69245079ff183b934b343d7c0a43d0591e59b916ea80f8c695e64568f93464a

Original source: https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20260221/00z/ifs/0p25/oper/20260221000000-0h-oper-fc.grib2

Input derivative: ecmwf-ifs-repacked.grib2; SHA256 904c337ee2e1d7171f2997b199a9906e39b657c48de07d9b9d58748a43fd0977
