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
  if args.length() != 1 {
    fail("usage: GRIB_PATH")
  }
  let fields = match @grib2.read_fields(read_bytes(args[0])) {
    Ok(fields) => fields
    Err(error) => {
      diagnostic(decode_error(error).stringify())
      fail("GRIB decoding failed")
    }
  }
  let entries : Array[Json] = []
  for index, field in fields {
    let entry : Json = {
      "index": index.to_json(),
      "rows": field.rows().to_json(),
      "cols": field.cols().to_json(),
      "is_global": field.is_global().to_json(),
      "origin": ToJson::to_json(field.origin()),
      "product": ToJson::to_json(field.product()),
    }
    entries.push(entry)
  }
  let inventory : Json = {
    "field_count": fields.length().to_json(),
    "fields": entries.to_json(),
  }
  println(inventory.stringify())
}
