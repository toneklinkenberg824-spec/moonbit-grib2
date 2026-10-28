///|
/// First blocking condition from per-station sampling, after decoding/selection.
pub(all) enum SampleFailure {
  InvalidStation
  OutsideGrid
  MissingData
  UnsupportedPolarVector
  NonFiniteResult
} derive(Debug, Eq)

///|
/// Stable application codes; no metadata or station values are altered.
pub impl ToJson for SampleFailure with fn to_json(self) {
  let code = match self {
    InvalidStation => "invalid-station"
    OutsideGrid => "outside-grid"
    MissingData => "missing-data"
    UnsupportedPolarVector => "unsupported-polar-vector"
    NonFiniteResult => "nonfinite-result"
  }
  code.to_json()
}

///|
/// Legacy missing-value representation over the same typed sampling kernel.
pub fn GriddedField::sample(self : GriddedField, station : Station) -> Sample {
  match self.sample_result(station) {
    Ok(sample) => sample
    Err(_) =>
      {
        station,
        origin: self.source,
        product: self.product(),
        value: None,
        algorithm: "outside-or-missing",
        contributors: [],
      }
  }
}
