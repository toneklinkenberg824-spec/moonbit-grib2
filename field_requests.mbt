///|
/// Explicitly distinguish an unconstrained forecast from an encoded missing one.
pub(all) enum ForecastTimeFilter {
  AnyTime
  MissingTime
  ExactTime(Int)
} derive(Debug, Eq)

///|
/// Exact encoded metadata filters. Omitted optional filters are wildcards.
pub struct FieldQuery {
  discipline : Int
  category : Int
  parameter : Int
  centre : Int?
  subcentre : Int?
  master_table : Int?
  local_table : Int?
  time_unit : Int?
  forecast_time : Int?
  first_surface : Surface?
  second_surface : Surface?
  priv reference_time : Array[Int]?
  priv missing_forecast_time : Bool
}

///|
/// Reference components are copied. Surfaces compare original codes and scales;
/// no physical-unit or calendar conversion is performed.
pub fn FieldQuery::new(
  discipline : Int,
  category : Int,
  parameter : Int,
  centre? : Int,
  subcentre? : Int,
  master_table? : Int,
  local_table? : Int,
  time_unit? : Int,
  forecast_time? : Int,
  first_surface? : Surface,
  second_surface? : Surface,
  reference_time? : Array[Int],
) -> FieldQuery {
  {
    discipline,
    category,
    parameter,
    centre,
    subcentre,
    master_table,
    local_table,
    time_unit,
    forecast_time,
    first_surface,
    second_surface,
    reference_time: match reference_time {
      None => None
      Some(t) => Some(t.copy())
    },
    missing_forecast_time: false,
  }
}

///|
/// Return a refined query without mutating its layer/run filters or the original.
pub fn FieldQuery::with_forecast_time_filter(
  self : FieldQuery,
  filter : ForecastTimeFilter,
) -> FieldQuery {
  {
    ..self,
    forecast_time: match filter {
      ExactTime(t) => Some(t)
      AnyTime | MissingTime => None
    },
    missing_forecast_time: filter == MissingTime,
  }
}

///|
/// Inspect the effective criterion; the legacy optional integer remains readable.
pub fn FieldQuery::forecast_time_filter(
  self : FieldQuery,
) -> ForecastTimeFilter {
  match self.forecast_time {
    Some(t) => ExactTime(t)
    None => if self.missing_forecast_time { MissingTime } else { AnyTime }
  }
}

///|
fn FieldQuery::matches(self : FieldQuery, p : Product) -> Bool {
  let reference_matches = match self.reference_time {
    None => true
    Some(t) => t == p.reference_time
  }
  let forecast_matches = match self.forecast_time_filter() {
    AnyTime => true
    MissingTime => p.forecast_time is None
    ExactTime(t) => p.forecast_time == Some(t)
  }
  self.discipline == p.discipline &&
  self.category == p.category &&
  self.parameter == p.parameter &&
  (self.centre is None || self.centre == Some(p.centre)) &&
  (self.subcentre is None || self.subcentre == Some(p.subcentre)) &&
  (self.master_table is None || self.master_table == Some(p.master_table)) &&
  (self.local_table is None || self.local_table == Some(p.local_table)) &&
  (self.time_unit is None || self.time_unit == Some(p.time_unit)) &&
  forecast_matches &&
  (self.first_surface is None || self.first_surface == Some(p.first_surface)) &&
  (self.second_surface is None || self.second_surface == Some(p.second_surface)) &&
  reference_matches
}

///|
/// Reject absent or ambiguous matches rather than choosing an arbitrary record.
pub fn select_unique_field(
  fields : ArrayView[GriddedField],
  query : FieldQuery,
) -> Result[GriddedField, GribError] {
  if query.reference_time is Some(t) && t.length() != 6 {
    return Err(InvalidRequest("reference_time must contain six components"))
  }
  let mut selected : GriddedField? = None
  for f in fields {
    if query.matches(f.product_info) {
      if selected is Some(_) {
        return Err(InvalidRequest("query matches multiple fields"))
      }
      selected = Some(f)
    }
  }
  match selected {
    Some(f) => Ok(f)
    None => Err(InvalidRequest("no field matches query"))
  }
}

///|
pub(all) struct FieldRequest {
  key : String
  query : FieldQuery
}

///|
/// Named results retain selected-field identity even when the station list is empty.
pub(all) struct FieldSamples {
  key : String
  origin : Origin
  product : Product
  samples : Array[Sample]
} derive(ToJson)

///|
fn resolve_field_requests(
  fields : ArrayView[GriddedField],
  requests : ArrayView[FieldRequest],
) -> Result[Array[(String, GriddedField)], GribError] {
  let selected : Array[(String, GriddedField)] = []
  for i, r in requests {
    if r.key == "" {
      return Err(InvalidRequest("request key must be nonempty"))
    }
    for j in 0..<i {
      if requests[j].key == r.key {
        return Err(InvalidRequest("duplicate request key: " + r.key))
      }
    }
    match select_unique_field(fields, r.query) {
      Ok(f) => selected.push((r.key, f))
      Err(InvalidRequest(message)) =>
        return Err(InvalidRequest(r.key + ": " + message))
      Err(e) => return Err(e)
    }
  }
  Ok(selected)
}

///|
/// Resolve every uniquely named request before sampling. Any selection failure
/// fails the batch; valid spatial gaps remain explicit None values inside samples.
pub fn sample_requested_fields(
  fields : ArrayView[GriddedField],
  requests : ArrayView[FieldRequest],
  stations : ArrayView[Station],
) -> Result[Array[FieldSamples], GribError] {
  let selected = match resolve_field_requests(fields, requests) {
    Ok(selected) => selected
    Err(e) => return Err(e)
  }
  let out : Array[FieldSamples] = []
  for item in selected {
    let (key, f) = item
    out.push({
      key,
      origin: f.origin(),
      product: f.product(),
      samples: f.sample_stations(stations),
    })
  }
  Ok(out)
}
