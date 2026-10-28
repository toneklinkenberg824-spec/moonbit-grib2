///|
extern "js" fn arguments() -> FixedArray[String] =
  #|() => process.argv.slice(2)

///|
extern "js" fn read_bytes(path : String) -> Bytes =
  #|(path) => new Uint8Array(process.getBuiltinModule('fs').readFileSync(path))

///|
extern "js" fn write_new_bytes(path : String, bytes : Bytes) -> Unit =
  #|(path, bytes) => { process.getBuiltinModule('fs').writeFileSync(path, bytes, { flag: 'wx' }); }

///|
extern "js" fn sha256(bytes : Bytes) -> String =
  #|(bytes) => process.getBuiltinModule('crypto').createHash('sha256').update(bytes).digest('hex')

///|
extern "js" fn diagnostic(line : String) -> Unit =
  #|(line) => { process.stderr.write(line + '\n'); }

///|
fn framing_event(error : @grib2.MessageFrameError) -> Json {
  let (code, offset) = match error {
    EmptyInput => ("empty-input", 0)
    InvalidMagic(at) => ("invalid-magic", at)
    TruncatedHeader(at) => ("truncated-header", at)
    UnsupportedEdition(at) => ("unsupported-edition", at)
    ShortMessageLength(at) => ("short-message-length", at)
    MessageLengthOutOfBounds(at) => ("message-length-out-of-bounds", at)
    InvalidEndMarker(at) => ("invalid-end-marker", at)
    MissingSection(at) => ("missing-section", at)
    TruncatedSectionHeader(at) => ("truncated-section-header", at)
    ShortSectionLength(at) => ("short-section-length", at)
    SectionLengthOutOfBounds(at) => ("section-length-out-of-bounds", at)
    InvalidSectionNumber(at) => ("invalid-section-number", at)
    InvalidFirstSection(at) => ("invalid-first-section", at)
  }
  { "phase": "framing", "code": code.to_json(), "byte_offset": offset.to_json(), }
}

///|
fn main raise {
  let args = arguments()
  if args.length() != 3 {
    fail("usage: INPUT_GRIB OUTPUT_GRIB MESSAGE_INDEX")
  }
  let index = @string.parse_int(args[2][:]) catch {
    Failure(_) => {
      let event : Json = {
        "phase": "selection",
        "code": "invalid-message-index",
        "argument": "MESSAGE_INDEX",
      }
      diagnostic(event.stringify())
      fail("MESSAGE_INDEX must parse as a supported Int")
    }
    error => raise error
  }
  let input = read_bytes(args[0])
  let spans = match @grib2.index_message_spans(input) {
    Ok(spans) => spans
    Err(error) => {
      diagnostic(framing_event(error).stringify())
      fail("GRIB message framing failed")
    }
  }
  if index < 0 || index >= spans.length() {
    let event : Json = {
      "phase": "selection",
      "code": "message-index-out-of-range",
      "message_count": spans.length().to_json(),
    }
    diagnostic(event.stringify())
    fail("message index must identify a framed original message")
  }
  let span = spans[index]
  let selected = input[span.byte_offset:span.byte_offset + span.length].to_owned()
  write_new_bytes(args[1], selected)
  let written = read_bytes(args[1])
  if written != selected {
    let event : Json = {
      "phase": "verification",
      "code": "output-readback-mismatch",
    }
    diagnostic(event.stringify())
    fail("output bytes do not match the selected original message")
  }
  let summary : Json = {
    "input": args[0].to_json(),
    "output": args[1].to_json(),
    "span": span.to_json(),
    "bytes_written": written.length().to_json(),
    "input_sha256": sha256(input).to_json(),
    "output_sha256": sha256(written).to_json(),
  }
  println(summary.stringify())
}
