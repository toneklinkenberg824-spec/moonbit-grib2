///|
extern "js" fn arguments() -> FixedArray[String] =
  #|() => process.argv.slice(2)

///|
extern "js" fn read_bytes(path : String) -> Bytes =
  #|(path) => new Uint8Array(process.getBuiltinModule('fs').readFileSync(path))

///|
extern "js" fn diagnostic(line : String) -> Unit =
  #|(line) => { process.stderr.write(line + '\n'); }

///|
fn time_outcome(product : @grib2.Product) -> Json {
  match product.valid_time() {
    Ok(time) => { "valid_time": time.to_json() }
    Err(MissingForecastTime) => { "error": "missing-forecast-time" }
    Err(UnsupportedTimeUnit(unit)) => { "error": "unsupported-time-unit", "unit": unit.to_json() }
    Err(InvalidReferenceTime) => { "error": "invalid-reference-time" }
    Err(UnsupportedLeapSecond) => { "error": "unsupported-leap-second" }
    Err(TimeOutOfRange) => { "error": "out-of-range" }
  }
}

///|
fn decode_error(error : @grib2.GribError) -> Json {
  match error {
    UnsupportedTemplate(section, template) => { "phase": "decode", "code": "unsupported-template", "section": section.to_json(), "template": template.to_json() }
    CorruptedBitstream(message) => { "phase": "decode", "code": "corrupted-bitstream", "message": message.to_json() }
    InvalidGrid(message) => { "phase": "decode", "code": "invalid-grid", "message": message.to_json() }
    InvalidScanningMode(mode) => { "phase": "decode", "code": "invalid-scanning-mode", "mode": mode.to_json() }
    InvalidRequest(message) => { "phase": "decode", "code": "invalid-request", "message": message.to_json() }
  }
}

///|
fn main raise {
  let args = arguments()
  if args.length() != 1 { fail("usage: INPUT_GRIB") }
  let fields = match @grib2.read_fields(read_bytes(args[0])) {
    Ok(fields) => fields
    Err(error) => { diagnostic(decode_error(error).stringify()); fail("GRIB decoding failed") }
  }
  let rows : Array[Json] = []
  for index, field in fields {
    let product = field.product()
    rows.push({ "index": index.to_json(), "origin": field.origin().to_json(), "product": product.to_json(), "time": time_outcome(product) })
  }
  let result : Json = { "field_count": rows.length().to_json(), "fields": rows.to_json() }
  println(result.stringify())
}
