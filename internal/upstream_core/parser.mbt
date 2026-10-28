// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
priv struct ParsedMessageStep {
  message : @context.Grib2MessageContext
  next_offset : Int
}

///|
fn error_with_offset(prefix : String, offset : Int) -> String {
  prefix + " (offset=" + offset.to_string() + ")"
}

///|
fn read_u32_be(bytes : Bytes, offset : Int) -> UInt {
  binary_read_u32_be_uint(bytes, offset)
}

///|
fn read_u8_as_int(bytes : Bytes, offset : Int) -> Int {
  binary_read_u8_as_int(bytes, offset)
}

///|
fn has_grib_magic(bytes : Bytes, offset : Int) -> Bool {
  binary_has_magic_at(bytes, offset, b'G', b'R', b'I', b'B')
}

///|
fn has_end_magic(bytes : Bytes, offset : Int) -> Bool {
  binary_has_magic_at(bytes, offset, b'7', b'7', b'7', b'7')
}

///|
fn parse_total_length(
  bytes : Bytes,
  message_offset : Int,
) -> Result[Int, @context.Grib2ParseError] {
  let hi = read_u32_be(bytes, message_offset + 8).reinterpret_as_int()
  let lo = read_u32_be(bytes, message_offset + 12).reinterpret_as_int()
  if hi != 0 {
    Err(
      InvalidMessageLength(
        error_with_offset(
          "section0 message length exceeds 32-bit range: hi=" + hi.to_string(),
          message_offset + 8,
        ),
      ),
    )
  } else if lo < 20 {
    Err(
      InvalidMessageLength(
        error_with_offset(
          "section0 message length too small: " + lo.to_string(),
          message_offset + 8,
        ),
      ),
    )
  } else {
    Ok(lo)
  }
}

///|
fn parse_submessages(
  sections : Array[@context.Grib2SectionFrame],
) -> Result[Array[@context.Grib2SubmessageFrame], @context.Grib2ParseError] {
  if sections.length() == 0 {
    return Err(InvalidSectionOrder("section list is empty"))
  }
  if sections[0].section_number != 1 {
    return Err(
      InvalidSectionOrder(
        error_with_offset(
          "first section after section0 must be section1",
          sections[0].start,
        ),
      ),
    )
  }
  let submessages : Array[@context.Grib2SubmessageFrame] = []
  let mut current_section3 : @context.Grib2SectionFrame? = None
  loop 1 {
    index => {
      if index == sections.length() {
        return Ok(submessages)
      }
      let section2 = if sections[index].section_number == 2 {
        Some(sections[index])
      } else {
        None
      }
      let mut cursor = if section2 is Some(_) { index + 1 } else { index }
      if cursor >= sections.length() {
        return Err(
          InvalidSectionOrder(
            error_with_offset(
              "incomplete submessage after section2",
              sections[index].start,
            ),
          ),
        )
      }
      let section3 = if sections[cursor].section_number == 3 {
        current_section3 = Some(sections[cursor])
        cursor += 1
        sections[cursor - 1]
      } else {
        match current_section3 {
          Some(section3) => section3
          None =>
            return Err(
              InvalidSectionOrder(
                error_with_offset(
                  "expected section3 in first submessage",
                  sections[cursor].start,
                ),
              ),
            )
        }
      }
      if cursor + 3 >= sections.length() {
        return Err(
          InvalidSectionOrder(
            error_with_offset(
              "incomplete submessage, expected sections 4-7",
              sections[index].start,
            ),
          ),
        )
      }
      let section4 = sections[cursor]
      let section5 = sections[cursor + 1]
      let section6 = sections[cursor + 2]
      let section7 = sections[cursor + 3]
      if section4.section_number != 4 {
        return Err(
          InvalidSectionOrder(
            error_with_offset("expected section4", section4.start),
          ),
        )
      }
      if section5.section_number != 5 {
        return Err(
          InvalidSectionOrder(
            error_with_offset("expected section5", section5.start),
          ),
        )
      }
      if section6.section_number != 6 {
        return Err(
          InvalidSectionOrder(
            error_with_offset("expected section6", section6.start),
          ),
        )
      }
      if section7.section_number != 7 {
        return Err(
          InvalidSectionOrder(
            error_with_offset("expected section7", section7.start),
          ),
        )
      }
      submessages.push({
        section2,
        section3,
        section4,
        section5,
        section6,
        section7,
      })
      continue cursor + 4
    }
  }
}

///|
fn scan_sections(
  bytes : Bytes,
  offset : Int,
  message_end : Int,
) -> Result[Array[@context.Grib2SectionFrame], @context.Grib2ParseError] {
  let sections : Array[@context.Grib2SectionFrame] = []
  let section_limit = message_end - 4
  loop offset {
    section_cursor => {
      if section_cursor == section_limit {
        return Ok(sections)
      }
      if section_cursor + 5 > section_limit {
        return Err(
          UnexpectedEof(
            error_with_offset("section header is truncated", section_cursor),
          ),
        )
      }
      let section_length = read_u32_be(bytes, section_cursor).reinterpret_as_int()
      let section_number = read_u8_as_int(bytes, section_cursor + 4)
      if section_length < 5 {
        return Err(
          InvalidSectionLength(
            error_with_offset(
              "invalid section length: " + section_length.to_string(),
              section_cursor,
            ),
          ),
        )
      }
      if section_number < 1 || section_number > 7 {
        return Err(
          InvalidSectionNumber(
            error_with_offset(
              "invalid section number: " + section_number.to_string(),
              section_cursor + 4,
            ),
          ),
        )
      }
      // Local adaptation: subtraction before addition prevents integer-wrap bypass.
      let next_section_cursor = section_cursor + section_length
      if section_length > section_limit - section_cursor {
        return Err(
          InvalidSectionLength(
            error_with_offset(
              "section length crosses section8 boundary", section_cursor,
            ),
          ),
        )
      }
      sections.push({
        section_number,
        start: section_cursor,
        length: section_length,
      })
      continue next_section_cursor
    }
  }
}

///|
fn parse_one_message(
  bytes : Bytes,
  offset : Int,
) -> Result[ParsedMessageStep, @context.Grib2ParseError] {
  let file_length = bytes.length()
  if offset + 16 > file_length {
    return Err(
      UnexpectedEof(error_with_offset("section0 is truncated", offset)),
    )
  }
  if !has_grib_magic(bytes, offset) {
    return Err(InvalidMagic(error_with_offset("missing GRIB magic", offset)))
  }
  let discipline = read_u8_as_int(bytes, offset + 6)
  let edition = read_u8_as_int(bytes, offset + 7)
  let total_length = match parse_total_length(bytes, offset) {
    Ok(total_length) => total_length
    Err(error) => return Err(error)
  }
  let message_end = offset + total_length
  if total_length > file_length - offset {
    return Err(
      InvalidMessageLength(
        error_with_offset(
          "section0 length exceeds file size: " + total_length.to_string(),
          offset + 8,
        ),
      ),
    )
  }
  if !has_end_magic(bytes, message_end - 4) {
    return Err(
      InvalidMagic(
        error_with_offset("missing section8 magic 7777", message_end - 4),
      ),
    )
  }
  let sections = match scan_sections(bytes, offset + 16, message_end) {
    Ok(sections) => sections
    Err(error) => return Err(error)
  }
  if sections.length() == 0 {
    return Err(
      InvalidSectionOrder(
        error_with_offset(
          "message has no sections between section0 and section8", offset,
        ),
      ),
    )
  }
  if sections[0].section_number != 1 {
    return Err(
      InvalidSectionOrder(
        error_with_offset("first section must be section1", sections[0].start),
      ),
    )
  }
  let submessages = match parse_submessages(sections) {
    Ok(submessages) => submessages
    Err(error) => return Err(error)
  }
  Ok({
    message: {
      offset,
      total_length,
      discipline,
      edition,
      section1: sections[0],
      section8_offset: message_end - 4,
      sections,
      submessages,
      raw: bytes.sub(start=offset, end=message_end).to_bytes(),
    },
    next_offset: message_end,
  })
}

///|
pub fn parse_grib2_file(
  bytes : Bytes,
) -> Result[@context.Grib2FileContext, @context.Grib2ParseError] {
  let messages : Array[@context.Grib2MessageContext] = []
  loop 0 {
    offset => {
      if offset == bytes.length() {
        return Ok({ messages, })
      }
      if offset > bytes.length() {
        return Err(
          InvalidMessageLength(
            error_with_offset("cursor exceeded file length", offset),
          ),
        )
      }
      let step = match parse_one_message(bytes, offset) {
        Ok(step) => step
        Err(error) => return Err(error)
      }
      messages.push(step.message)
      continue step.next_offset
    }
  }
}
