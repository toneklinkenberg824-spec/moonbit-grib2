///|
/// Adapter helpers over bounds-checked section slices; framing/bit unpacking are vendored.
fn byte_at(b : Bytes, i : Int) -> Int {
  b[i].to_int()
}

///|
fn u16(b : Bytes, i : Int) -> Int {
  (byte_at(b, i) << 8) | byte_at(b, i + 1)
}

///|
fn u32(b : Bytes, i : Int) -> UInt {
  b.unsafe_read_uint32_be(i)
}

///|
fn sm32(b : Bytes, i : Int) -> Double {
  let raw = u32(b, i)
  let v = (raw & 0x7fffffffU).to_double()
  if (raw & 0x80000000U) != 0U {
    -v
  } else {
    v
  }
}

///|
fn surface(b : Bytes, i : Int) -> Surface {
  let scale = byte_at(b, i + 1)
  let v = u32(b, i + 2)
  {
    kind: byte_at(b, i),
    scale: if scale == 255 {
      None
    } else if scale >= 128 {
      Some(-(scale & 127))
    } else {
      Some(scale)
    },
    scaled_value: if v == 0xffffffffU {
      None
    } else {
      Some(v)
    },
  }
}

///|
fn section_bytes(
  m : @context.Grib2MessageContext,
  s : @context.Grib2SectionFrame,
) -> Bytes {
  let start = s.start - m.offset
  m.raw[start:start + s.length].to_owned()
}

///|
fn product(m : @context.Grib2MessageContext, p : Bytes) -> Product {
  let s = section_bytes(m, m.section1)
  {
    discipline: m.discipline,
    category: byte_at(p, 9),
    parameter: byte_at(p, 10),
    centre: u16(s, 5),
    subcentre: u16(s, 7),
    master_table: byte_at(s, 9),
    local_table: byte_at(s, 10),
    reference_time: [
      u16(s, 12),
      byte_at(s, 14),
      byte_at(s, 15),
      byte_at(s, 16),
      byte_at(s, 17),
      byte_at(s, 18),
    ],
    time_unit: byte_at(p, 17),
    forecast_time: if u32(p, 18) == 0xffffffffU {
      None
    } else {
      Some(sm32(p, 18).to_int())
    },
    first_surface: surface(p, 22),
    second_surface: surface(p, 28),
  }
}
