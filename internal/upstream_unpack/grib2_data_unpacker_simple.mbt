// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
/// Simple Packing (Template 5.0) unpacker.
/// Local documentation correction: Y = (R + X * 2^E) / 10^D.
///
/// Where:
/// - Y = unpacked value
/// - R = reference_value (IEEE 754 single precision float)
/// - X = packed integer value
/// - E = binary_scale_factor (signed 16-bit)
/// - D = decimal_scale_factor (signed 16-bit)

///|
/// Result of unpacking grid data.
pub(all) struct UnpackedGridData {
  values : Array[Double]
  num_points : Int
}

///|
/// Error during unpacking.
pub(all) suberror UnpackError {
  InvalidBitsPerValue(String)
  InsufficientData(String)
  UnsupportedTemplate(String)
}

///|
/// Convert IEEE 754 single precision float bits to Double.
/// The input is 32-bit integer representing the float bit pattern.
pub fn ieee754_single_to_double(bits : Int) -> Double {
  // IEEE 754 single precision: 1 sign + 8 exponent + 23 mantissa
  let sign = (bits >> 31) & 1
  let exponent = (bits >> 23) & 0xFF
  let mantissa = bits & 0x7FFFFF
  if exponent == 0 && mantissa == 0 {
    // Zero
    if sign == 1 {
      -0.0
    } else {
      0.0
    }
  } else if exponent == 0xFF {
    // Infinity or NaN
    if mantissa == 0 {
      if sign == 1 {
        -1.0 / 0.0 // negative infinity
      } else {
        1.0 / 0.0 // positive infinity
      }
    } else {
      0.0 / 0.0 // NaN
    }
  } else if exponent == 0 {
    // Denormalized number
    let frac = mantissa.to_double() / 8388608.0 // 2^23
    let exp_val = -126.0
    let value = frac * pow2(exp_val.to_int())
    if sign == 1 {
      -value
    } else {
      value
    }
  } else {
    // Normalized number
    let frac = 1.0 + mantissa.to_double() / 8388608.0 // 1 + m/2^23
    let exp_val = exponent - 127
    let value = frac * pow2(exp_val)
    if sign == 1 {
      -value
    } else {
      value
    }
  }
}

///|
/// Compute 2^n for integer n (can be negative).
fn pow2(n : Int) -> Double {
  if n >= 0 {
    let mut result = 1.0
    for i = 0; i < n; i = i + 1 {
      result = result * 2.0
    }
    result
  } else {
    let mut result = 1.0
    for i = 0; i < -n; i = i + 1 {
      result = result / 2.0
    }
    result
  }
}

///|
/// Convert GRIB2 scale factor to signed integer.
/// GRIB2 uses sign-magnitude encoding (NOT two's complement):
/// - Bit 15 is sign: 0=positive, 1=negative
/// - Bits 0-14 are the magnitude
pub fn u16_to_i16(raw : Int) -> Int {
  let v = raw & 0xFFFF
  let sign_bit = v & 0x8000
  let magnitude = v & 0x7FFF
  if sign_bit != 0 {
    -magnitude
  } else {
    magnitude
  }
}

///|
/// Compute 10^n for integer n (can be negative).
fn pow10(n : Int) -> Double {
  if n >= 0 {
    let mut result = 1.0
    for i = 0; i < n; i = i + 1 {
      result = result * 10.0
    }
    result
  } else {
    let mut result = 1.0
    for i = 0; i < -n; i = i + 1 {
      result = result / 10.0
    }
    result
  }
}

///|
/// Unpack simple packed data (Template 5.0).
///
/// Parameters:
/// - data: Raw packed data bytes from Section 7
/// - reference_value_ieee: IEEE 754 bits of reference value
/// - binary_scale_factor: Binary scale factor E (signed)
/// - decimal_scale_factor: Decimal scale factor D (signed)
/// - bits_per_value: Number of bits per packed value
/// - num_points: Expected number of data points
pub fn unpack_simple(
  data : Bytes,
  reference_value_ieee : Int,
  binary_scale_factor : Int,
  decimal_scale_factor : Int,
  bits_per_value : Int,
  num_points : Int,
) -> Result[UnpackedGridData, UnpackError] {
  if bits_per_value < 0 || bits_per_value > 32 {
    return Err(
      InvalidBitsPerValue("bits_per_value must be 0-32, got \{bits_per_value}"),
    )
  }
  // Local repair: zero packed bits means X=0, not D=0. Apply the same
  // decimal scaling as WMO 92.9.4 / this module's simple-packing contract.
  if bits_per_value == 0 {
    let ref_value = ieee754_single_to_double(reference_value_ieee)
    let d = u16_to_i16(decimal_scale_factor)
    let constant = if d >= -300 && d <= 300 {
      ref_value / pow10(d)
    } else {
      // Same settled X=0 formula, with balanced factors at extreme scales.
      balanced_simple_value(ref_value, 0.0, 0, d)
    }
    let values = Array::make(num_points, constant)
    return Ok({ values, num_points, })
  }
  // Check if we have enough data
  let required_bits = num_points * bits_per_value
  let available_bits = data.length() * 8
  if available_bits < required_bits {
    return Err(
      InsufficientData("need \{required_bits} bits, have \{available_bits}"),
    )
  }
  // Calculate scaling factors
  let ref_value = ieee754_single_to_double(reference_value_ieee)
  let e = u16_to_i16(binary_scale_factor)
  let d = u16_to_i16(decimal_scale_factor)
  let ordinary = e >= -1022 && e <= 1023 && d >= -300 && d <= 300
  let binary_scale = if ordinary { pow2(e) } else { 1.0 }
  let decimal_scale = if ordinary { pow10(d) } else { 1.0 }
  // Unpack values
  let reader = BitReader::new(data)
  let values : Array[Double] = []
  for i = 0; i < num_points; i = i + 1 {
    let packed = reader.read_bits(bits_per_value)
    // GRIB2 formula: Y * 10^D = R + X * 2^E
    // Therefore: Y = (R + X * 2^E) / 10^D
    let numerator = ref_value + packed.to_double() * binary_scale
    let candidate = numerator / decimal_scale
    let unpacked = if ordinary &&
      !numerator.is_inf() &&
      !candidate.is_inf() &&
      !candidate.is_nan() {
      candidate
    } else {
      balanced_simple_value(ref_value, packed.to_double(), e, d)
    }
    values.push(unpacked)
  }
  Ok({ values, num_points, })
}

///|
test "ieee754_single_to_double zero" {
  // +0.0: 0x00000000
  inspect(ieee754_single_to_double(0x00000000), content="0")
  // -0.0: 0x80000000 = -2147483648 in signed int
  let neg_zero_bits : Int = -2147483648
  let neg_zero = ieee754_single_to_double(neg_zero_bits)
  inspect(neg_zero == 0.0, content="true")
}

///|
test "ieee754_single_to_double one" {
  // 1.0: 0x3F800000 = 1065353216
  inspect(ieee754_single_to_double(1065353216), content="1")
}

///|
test "ieee754_single_to_double negative" {
  // -1.0: 0xBF800000 = -1082130432 in signed int
  let bits : Int = -1082130432
  inspect(ieee754_single_to_double(bits), content="-1")
}

///|
test "ieee754_single_to_double two" {
  // 2.0: 0x40000000 = 1073741824
  inspect(ieee754_single_to_double(1073741824), content="2")
}

///|
test "unpack_simple all same value" {
  // bits_per_value = 0 means all values equal reference
  let data = Bytes::new(0)
  // 1.0 in IEEE 754: 0x3F800000 = 1065353216
  let result = unpack_simple(
    data, 1065353216, // 1.0
     0, // binary_scale
     0, // decimal_scale
     0, // bits_per_value
     3, // num_points
  )
  match result {
    Ok(grid) => {
      inspect(grid.num_points, content="3")
      inspect(grid.values[0], content="1")
      inspect(grid.values[1], content="1")
      inspect(grid.values[2], content="1")
    }
    Err(_) => fail("unexpected error")
  }
}

///|
test "unpack_simple basic" {
  // Pack values: 0, 1, 2, 3 with 2 bits each
  // ref = 10.0, E = 0, D = 0
  // Result should be: 10, 11, 12, 13
  let data = Bytes::from_array([b'\x1B'], // 00 01 10 11 = 0, 1, 2, 3
  )
  // 10.0 in IEEE 754: 0x41200000 = 1092616192
  let result = unpack_simple(
    data, 1092616192, // 10.0
     0, // binary_scale
     0, // decimal_scale
     2, // bits_per_value
     4, // num_points
  )
  match result {
    Ok(grid) => {
      inspect(grid.num_points, content="4")
      inspect(grid.values[0], content="10")
      inspect(grid.values[1], content="11")
      inspect(grid.values[2], content="12")
      inspect(grid.values[3], content="13")
    }
    Err(_) => fail("unexpected error")
  }
}
