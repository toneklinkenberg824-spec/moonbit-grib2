// Local numeric adaptation for the reused GRIB2 unpacker; source reuse remains attributed.

///|
fn normalise_binary(value : Double, exponent : Int) -> (Double, Int) {
  if value == 0.0 {
    return (value, 0)
  }
  if value.is_nan() || value.is_inf() {
    return (value, exponent)
  }
  let mut m = value
  let mut e = exponent
  while m.abs() >= 2.0 {
    m *= 0.5
    e += 1
  }
  while m.abs() < 1.0 {
    m *= 2.0
    e -= 1
  }
  (m, e)
}

///|
/// Represent 10^-D without overflowing or rounding the factor to zero.
fn decimal_factor(d : Int) -> (Double, Int) {
  let mut n = if d < 0 { -d } else { d }
  let mut m = 1.0
  let mut e = 0
  let mut bm = 1.25 // 10 = 1.25 * 2^3, exactly.
  let mut be = 3
  while n > 0 {
    if n % 2 == 1 {
      let (next_m, next_e) = normalise_binary(m * bm, e + be)
      m = next_m
      e = next_e
    }
    n = n / 2
    if n > 0 {
      let (next_m, next_e) = normalise_binary(bm * bm, be + be)
      bm = next_m
      be = next_e
    }
  }
  if d > 0 {
    (1.0 / m, -e)
  } else {
    (m, e)
  }
}

///|
/// Preserve (R + X*2^E)*10^-D until the final binary64 scaling operation.
/// Normalisation keeps both mantissas finite even when the individual factors cannot be materialised.
fn balanced_simple_value(r : Double, x : Double, e : Int, d : Int) -> Double {
  let (rm, re) = normalise_binary(r, 0)
  let (xm, xe) = normalise_binary(x, e)
  let common = if rm == 0.0 {
    xe
  } else if xm == 0.0 {
    re
  } else if re > xe {
    re
  } else {
    xe
  }
  let sum = @math.scalbn(rm, re - common) + @math.scalbn(xm, xe - common)
  let (m, exponent) = normalise_binary(sum, common)
  let (factor, power) = decimal_factor(d)
  @math.scalbn(m * factor, exponent + power)
}
