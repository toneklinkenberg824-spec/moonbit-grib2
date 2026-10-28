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
extern "js" fn write_new_csv(path : String, text : String) -> Unit =
  #|(path, text) => { process.getBuiltinModule('fs').writeFileSync(path, text, { encoding: 'utf8', flag: 'wx' }); }

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
fn decode_error(error : @grib2.GribError) -> Json {
  match error {
    UnsupportedTemplate(section, template) =>
      {
        "phase": "decode",
        "code": "unsupported-template",
        "section": section.to_json(),
        "template": template.to_json(),
      }
    CorruptedBitstream(message) =>
      {
        "phase": "decode",
        "code": "corrupted-bitstream",
        "message": message.to_json(),
      }
    InvalidScanningMode(mode) =>
      {
        "phase": "decode",
        "code": "invalid-scanning-mode",
        "mode": mode.to_json(),
      }
    InvalidGrid(message) =>
      {
        "phase": "decode",
        "code": "invalid-grid",
        "message": message.to_json(),
      }
    InvalidRequest(message) =>
      {
        "phase": "decode",
        "code": "invalid-request",
        "message": message.to_json(),
      }
  }
}

///|
fn main raise {
  let args = arguments()
  if args.length() != 4 {
    fail("usage: GRIB_PATH STATIONS_JSON OUTPUT_CSV FIELD_INDEX")
  }
  let index = @string.parse_int(args[3][:]) catch {
    Failure(_) => {
      let event : Json = {
        "phase": "selection",
        "code": "invalid-field-index",
        "argument": "FIELD_INDEX",
      }
      diagnostic(event.stringify())
      fail("FIELD_INDEX must parse as a supported Int")
    }
    error => raise error
  }
  let input : Array[InputStation] = @json.from_json(
    @json.parse(read_text(args[1])[:]),
  )
  let stations : Array[@grib2.Station] = input.map(s => {
    id: s.id,
    latitude: s.latitude,
    longitude: s.longitude,
  })
  let fields = match @grib2.read_fields(read_bytes(args[0])) {
    Ok(fields) => fields
    Err(error) => {
      diagnostic(decode_error(error).stringify())
      fail("GRIB decoding failed")
    }
  }
  if index < 0 || index >= fields.length() {
    let event : Json = {
      "phase": "selection",
      "code": "field-index-out-of-range",
      "field_count": fields.length().to_json(),
    }
    diagnostic(event.stringify())
    fail("field index must identify a decoded field")
  }
  let field = fields[index]
  let samples : Array[@grib2.Sample] = []
  let mut unavailable = 0
  for station_index, station in stations {
    match field.sample_result(station) {
      Ok(sample) => samples.push(sample)
      Err(reason) => {
        unavailable += 1
        let event : Json = {
          "phase": "sample",
          "station_id": station.id.to_json(),
          "station_index": station_index.to_json(),
          "code": ToJson::to_json(reason),
        }
        diagnostic(event.stringify())
        samples.push(field.sample(station))
      }
    }
  }
  let groups : Array[@grib2.FieldSamples] = [
    {
      key: "selected-field",
      origin: field.origin(),
      product: field.product(),
      samples,
    },
  ]
  write_new_csv(args[2], @grib2.station_results_csv(groups))
  let summary : Json = {
    "output": args[2].to_json(),
    "selected_index": index.to_json(),
    "rows": samples.length().to_json(),
    "unavailable": unavailable.to_json(),
    "origin": ToJson::to_json(field.origin()),
    "product": ToJson::to_json(field.product()),
  }
  println(summary.stringify())
}
