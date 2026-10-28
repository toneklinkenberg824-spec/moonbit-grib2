from pathlib import Path
import json
P=Path(__file__).resolve().parents[3]
code=r"""///|
fn direct12_requests() -> Array[@grib2.FieldRequest] {
  let q = forecast09_query()
  [
    { key: " 未指定,\"时效\"\r\n组😀 ", query: q.with_forecast_time_filter(MissingTime) },
    { key: "分析0", query: q.with_forecast_time_filter(ExactTime(0)) },
    { key: "预报6", query: q.with_forecast_time_filter(ExactTime(6)) },
    { key: "负时效", query: q.with_forecast_time_filter(ExactTime(-6)) },
  ]
}

///|
test "direct12 records equal materialized missing zero positive negative pipeline" {
  let fields = forecast09_fields()
  let requests = direct12_requests()
  let stations : Array[@grib2.Station] = [
    { id: "站点,\"A\"\r\n第二行😀", latitude: 1.0, longitude: 10.0 },
    { id: "", latitude: 0.0, longitude: 10.5 },
    { id: "outside", latitude: 2.0, longitude: 10.0 },
  ]
  let expected = @grib2.station_results_csv(
    @grib2.sample_requested_fields(fields, requests, stations).unwrap(),
  )
  let chunks : Array[String] = []
  let out = StringBuilder()
  for chunk in @grib2.sample_requested_csv_records(fields, requests, stations).unwrap() {
    chunks.push(chunk)
    out.write_string(chunk)
  }
  assert_eq(chunks.length(), 13)
  assert_eq(out.to_string(), expected)
  assert_eq(requests[0].key, " 未指定,\"时效\"\r\n组😀 ")
  assert_eq(stations[0].id, "站点,\"A\"\r\n第二行😀")
  println("DIRECT12|chunks|" + chunks.to_json().stringify())
}

///|
fn direct12_error(
  fields : ArrayView[@grib2.GriddedField],
  requests : ArrayView[@grib2.FieldRequest],
  stations : ArrayView[@grib2.Station],
) -> String {
  match @grib2.sample_requested_csv_records(fields, requests, stations) {
    Err(InvalidRequest(message)) => message
    Err(_) => "unexpected error"
    Ok(_) => "unexpected iterator"
  }
}

///|
test "direct12 validates all requests before output including no stations" {
  let fields = forecast09_fields()
  let q = forecast09_query().with_forecast_time_filter(MissingTime)
  let station_sets : Array[Array[@grib2.Station]] = [
    [], [{ id: "inland", latitude: 0.0, longitude: 10.5 }],
  ]
  for stations in station_sets {
    assert_eq(direct12_error(fields, [{ key: "", query: q }], stations),
      "request key must be nonempty")
    assert_eq(direct12_error(fields, [{ key: "same", query: q }, { key: "same", query: q }], stations),
      "duplicate request key: same")
    assert_eq(direct12_error(fields, [{ key: "ok", query: q }, { key: "absent", query: @grib2.FieldQuery::new(0, 0, 1) }], stations),
      "absent: no field matches query")
    assert_eq(direct12_error(fields, [{ key: "ok", query: q }, { key: "ambiguous", query: forecast09_query() }], stations),
      "ambiguous: query matches multiple fields")
    assert_eq(direct12_error(fields, [{ key: "bad-time", query: @grib2.FieldQuery::new(0, 0, 0, reference_time=[2007]) }], stations),
      "bad-time: reference_time must contain six components")
    // Preserve per-request error precedence: an earlier selection error wins.
    assert_eq(direct12_error(fields, [{ key: "bad-first", query: forecast09_query() }, { key: "", query: q }], stations),
      "bad-first: query matches multiple fields")
    assert_eq(direct12_error([], [{ key: "absent", query: q }], stations),
      "absent: no field matches query")
  }
}

///|
test "direct12 captured selection survives array replacement and empty exhaustion" {
  let fields = forecast09_fields()
  let requests : Array[@grib2.FieldRequest] = [direct12_requests()[0]]
  let stations : Array[@grib2.Station] = [{ id: "inland", latitude: 0.0, longitude: 10.5 }]
  let expected = @grib2.station_results_csv(
    @grib2.sample_requested_fields(fields, requests, stations).unwrap(),
  )
  let records = @grib2.sample_requested_csv_records(fields, requests, stations).unwrap()
  fields[0] = fields[1]
  requests[0] = { key: "replaced", query: @grib2.FieldQuery::new(0, 0, 99) }
  let out = StringBuilder()
  for chunk in records { out.write_string(chunk) }
  assert_eq(out.to_string(), expected)
  assert_eq(records.next(), None)
  assert_eq(records.next(), None)
  println("DIRECT12|captured|" + out.to_string().to_json().stringify())
  let empty = @grib2.sample_requested_csv_records([], [], stations).unwrap()
  assert_eq(empty.next(), Some(@grib2.station_results_csv([])))
  assert_eq(empty.next(), None)
  assert_eq(empty.next(), None)
  let no_stations = @grib2.sample_requested_csv_records(forecast09_fields(), direct12_requests(), []).unwrap()
  assert_eq(no_stations.next(), Some(@grib2.station_results_csv([])))
  assert_eq(no_stations.next(), None)
  assert_eq(no_stations.next(), None)
}

///|
test "direct12 stop after first station without materializing10000 samples" {
  let fields = forecast09_fields()
  let requests : Array[@grib2.FieldRequest] = [direct12_requests()[0]]
  let stations : Array[@grib2.Station] = Array::make(10000, {
    id: "preview", latitude: 0.0, longitude: 10.5,
  })
  let a = @grib2.sample_requested_csv_records(fields, requests, stations).unwrap()
  let b = @grib2.sample_requested_csv_records(fields, requests, stations).unwrap()
  let header = a.next().unwrap()
  assert_eq(b.next(), Some(header))
  let first = a.next().unwrap()
  assert_eq(b.next(), Some(first))
  let expected = StringBuilder()
  expected.write_string(header)
  expected.write_string(first)
  assert_eq(expected.to_string(), @grib2.station_results_csv(
    @grib2.sample_requested_fields(fields, requests, stations[:1]).unwrap(),
  ))
  println("DIRECT12|prefix|" + [header, first].to_json().stringify())
  let stats : Json = {
    "prepared_stations": stations.length().to_json(),
    "consumed_records_per_iterator": (2).to_json(),
    "consumed_data_records_per_iterator": (1).to_json(),
  }
  println("DIRECT12|stats|" + stats.stringify())
  // Both iterators are intentionally left after the first data record.
}
"""
(P/'direct12_test.mbt').write_text(code,encoding='utf-8')
base=(P/'cmd/stream/main.mbt').read_text(encoding='utf-8')
base=base.replace('  let groups = @grib2.sample_requested_fields(fields, requests, stations).unwrap()\n  for chunk in @grib2.station_csv_records(groups) {', '  let records = @grib2.sample_requested_csv_records(fields, requests, stations).unwrap()\n  for chunk in records {')
assert 'station_csv_records(groups)' not in base
D=P/'cmd/direct';D.mkdir(exist_ok=True)
(D/'main.mbt').write_text(base,encoding='utf-8');(D/'moon.pkg').write_text((P/'cmd/stream/moon.pkg').read_text(encoding='utf-8'),encoding='utf-8')
