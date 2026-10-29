///|
extern "js" fn arguments() -> FixedArray[String] =
  #|() => process.argv.slice(2)

///|
extern "js" fn read_bytes(path : String) -> Bytes =
  #|(path) => new Uint8Array(process.getBuiltinModule('fs').readFileSync(path))

///|
extern "js" fn read_text(path : String) -> String =
  #|(path) => process.getBuiltinModule('fs').readFileSync(path, 'utf8').replace(/^\uFEFF/, '')

///|
extern "js" fn diagnostic(line : String) -> Unit =
  #|(line) => { process.stderr.write(line + '\n'); }

///|
struct InputStation {
  id : String
  latitude : Double
  longitude : Double
} derive(FromJson)

///|
fn index_argument(argument : String, side : String) -> Int raise {
  @string.parse_int(argument[:]) catch {
    Failure(_) => {
      let event : Json = { "phase": "selection", "code": "invalid-field-index", "side": side.to_json() }
      diagnostic(event.stringify())
      fail("field index must parse as a supported Int")
    }
    error => raise error
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
fn read_selected(path : String, index : Int, side : String) -> @grib2.GriddedField raise {
  let fields = match @grib2.read_fields(read_bytes(path)) {
    Ok(fields) => fields
    Err(error) => { diagnostic(decode_error(error).stringify()); fail("GRIB decoding failed") }
  }
  if index < 0 || index >= fields.length() {
    let event : Json = { "phase": "selection", "code": "field-index-out-of-range", "side": side.to_json(), "field_count": fields.length().to_json() }
    diagnostic(event.stringify())
    fail("field index out of range")
  }
  fields[index]
}

///|
fn main raise {
  let args = arguments()
  if args.length() != 5 { fail("usage: LEFT_GRIB LEFT_INDEX RIGHT_GRIB RIGHT_INDEX STATIONS_JSON") }
  let left_index = index_argument(args[1], "left")
  let right_index = index_argument(args[3], "right")
  let input : Array[InputStation] = @json.from_json(@json.parse(read_text(args[4])[:]))
  let stations : Array[@grib2.Station] = input.map(s => { id: s.id, latitude: s.latitude, longitude: s.longitude })
  let left = read_selected(args[0], left_index, "left")
  let right = read_selected(args[2], right_index, "right")
  let rows = match left.compare_stations(right, stations) {
    Ok(rows) => rows
    Err(error) => {
      let event : Json = { "phase": "comparison", "error": error.to_json() }
      diagnostic(event.stringify())
      fail("fields do not meet comparison contract")
    }
  }
  let mut available = 0
  for row in rows { if row.difference is Ok(_) { available += 1 } }
  let result : Json = {
    "operation": "right-minus-left",
    "valid_time": left.product().valid_time().unwrap().to_json(),
    "left": { "index": left_index.to_json(), "origin": left.origin().to_json(), "product": left.product().to_json() },
    "right": { "index": right_index.to_json(), "origin": right.origin().to_json(), "product": right.product().to_json() },
    "station_count": rows.length().to_json(), "available_count": available.to_json(), "unavailable_count": (rows.length() - available).to_json(),
    "rows": rows.to_json(),
  }
  println(result.stringify())
}
