// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
/// Bitstream reader for unpacking GRIB2 data.
/// Reads arbitrary number of bits from a byte buffer in big-endian order.

///|
pub(all) struct BitReader {
  data : Bytes
  mut bit_position : Int
}

///|
pub fn BitReader::new(data : Bytes) -> BitReader {
  { data, bit_position: 0, }
}

///|
/// Read up to 32 bits and return as unsigned integer.
/// Returns 0 if not enough bits available.
pub fn BitReader::read_bits(self : BitReader, count : Int) -> UInt {
  if count <= 0 || count > 32 {
    return 0U
  }
  let total_bits = self.data.length() * 8
  if self.bit_position + count > total_bits {
    return 0U
  }
  let mut result = 0U
  let mut remaining = count
  while remaining > 0 {
    let byte_index = self.bit_position / 8
    let bit_offset = self.bit_position % 8
    let bits_in_byte = 8 - bit_offset
    let bits_to_read = if remaining < bits_in_byte {
      remaining
    } else {
      bits_in_byte
    }
    let mask = (1 << bits_to_read) - 1
    let byte_val = self.data[byte_index].to_int()
    let shift = bits_in_byte - bits_to_read
    let bits = (byte_val >> shift) & mask
    result = (result << bits_to_read) | bits.reinterpret_as_uint()
    self.bit_position += bits_to_read
    remaining -= bits_to_read
  }
  result
}

///|
/// Read bits and return as signed integer (two's complement).
pub fn BitReader::read_bits_signed(self : BitReader, count : Int) -> Int {
  if count <= 0 || count > 32 {
    return 0
  }
  let unsigned_val = self.read_bits(count)
  let sign_bit = 1U << (count - 1)
  if (unsigned_val & sign_bit) != 0U {
    // Negative: sign extend
    let mask = (1U << count) - 1U
    (unsigned_val | (0xFFFFFFFFU ^ mask)).reinterpret_as_int()
  } else {
    unsigned_val.reinterpret_as_int()
  }
}

///|
/// Get remaining bits count.
pub fn BitReader::remaining_bits(self : BitReader) -> Int {
  let total_bits = self.data.length() * 8
  total_bits - self.bit_position
}

///|
/// Check if there are at least `count` bits remaining.
pub fn BitReader::has_bits(self : BitReader, count : Int) -> Bool {
  self.remaining_bits() >= count
}

///|
/// Reset to beginning.
pub fn BitReader::reset(self : BitReader) -> Unit {
  self.bit_position = 0
}

///|
/// Skip bits without reading.
pub fn BitReader::skip_bits(self : BitReader, count : Int) -> Unit {
  self.bit_position += count
}

///|
test "read_bits basic" {
  // 0xAB = 10101011, 0xCD = 11001101
  let data = Bytes::from_array([b'\xAB', b'\xCD'])
  let reader = BitReader::new(data)
  // Read 4 bits: 1010 = 10
  inspect(reader.read_bits(4), content="10")
  // Read 8 bits: 10111100 = 188
  inspect(reader.read_bits(8), content="188")
  // Read 4 bits: 1101 = 13
  inspect(reader.read_bits(4), content="13")
}

///|
test "read_bits_signed" {
  // 0xFF = 11111111 (8-bit signed = -1)
  let data = Bytes::from_array([b'\xFF'])
  let reader = BitReader::new(data)
  inspect(reader.read_bits_signed(8), content="-1")
}

///|
test "read_bits_signed positive" {
  // 0x7F = 01111111 (8-bit signed = 127)
  let data = Bytes::from_array([b'\x7F'])
  let reader = BitReader::new(data)
  inspect(reader.read_bits_signed(8), content="127")
}
