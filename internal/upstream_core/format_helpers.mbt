// Adapted from trkbt10/grib2_mbt@00c30ee9a31adca0a15157f1b93ac7269415b9d3.
// Apache-2.0. Modified for this module; see THIRD_PARTY.md and UPSTREAM-LOCK.json.

///|
pub fn pad_zero(value : Int, width : Int) -> String {
  let s = value.to_string()
  if s.length() >= width {
    s
  } else {
    let mut result = ""
    for _ in 0..<(width - s.length()) {
      result = result + "0"
    }
    result + s
  }
}

///|
let hex_digits : Array[String] = [
  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f",
]

///|
pub fn hex_digit(value : Int) -> String {
  hex_digits[value & 0x0f]
}

///|
pub fn hex_byte(value : Byte) -> String {
  let u = value.to_uint().reinterpret_as_int()
  hex_digit((u >> 4) & 0x0f) + hex_digit(u & 0x0f)
}

///|
pub fn is_leap_year(year : Int) -> Bool {
  (year % 4 == 0 && year % 100 != 0) || year % 400 == 0
}

///|
pub fn days_in_month(year : Int, month : Int) -> Int {
  match month {
    1 => 31
    2 => if is_leap_year(year) { 29 } else { 28 }
    3 => 31
    4 => 30
    5 => 31
    6 => 30
    7 => 31
    8 => 31
    9 => 30
    10 => 31
    11 => 30
    12 => 31
    _ => 0
  }
}

///|
pub fn datetime_to_unix(
  year : Int,
  month : Int,
  day : Int,
  hour : Int,
  minute : Int,
  second : Int,
) -> Int64 {
  let mut days : Int64 = 0L
  for y in 1970..<year {
    days += if is_leap_year(y) { 366L } else { 365L }
  }
  for m in 1..<month {
    days += days_in_month(year, m).to_int64()
  }
  days += (day - 1).to_int64()
  days * 86400L +
  hour.to_int64() * 3600L +
  minute.to_int64() * 60L +
  second.to_int64()
}
