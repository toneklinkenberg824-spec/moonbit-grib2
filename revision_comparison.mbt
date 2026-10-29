///|
/// Encoded compatibility failures, checked before any station is sampled.
pub(all) enum FieldComparisonError {
  ParameterMismatch
  TableMismatch
  SurfaceMismatch
  LeftTime(ValidTimeError)
  RightTime(ValidTimeError)
  ValidTimeMismatch
} derive(Debug, Eq)

///|
pub(all) enum DifferenceFailure {
  SamplingUnavailable
  NonFiniteDifference
} derive(Debug, Eq)

///|
/// Both original sampling outcomes are retained, including independent failures.
pub(all) struct StationDifference {
  station : Station
  left : Result[Sample, SampleFailure]
  right : Result[Sample, SampleFailure]
  difference : Result[Double, DifferenceFailure]
} derive(Debug)

///|
fn comparison_time_error(error : ValidTimeError) -> Json {
  match error {
    MissingForecastTime => { "code": "missing-forecast-time" }
    UnsupportedTimeUnit(unit) =>
      { "code": "unsupported-time-unit", "unit": unit.to_json() }
    InvalidReferenceTime => { "code": "invalid-reference-time" }
    UnsupportedLeapSecond => { "code": "unsupported-leap-second" }
    TimeOutOfRange => { "code": "out-of-range" }
  }
}

///|
pub impl ToJson for FieldComparisonError with fn to_json(self) {
  match self {
    ParameterMismatch => { "code": "parameter-mismatch" }
    TableMismatch => { "code": "table-mismatch" }
    SurfaceMismatch => { "code": "surface-mismatch" }
    LeftTime(reason) =>
      { "code": "left-time", "reason": comparison_time_error(reason) }
    RightTime(reason) =>
      { "code": "right-time", "reason": comparison_time_error(reason) }
    ValidTimeMismatch => { "code": "valid-time-mismatch" }
  }
}

///|
pub impl ToJson for DifferenceFailure with fn to_json(self) {
  match self {
    SamplingUnavailable => "sampling-unavailable".to_json()
    NonFiniteDifference => "nonfinite-difference".to_json()
  }
}

///|
fn comparison_sample_json(value : Result[Sample, SampleFailure]) -> Json {
  match value {
    Ok(sample) => { "sample": sample.to_json() }
    Err(reason) => { "failure": reason.to_json() }
  }
}

///|
pub impl ToJson for StationDifference with fn to_json(self) {
  let difference : Json = match self.difference {
    Ok(value) => { "value": value.to_json() }
    Err(reason) => { "error": reason.to_json() }
  }
  {
    "station": self.station.to_json(),
    "left": comparison_sample_json(self.left),
    "right": comparison_sample_json(self.right),
    "difference": difference,
  }
}

///|
/// Compare independently sampled values as right minus left at each station.
/// Requires equal parameter, centre/table and exact surface codes, then equal
/// existing valid civil time; checks apply even to an empty station list.
/// This is an encoded compatibility screen, not physical calibration or model
/// equivalence. Grids may differ; no grid subtraction/regridding is performed.
/// Both sampling failures survive; a nonfinite subtraction is an explicit row
/// error. Raw metadata, sample weights and all existing time semantics remain.
pub fn GriddedField::compare_stations(
  self : GriddedField,
  right : GriddedField,
  stations : ArrayView[Station],
) -> Result[Array[StationDifference], FieldComparisonError] {
  let a = self.product()
  let b = right.product()
  if a.discipline != b.discipline ||
    a.category != b.category ||
    a.parameter != b.parameter {
    return Err(ParameterMismatch)
  }
  if a.centre != b.centre ||
    a.subcentre != b.subcentre ||
    a.master_table != b.master_table ||
    a.local_table != b.local_table {
    return Err(TableMismatch)
  }
  if a.first_surface != b.first_surface || a.second_surface != b.second_surface {
    return Err(SurfaceMismatch)
  }
  let left_time = match a.valid_time() {
    Ok(time) => time
    Err(error) => return Err(LeftTime(error))
  }
  let right_time = match b.valid_time() {
    Ok(time) => time
    Err(error) => return Err(RightTime(error))
  }
  if left_time != right_time {
    return Err(ValidTimeMismatch)
  }
  let rows : Array[StationDifference] = []
  for station in stations {
    let left_sample = self.sample_result(station)
    let right_sample = right.sample_result(station)
    let difference = match (left_sample, right_sample) {
      (Ok(left), Ok(right)) => {
        let value = right.value.unwrap() - left.value.unwrap()
        if finite(value) {
          Ok(value)
        } else {
          Err(NonFiniteDifference)
        }
      }
      _ => Err(SamplingUnavailable)
    }
    rows.push({ station, left: left_sample, right: right_sample, difference, })
  }
  Ok(rows)
}
