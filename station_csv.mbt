///|
fn write_station_csv_row(
  out : StringBuilder,
  cells : ArrayView[String],
) -> Unit {
  for i, cell in cells {
    if i > 0 {
      out.write_char(',')
    }
    out.write_char('"')
    for c in cell.iter() {
      if c == '"' {
        out.write_char('"')
      }
      out.write_char(c)
    }
    out.write_char('"')
  }
  out.write_string("\r\n")
}

///|
fn write_station_csv_header(out : StringBuilder) -> Unit {
  write_station_csv_row(out, [
    "request_key", "station_id", "latitude", "longitude", "value", "algorithm", "message",
    "field", "byte_offset", "product_json", "contributors_json",
  ])
}

///|
fn write_station_csv_sample(
  out : StringBuilder,
  key : String,
  sample : Sample,
) -> Unit {
  write_station_csv_row(out, [
    key,
    sample.station.id,
    sample.station.latitude.to_string(),
    sample.station.longitude.to_string(),
    match sample.value {
      Some(v) => v.to_string()
      None => ""
    },
    sample.algorithm,
    sample.origin.message.to_string(),
    sample.origin.field.to_string(),
    sample.origin.byte_offset.to_string(),
    ToJson::to_json(sample.product).stringify(),
    sample.contributors.to_json().stringify(),
  ])
}

///|
/// One CSV row per station sample, preserving group/station order and provenance.
/// All cells are quoted; None numeric values are empty, while actual zero is0.
/// Metadata and contributors use the existing JSON representation inside cells.
pub fn station_results_csv(results : ArrayView[FieldSamples]) -> String {
  let out = StringBuilder()
  write_station_csv_header(out)
  for group in results {
    for sample in group.samples {
      write_station_csv_sample(out, group.key, sample)
    }
  }
  out.to_string()
}

///|
/// Header then complete CSV records, serialized lazily on next().
/// Keep input results unchanged while consuming; a record can contain quoted newlines.
pub fn station_csv_records(results : ArrayView[FieldSamples]) -> Iter[String] {
  let mut header_pending = true
  let mut group_index = 0
  let mut sample_index = 0
  Iter::new(fn() {
    if header_pending {
      header_pending = false
      let out = StringBuilder()
      write_station_csv_header(out)
      return Some(out.to_string())
    }
    while group_index < results.length() {
      let group = results[group_index]
      if sample_index < group.samples.length() {
        let out = StringBuilder()
        write_station_csv_sample(out, group.key, group.samples[sample_index])
        sample_index += 1
        return Some(out.to_string())
      }
      group_index += 1
      sample_index = 0
    }
    None
  })
}

///|
/// Resolve all requests now, then sample and serialize one station per next().
/// Keys/selected fields are captured; keep stations unchanged while consuming.
/// Decoded fields and the station list stay materialized; one record can be large.
pub fn sample_requested_csv_records(
  fields : ArrayView[GriddedField],
  requests : ArrayView[FieldRequest],
  stations : ArrayView[Station],
) -> Result[Iter[String], GribError] {
  let selected = match resolve_field_requests(fields, requests) {
    Ok(selected) => selected
    Err(e) => return Err(e)
  }
  let mut header_pending = true
  let mut group_index = 0
  let mut station_index = 0
  Ok(
    Iter::new(fn() {
      if header_pending {
        header_pending = false
        let out = StringBuilder()
        write_station_csv_header(out)
        return Some(out.to_string())
      }
      while group_index < selected.length() {
        if station_index < stations.length() {
          let (key, field) = selected[group_index]
          let sample = field.sample(stations[station_index])
          station_index += 1
          let out = StringBuilder()
          write_station_csv_sample(out, key, sample)
          return Some(out.to_string())
        }
        group_index += 1
        station_index = 0
      }
      None
    }),
  )
}
