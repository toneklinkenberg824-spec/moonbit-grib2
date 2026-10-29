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
fn checked_object(
  value : Json,
  allowed : ArrayView[String],
  label : String,
) -> Map[String, Json] raise {
  guard value is Object(object) else { fail(label + " must be an object") }
  for key, _ in object {
    let mut known = false
    for candidate in allowed {
      if candidate == key {
        known = true
        break
      }
    }
    if !known {
      fail(label + " contains unknown key: " + key)
    }
  }
  object
}

///|
fn required(object : Map[String, Json], key : String) -> Json raise {
  match object.get(key) {
    Some(value) => value
    None => fail("missing required key: " + key)
  }
}

///|
fn integer_json(value : Json) -> Json raise {
  guard value is Number(number, ..) && number.trunc() == number else {
    fail("expected an integer JSON number")
  }
  value
}

///|
fn query_int(value : Json) -> Int raise {
  @json.from_json(integer_json(value))
}

///|
fn required_int(object : Map[String, Json], key : String) -> Int raise {
  query_int(required(object, key))
}

///|
fn optional_int(object : Map[String, Json], key : String) -> Int? raise {
  match object.get(key) {
    None | Some(Null) => None
    Some(value) => Some(query_int(value))
  }
}

///|
fn query_surface(
  object : Map[String, Json],
  key : String,
) -> @grib2.Surface? raise {
  match object.get(key) {
    None | Some(Null) => None
    Some(value) => {
      let surface = checked_object(
        value,
        ["kind", "scale", "scaled_value"],
        key,
      )
      let scaled_value : UInt? = match surface.get("scaled_value") {
        None | Some(Null) => None
        Some(value) => Some(@json.from_json(integer_json(value)))
      }
      Some({
        kind: required_int(surface, "kind"),
        scale: optional_int(surface, "scale"),
        scaled_value,
      })
    }
  }
}

///|
fn query_reference(object : Map[String, Json]) -> Array[Int]? raise {
  match object.get("reference_time") {
    None | Some(Null) => None
    Some(value) => {
      guard value is Array(entries) else {
        fail("reference_time must be an array")
      }
      let components : Array[Int] = []
      for entry in entries {
        components.push(query_int(entry))
      }
      Some(components)
    }
  }
}

///|
fn parse_query(value : Json) -> @grib2.FieldQuery raise {
  let object = checked_object(
    value,
    [
      "discipline", "category", "parameter", "centre", "subcentre", "master_table",
      "local_table", "time_unit", "forecast_time", "reference_time", "first_surface",
      "second_surface",
    ],
    "query",
  )
  let time : @grib2.ForecastTimeFilter = match object.get("forecast_time") {
    None => AnyTime
    Some(Null) => MissingTime
    Some(value) => {
      let lead = query_int(value)
      ExactTime(lead)
    }
  }
  @grib2.FieldQuery::new(
    required_int(object, "discipline"),
    required_int(object, "category"),
    required_int(object, "parameter"),
    centre?=optional_int(object, "centre"),
    subcentre?=optional_int(object, "subcentre"),
    master_table?=optional_int(object, "master_table"),
    local_table?=optional_int(object, "local_table"),
    time_unit?=optional_int(object, "time_unit"),
    first_surface?=query_surface(object, "first_surface"),
    second_surface?=query_surface(object, "second_surface"),
    reference_time?=query_reference(object),
  ).with_forecast_time_filter(time)
}

///|
fn parse_requests(value : Json) -> Array[@grib2.FieldRequest] raise {
  guard value is Array(items) else { fail("requests must be an array") }
  let requests : Array[@grib2.FieldRequest] = []
  for item in items {
    let object = checked_object(item, ["key", "query"], "request")
    let key : String = @json.from_json(required(object, "key"))
    requests.push({ key, query: parse_query(required(object, "query")), })
  }
  requests
}

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
    InvalidGrid(message) =>
      {
        "phase": "decode",
        "code": "invalid-grid",
        "message": message.to_json(),
      }
    InvalidScanningMode(mode) =>
      {
        "phase": "decode",
        "code": "invalid-scanning-mode",
        "mode": mode.to_json(),
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
    fail("usage: GRIB_PATH REQUESTS_JSON STATIONS_JSON OUTPUT_CSV")
  }
  let request_text = read_text(args[1])
  let requests = parse_requests(@json.parse(request_text[:])) catch {
    error => {
      let event : Json = { "phase": "requests", "code": "invalid-request-file" }
      diagnostic(event.stringify())
      raise error
    }
  }
  let input : Array[InputStation] = @json.from_json(
    @json.parse(read_text(args[2])[:]),
  )
  let stations : Array[@grib2.Station] = input.map(station => {
    id: station.id,
    latitude: station.latitude,
    longitude: station.longitude,
  })
  let fields = match @grib2.read_fields(read_bytes(args[0])) {
    Ok(fields) => fields
    Err(error) => {
      diagnostic(decode_error(error).stringify())
      fail("GRIB decoding failed")
    }
  }
  let results = match
    @grib2.sample_requested_fields(fields, requests, stations) {
    Ok(results) => results
    Err(InvalidRequest(message)) => {
      let event : Json = {
        "phase": "selection",
        "code": "invalid-field-request",
        "message": message.to_json(),
      }
      diagnostic(event.stringify())
      fail("field request selection failed")
    }
    Err(error) => {
      diagnostic(decode_error(error).stringify())
      fail("field request failed")
    }
  }
  let mut row_count = 0
  let mut unavailable = 0
  let groups = results.map(group => {
    row_count += group.samples.length()
    for sample in group.samples {
      if sample.value is None {
        unavailable += 1
      }
    }
    let metadata : Json = {
      "key": group.key.to_json(),
      "origin": group.origin.to_json(),
      "product": group.product.to_json(),
    }
    metadata
  })
  let csv = @grib2.station_results_csv(results)
  write_new_csv(args[3], csv)
  let summary : Json = {
    "output": args[3].to_json(),
    "request_count": results.length().to_json(),
    "station_count": stations.length().to_json(),
    "row_count": row_count.to_json(),
    "unavailable": unavailable.to_json(),
    "groups": groups.to_json(),
  }
  println(summary.stringify())
}
