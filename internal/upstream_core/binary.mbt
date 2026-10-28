// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
pub fn binary_read_u8_as_int(bytes : Bytes, offset : Int) -> Int {
  bytes[offset].to_uint().reinterpret_as_int()
}

///|
pub fn binary_read_u32_be_uint(bytes : Bytes, offset : Int) -> UInt {
  bytes.unsafe_read_uint32_be(offset)
}

///|
pub fn binary_read_u16_be(bytes : Bytes, offset : Int) -> Int {
  bytes.unsafe_read_uint16_be(offset).to_uint().reinterpret_as_int()
}

///|
pub fn binary_read_u16_be_view(bytes : BytesView, offset : Int) -> Int {
  bytes.unsafe_read_uint16_be(offset).to_uint().reinterpret_as_int()
}

///|
pub fn binary_read_u32_be_view(bytes : BytesView, offset : Int) -> Int {
  bytes.unsafe_read_uint32_be(offset).reinterpret_as_int()
}

///|
pub fn binary_bytes_with_u8_at(
  bytes : Bytes,
  offset : Int,
  value : Int,
) -> Bytes {
  let copy = bytes.to_array()
  copy[offset] = value.to_byte()
  Bytes::from_array(copy)
}

///|
pub fn binary_bytes_with_u16_be_at(
  bytes : Bytes,
  offset : Int,
  value : Int,
) -> Bytes {
  let copy = bytes.to_array()
  copy[offset] = ((value >> 8) & 0xff).to_byte()
  copy[offset + 1] = (value & 0xff).to_byte()
  Bytes::from_array(copy)
}

///|
pub fn binary_bytes_with_u32_be_at(
  bytes : Bytes,
  offset : Int,
  value : Int,
) -> Bytes {
  let copy = bytes.to_array()
  copy[offset] = ((value >> 24) & 0xff).to_byte()
  copy[offset + 1] = ((value >> 16) & 0xff).to_byte()
  copy[offset + 2] = ((value >> 8) & 0xff).to_byte()
  copy[offset + 3] = (value & 0xff).to_byte()
  Bytes::from_array(copy)
}

///|
pub fn binary_encode_f32le_latin1(values : Array[Double]) -> String {
  let buf = StringBuilder::new()
  for value in values {
    let f32_bits = Float::from_double(value).reinterpret_as_uint()
    for j in 0..<4 {
      let byte_val = ((f32_bits >> (j * 8)) & 0xFF).reinterpret_as_int()
      buf.write_char(Char::from_int(byte_val))
    }
  }
  buf.to_string()
}

///|
pub fn binary_has_magic_at(
  bytes : Bytes,
  offset : Int,
  b0 : Byte,
  b1 : Byte,
  b2 : Byte,
  b3 : Byte,
) -> Bool {
  bytes[offset] == b0 &&
  bytes[offset + 1] == b1 &&
  bytes[offset + 2] == b2 &&
  bytes[offset + 3] == b3
}

///|
pub fn binary_has_magic_tail(
  bytes : Bytes,
  b0 : Byte,
  b1 : Byte,
  b2 : Byte,
  b3 : Byte,
) -> Bool {
  bytes.length() >= 4 &&
  bytes[bytes.length() - 4] == b0 &&
  bytes[bytes.length() - 3] == b1 &&
  bytes[bytes.length() - 2] == b2 &&
  bytes[bytes.length() - 1] == b3
}
