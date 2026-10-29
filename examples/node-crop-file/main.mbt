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
struct InputBounds {
  south : Double
  north : Double
  west : Double
  east : Double
} derive(FromJson)

///|
fn error_event(phase : String, error : @grib2.GribError) -> Json {
  match error {
    UnsupportedTemplate(section, template) =>
      {
        "phase": phase.to_json(),
        "code": "unsupported-template",
        "section": section.to_json(),
        "template": template.to_json(),
      }
    CorruptedBitstream(message) =>
      {
        "phase": phase.to_json(),
        "code": "corrupted-bitstream",
        "message": message.to_json(),
      }
    InvalidScanningMode(mode) =>
      {
        "phase": phase.to_json(),
        "code": "invalid-scanning-mode",
        "mode": mode.to_json(),
      }
    InvalidGrid(message) =>
      {
        "phase": phase.to_json(),
        "code": "invalid-grid",
        "message": message.to_json(),
      }
    InvalidRequest(message) =>
      {
        "phase": phase.to_json(),
        "code": "invalid-request",
        "message": message.to_json(),
      }
  }
}

///|
fn emit(value : Json) -> Unit {
  println(value.stringify())
}

///|
fn main raise {
  let args = arguments()
  if args.length() != 3 {
    fail("usage: GRIB_PATH BOUNDS_JSON FIELD_INDEX")
  }
  let index = @string.parse_int(args[2][:]) catch {
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
  let input : InputBounds = @json.from_json(@json.parse(read_text(args[1])[:]))
  let bounds : @grib2.BBox = {
    south: input.south,
    north: input.north,
    west: input.west,
    east: input.east,
  }
  let fields = match @grib2.read_fields(read_bytes(args[0])) {
    Ok(fields) => fields
    Err(error) => {
      diagnostic(error_event("decode", error).stringify())
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
  let nodes = match field.crop_iter(bounds) {
    Ok(nodes) => nodes
    Err(error) => {
      diagnostic(error_event("bounds", error).stringify())
      fail("invalid regional bounds")
    }
  }
  emit({
    "type": "field",
    "schema": "grib2-node-crop/1",
    "selected_index": index.to_json(),
    "field_count": fields.length().to_json(),
    "bounds": bounds.to_json(),
    "origin": field.origin().to_json(),
    "product": field.product().to_json(),
    "grid": {
      "rows": field.rows().to_json(),
      "cols": field.cols().to_json(),
      "north": field.north.to_json(),
      "west": field.west.to_json(),
      "dx": field.dx.to_json(),
      "dy": field.dy.to_json(),
      "cyclic": field.is_global().to_json(),
      "unique_columns": field.unique_cols.to_json(),
    },
  })
  let mut count = 0
  let mut missing = 0
  nodes.each(fn(point) {
    emit({ "type": "point", "point": point.to_json() })
    count += 1
    if point.value is None {
      missing += 1
    }
  })
  emit({
    "type": "end",
    "points": count.to_json(),
    "missing": missing.to_json(),
  })
}
