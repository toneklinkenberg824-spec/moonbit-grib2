///|
/// An original message range, not a decoded-field identity or validity certificate.
pub(all) struct MessageSpan {
  index : Int
  byte_offset : Int
  length : Int
  edition : Int
  discipline : Int
} derive(Debug, Eq, ToJson)

///|
/// Framing failure at an original byte offset. No successful prefix is returned.
/// Length failures point to the length field; section-number failures to its octet.
pub(all) enum MessageFrameError {
  EmptyInput
  InvalidMagic(Int)
  TruncatedHeader(Int)
  UnsupportedEdition(Int)
  ShortMessageLength(Int)
  MessageLengthOutOfBounds(Int)
  InvalidEndMarker(Int)
  MissingSection(Int)
  TruncatedSectionHeader(Int)
  ShortSectionLength(Int)
  SectionLengthOutOfBounds(Int)
  InvalidSectionNumber(Int)
  InvalidFirstSection(Int)
} derive(Debug, Eq)

///|
/// Index every declared GRIB2 message from byte0 to EOF without decoding templates,
/// copying raw messages or materializing section/submessage contexts. Validate only
/// Section0, the declared7777 end and length-delimited sections1..7 starting with1.
/// Section contents and repeated-section semantic order are deliberately unchecked.
/// Input bytes remain resident and metadata grows with message count.
pub fn index_message_spans(
  bytes : Bytes,
) -> Result[Array[MessageSpan], MessageFrameError] {
  if bytes.length() == 0 {
    return Err(EmptyInput)
  }
  let spans : Array[MessageSpan] = []
  let magic = b"GRIB"
  let mut offset = 0
  while offset < bytes.length() {
    let remaining = bytes.length() - offset
    let prefix = if remaining < 4 { remaining } else { 4 }
    for i in 0..<prefix {
      if bytes[offset + i] != magic[i] {
        return Err(InvalidMagic(offset))
      }
    }
    if remaining < 16 {
      return Err(TruncatedHeader(offset))
    }
    let edition = byte_at(bytes, offset + 7)
    if edition != 2 {
      return Err(UnsupportedEdition(offset + 7))
    }
    let total = (u32(bytes, offset + 8).to_uint64() << 32) |
      u32(bytes, offset + 12).to_uint64()
    if total < 20UL {
      return Err(ShortMessageLength(offset + 8))
    }
    // remaining is a nonnegative Int. This proves Int representability and that
    // the subsequent conversion/addition cannot wrap, including high-bit UInt64.
    if total > remaining.to_uint64() {
      return Err(MessageLengthOutOfBounds(offset + 8))
    }
    let length = total.to_int()
    let end = offset + length
    let section_end = end - 4
    if bytes[section_end] != b'7' ||
      bytes[section_end + 1] != b'7' ||
      bytes[section_end + 2] != b'7' ||
      bytes[section_end + 3] != b'7' {
      return Err(InvalidEndMarker(section_end))
    }
    let mut cursor = offset + 16
    if cursor == section_end {
      return Err(MissingSection(cursor))
    }
    while cursor < section_end {
      let section_remaining = section_end - cursor
      if section_remaining < 5 {
        return Err(TruncatedSectionHeader(cursor))
      }
      let section_length = u32(bytes, cursor)
      if section_length < 5U {
        return Err(ShortSectionLength(cursor))
      }
      if section_length > section_remaining.to_uint() {
        return Err(SectionLengthOutOfBounds(cursor))
      }
      let number = byte_at(bytes, cursor + 4)
      if number < 1 || number > 7 {
        return Err(InvalidSectionNumber(cursor + 4))
      }
      if cursor == offset + 16 && number != 1 {
        return Err(InvalidFirstSection(cursor + 4))
      }
      cursor += section_length.to_int()
    }
    spans.push({
      index: spans.length(),
      byte_offset: offset,
      length,
      edition,
      discipline: byte_at(bytes, offset + 6),
    })
    offset = end
  }
  Ok(spans)
}
