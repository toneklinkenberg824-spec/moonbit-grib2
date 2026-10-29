///|
/// Calendar components under the opt-in fixed-day Gregorian forecast policy.
/// Years are 1..9999, days are 86400 seconds; leap seconds are not inserted.
pub(all) struct ValidTime {
  year : Int
  month : Int
  day : Int
  hour : Int
  minute : Int
  second : Int
} derive(Debug, Eq, ToJson)

///|
pub(all) enum ValidTimeError {
  MissingForecastTime
  UnsupportedTimeUnit(Int)
  InvalidReferenceTime
  UnsupportedLeapSecond
  TimeOutOfRange
} derive(Debug, Eq)

///|
fn valid_time_leap(year : Int) -> Bool {
  year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)
}

///|
fn valid_time_month_days(year : Int, month : Int) -> Int {
  match month {
    2 => if valid_time_leap(year) { 29 } else { 28 }
    4 | 6 | 9 | 11 => 30
    _ => 31
  }
}

///|
fn valid_time_before_year(year : Int) -> Int {
  let previous = year - 1
  previous * 365 + previous / 4 - previous / 100 + previous / 400
}

///|
/// Add a fixed-unit lead to the reference calendar components without changing
/// raw Product metadata or query matching. Supports units 0,1,2,10,11,12,13.
/// Error priority: missing lead, unsupported unit, invalid reference, explicit
/// leap second, then result outside years 1..9999. Calendar/local units fail.
/// This is civil arithmetic, not leap-second-aware physical elapsed UTC/TAI.
pub fn Product::valid_time(self : Product) -> Result[ValidTime, ValidTimeError] {
  let lead = match self.forecast_time {
    None => return Err(MissingForecastTime)
    Some(lead) => lead
  }
  let seconds_per_unit : Int64 = match self.time_unit {
    0 => 60L
    1 => 3600L
    2 => 86400L
    10 => 10800L
    11 => 21600L
    12 => 43200L
    13 => 1L
    unit => return Err(UnsupportedTimeUnit(unit))
  }
  let reference = self.reference_time
  if reference.length() != 6 {
    return Err(InvalidReferenceTime)
  }
  let year = reference[0]
  let month = reference[1]
  let day = reference[2]
  let hour = reference[3]
  let minute = reference[4]
  let second = reference[5]
  if year < 1 ||
    year > 9999 ||
    month < 1 ||
    month > 12 ||
    day < 1 ||
    day > valid_time_month_days(year, month) ||
    hour < 0 ||
    hour > 23 ||
    minute < 0 ||
    minute > 59 ||
    second < 0 ||
    second > 60 {
    return Err(InvalidReferenceTime)
  }
  if second == 60 {
    return Err(UnsupportedLeapSecond)
  }
  let mut reference_day = valid_time_before_year(year) + day - 1
  for prior_month = 1; prior_month < month; prior_month = prior_month + 1 {
    reference_day += valid_time_month_days(year, prior_month)
  }
  // Widen before every potentially large operation. |lead*factor| <= 2^31*86400,
  // while a validated reference is below 3652059*86400; both fit signed Int64.
  let target = reference_day.to_int64() * 86400L +
    (hour * 3600 + minute * 60 + second).to_int64() +
    lead.to_int64() * seconds_per_unit
  let exclusive_end = valid_time_before_year(10000).to_int64() * 86400L
  if target < 0L || target >= exclusive_end {
    return Err(TimeOutOfRange)
  }
  // Bounds above make these narrowings safe, including negative original leads.
  let target_day = (target / 86400L).to_int()
  let clock = (target % 86400L).to_int()
  let target_year = for low = 1, high = 10000; high - low > 1; {
    let middle = (low + high) / 2
    if valid_time_before_year(middle) <= target_day {
      continue middle, high
    } else {
      continue low, middle
    }
  } nobreak {
    low
  }
  let (target_month, target_date) = for month = 1, remaining = target_day -
                                          valid_time_before_year(target_year) {
    let count = valid_time_month_days(target_year, month)
    if remaining < count {
      break (month, remaining + 1)
    }
    continue month + 1, remaining - count
  }
  Ok({
    year: target_year,
    month: target_month,
    day: target_date,
    hour: clock / 3600,
    minute: clock % 3600 / 60,
    second: clock % 60,
  })
}
