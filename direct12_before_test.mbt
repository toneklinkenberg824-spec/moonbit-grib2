///|
test "direct12 before control eager samples precede CSV prefix" {
  let stations : Array[@grib2.Station] = Array::make(10000, {
    id: "preview",
    latitude: 0.0,
    longitude: 10.5,
  })
  let groups = @grib2.sample_requested_fields(
    forecast09_fields(),
    [
      {
        key: "missing",
        query: forecast09_query().with_forecast_time_filter(MissingTime),
      },
    ],
    stations,
  ).unwrap()
  assert_eq(groups[0].samples.length(), 10000)
  let records = @grib2.station_csv_records(groups)
  assert_true(records.next() is Some(_))
  assert_true(records.next() is Some(_))
  println("DIRECT12_BEFORE|" + groups[0].samples.length().to_string())
}
