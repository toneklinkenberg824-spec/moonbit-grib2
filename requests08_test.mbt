///|
fn requests08_fields() -> Array[@grib2.GriddedField] {
  @grib2.read_fields(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x67\x00\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x8c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb4\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x06\x00\x7c\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x86\xa0\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x06\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x84\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x0c\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x89\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x01\x00\x0c\xf8\x50\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x87\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x07\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x88\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\x64\x00\x00\x01\x11\x70\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x86\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x01\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x88\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x05\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x89\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x01\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x43\x8a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37",
  ).unwrap()
}

///|
test "requests08 exact layer and run selection" {
  let fs = requests08_fields()
  let a = @grib2.select_unique_field(
    fs,
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
  ).unwrap()
  let b = @grib2.select_unique_field(
    fs,
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
  ).unwrap()
  assert_eq(a.origin().message, 0)
  assert_eq(a.get(1, 0), Some(280.0))
  assert_eq(b.origin().message, 1)
  assert_eq(b.get(1, 0), Some(270.0))
  assert_eq(
    @grib2.select_fields(fs, 0, 0, 0, time_unit=1, forecast_time=6).length(),
    10,
  )
  assert_true(
    @grib2.select_unique_field(fs, @grib2.FieldQuery::new(0, 0, 0))
    is Err(InvalidRequest(_)),
  )
}

///|
test "requests08 metadata dimensions and raw surface identity" {
  let fs = requests08_fields()
  let queries = [
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=7,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=1,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=5,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=1,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 100, scale: Some(0), scaled_value: Some(70000U), },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 6, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=12,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
    @grib2.FieldQuery::new(
      0,
      0,
      0,
      centre=98,
      subcentre=0,
      master_table=4,
      local_table=0,
      time_unit=1,
      forecast_time=6,
      reference_time=[2007, 3, 23, 12, 0, 0],
      first_surface={ kind: 100, scale: Some(1), scaled_value: Some(850000U), },
      second_surface={ kind: 255, scale: None, scaled_value: None, },
    ),
  ]
  let indices = [6, 8, 9, 10, 7, 3, 4, 5]
  let values = [272.0, 273.0, 274.0, 276.0, 269.0, 265.0, 275.0, 271.0]
  for i, q in queries {
    let f = @grib2.select_unique_field(fs, q).unwrap()
    assert_eq(f.origin().message, indices[i])
    assert_eq(f.get(1, 0), Some(values[i]))
  }
}

///|
test "requests08 absent and duplicate records fail explicitly" {
  let fs = requests08_fields()
  for
    q in [
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=2,
        forecast_time=6,
        reference_time=[2007, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=99,
        reference_time=[2007, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=6,
        reference_time=[2008, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
    ] {
    assert_true(@grib2.select_unique_field(fs, q) is Err(InvalidRequest(_)))
  }
  assert_true(
    @grib2.select_unique_field(
      [],
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=6,
        reference_time=[2007, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
    )
    is Err(InvalidRequest(_)),
  )
  let duplicate = @grib2.read_fields(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb4\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x06\x00\x7c\x00\x00\x00\x05\x07\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb4\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x64\x00\x00\x01\x4c\x08\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x06\x00\x7c\x00\x00\x00\x05\x07\x37\x37\x37\x37",
  ).unwrap()
  assert_true(
    @grib2.select_unique_field(
      duplicate,
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=6,
        reference_time=[2007, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
    )
    is Err(InvalidRequest(_)),
  )
}

///|
test "requests08 named batch preserves order missing and provenance" {
  let out = @grib2.sample_requested_fields(
    requests08_fields(),
    [
      {
        key: "t850",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={
            kind: 100,
            scale: Some(0),
            scaled_value: Some(85000U),
          },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
      {
        key: "t2m",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
    ],
    [
      { id: "gap", latitude: 1.0, longitude: 10.0, },
      { id: "inland", latitude: 0.0, longitude: 10.5, },
      { id: "outside", latitude: 2.0, longitude: 10.0, },
    ],
  ).unwrap()
  assert_eq(out[0].key, "t850")
  assert_eq(out[1].key, "t2m")
  assert_eq(out[0].origin.message, 1)
  assert_eq(out[0].samples[0].value, None)
  assert_eq(out[0].samples[1].value, Some(270.0))
  assert_eq(out[0].samples[2].value, None)
  assert_eq(out[1].samples[0].value, Some(280.0))
  let c = out[0].samples[1].contributors
  assert_eq(c.length(), 2)
  assert_eq(c[0].source_index, 3)
  assert_eq(c[1].source_index, 4)
  assert_eq(c[0].weight, 0.5)
  assert_eq(c[1].weight, 0.5)
  assert_eq(out[0].samples[0].contributors.length(), 0)
}

///|
test "requests08 batch selection is all or error" {
  let fs = requests08_fields()
  for
    bad in [
      @grib2.FieldQuery::new(0, 0, 0),
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=99,
        reference_time=[2007, 3, 23, 12, 0, 0],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
    ] {
    assert_true(
      @grib2.sample_requested_fields(
        fs,
        [
          {
            key: "ok",
            query: @grib2.FieldQuery::new(
              0,
              0,
              0,
              centre=98,
              subcentre=0,
              master_table=4,
              local_table=0,
              time_unit=1,
              forecast_time=6,
              reference_time=[2007, 3, 23, 12, 0, 0],
              first_surface={
                kind: 103,
                scale: Some(0),
                scaled_value: Some(2U),
              },
              second_surface={ kind: 255, scale: None, scaled_value: None, },
            ),
          },
          { key: "bad", query: bad, },
        ],
        [
          { id: "gap", latitude: 1.0, longitude: 10.0, },
          { id: "inland", latitude: 0.0, longitude: 10.5, },
          { id: "outside", latitude: 2.0, longitude: 10.0, },
        ],
      )
      is Err(InvalidRequest(_)),
    )
  }
  assert_true(
    @grib2.sample_requested_fields(
      fs,
      [
        {
          key: "same",
          query: @grib2.FieldQuery::new(
            0,
            0,
            0,
            centre=98,
            subcentre=0,
            master_table=4,
            local_table=0,
            time_unit=1,
            forecast_time=6,
            reference_time=[2007, 3, 23, 12, 0, 0],
            first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
            second_surface={ kind: 255, scale: None, scaled_value: None, },
          ),
        },
        {
          key: "same",
          query: @grib2.FieldQuery::new(
            0,
            0,
            0,
            centre=98,
            subcentre=0,
            master_table=4,
            local_table=0,
            time_unit=1,
            forecast_time=6,
            reference_time=[2007, 3, 23, 12, 0, 0],
            first_surface={
              kind: 100,
              scale: Some(0),
              scaled_value: Some(85000U),
            },
            second_surface={ kind: 255, scale: None, scaled_value: None, },
          ),
        },
      ],
      [],
    )
    is Err(InvalidRequest(_)),
  )
  assert_true(
    @grib2.sample_requested_fields(
      fs,
      [
        {
          key: "",
          query: @grib2.FieldQuery::new(
            0,
            0,
            0,
            centre=98,
            subcentre=0,
            master_table=4,
            local_table=0,
            time_unit=1,
            forecast_time=6,
            reference_time=[2007, 3, 23, 12, 0, 0],
            first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
            second_surface={ kind: 255, scale: None, scaled_value: None, },
          ),
        },
      ],
      [],
    )
    is Err(InvalidRequest(_)),
  )
}

///|
test "requests08 query and result metadata are detached" {
  let fs = requests08_fields()
  let time = [2007, 3, 23, 12, 0, 0]
  let q = @grib2.FieldQuery::new(
    0,
    0,
    0,
    centre=98,
    subcentre=0,
    master_table=4,
    local_table=0,
    time_unit=1,
    forecast_time=6,
    reference_time=time,
    first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
    second_surface={ kind: 255, scale: None, scaled_value: None, },
  )
  time[0] = 0
  assert_eq(@grib2.select_unique_field(fs, q).unwrap().origin().message, 1)
  assert_true(
    @grib2.select_unique_field(
      fs,
      @grib2.FieldQuery::new(
        0,
        0,
        0,
        centre=98,
        subcentre=0,
        master_table=4,
        local_table=0,
        time_unit=1,
        forecast_time=6,
        reference_time=[2007],
        first_surface={ kind: 100, scale: Some(0), scaled_value: Some(85000U), },
        second_surface={ kind: 255, scale: None, scaled_value: None, },
      ),
    )
    is Err(InvalidRequest(_)),
  )
  let out = @grib2.sample_requested_fields(
    fs,
    [
      {
        key: "t850",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={
            kind: 100,
            scale: Some(0),
            scaled_value: Some(85000U),
          },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
      {
        key: "t2m",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
    ],
    [
      { id: "gap", latitude: 1.0, longitude: 10.0, },
      { id: "inland", latitude: 0.0, longitude: 10.5, },
      { id: "outside", latitude: 2.0, longitude: 10.0, },
    ],
  ).unwrap()
  out[0].product.reference_time[0] = 0
  out[0].samples[1].product.reference_time[0] = 1
  assert_eq(fs[1].product().reference_time[0], 2007)
  assert_eq(out[1].product.reference_time[0], 2007)
}

///|
test "requests08 empty dimensions and named aliases" {
  assert_eq(@grib2.sample_requested_fields([], [], []).unwrap().length(), 0)
  let out = @grib2.sample_requested_fields(
    requests08_fields(),
    [
      {
        key: "t850",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={
            kind: 100,
            scale: Some(0),
            scaled_value: Some(85000U),
          },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
      {
        key: "t2m",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
    ],
    [],
  ).unwrap()
  assert_eq(out.length(), 2)
  assert_eq(out[0].samples.length(), 0)
  assert_eq(out[0].origin.message, 1)
  let named_aliases = @grib2.sample_requested_fields(
    requests08_fields(),
    [
      {
        key: "a",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
      {
        key: "b",
        query: @grib2.FieldQuery::new(
          0,
          0,
          0,
          centre=98,
          subcentre=0,
          master_table=4,
          local_table=0,
          time_unit=1,
          forecast_time=6,
          reference_time=[2007, 3, 23, 12, 0, 0],
          first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U), },
          second_surface={ kind: 255, scale: None, scaled_value: None, },
        ),
      },
    ],
    [
      { id: "gap", latitude: 1.0, longitude: 10.0, },
      { id: "inland", latitude: 0.0, longitude: 10.5, },
      { id: "outside", latitude: 2.0, longitude: 10.0, },
    ],
  ).unwrap()
  assert_eq(
    named_aliases[0].samples[0].value,
    named_aliases[1].samples[0].value,
  )
}
