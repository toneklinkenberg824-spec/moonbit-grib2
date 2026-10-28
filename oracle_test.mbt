// Generated from ecCodes 2.50.0 / SciPy references, not from product output.

///|
test "oracle scan000.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -5.0, -4.875, -4.75, -4.625, -4.5, -4.375, -4.25, -4.125, -4.0, -3.875, -3.75,
    -3.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan000.grib2|" + max_abs.to_string())
}

///|
test "oracle scan016.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x10\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -5.0, -4.875, -4.75, -4.625, -4.125, -4.25, -4.375, -4.5, -4.0, -3.875, -3.75,
    -3.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan016.grib2|" + max_abs.to_string())
}

///|
test "oracle scan032.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x20\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -5.0, -4.625, -4.25, -3.875, -4.875, -4.5, -4.125, -3.75, -4.75, -4.375, -4.0,
    -3.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan032.grib2|" + max_abs.to_string())
}

///|
test "oracle scan048.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x30\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -5.0, -4.375, -4.25, -3.625, -4.875, -4.5, -4.125, -3.75, -4.75, -4.625, -4.0,
    -3.875,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 5, 6, 11, 1, 4, 7, 10, 2, 3, 8, 9]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan048.grib2|" + max_abs.to_string())
}

///|
test "oracle scan064.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x00\x00\x00\x00\x30\x05\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x40\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.0, -3.875, -3.75, -3.625, -4.5, -4.375, -4.25, -4.125, -5.0, -4.875, -4.75,
    -4.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan064.grib2|" + max_abs.to_string())
}

///|
test "oracle scan080.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x00\x00\x00\x00\x30\x05\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x50\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.0, -3.875, -3.75, -3.625, -4.125, -4.25, -4.375, -4.5, -5.0, -4.875, -4.75,
    -4.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [8, 9, 10, 11, 7, 6, 5, 4, 0, 1, 2, 3]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan080.grib2|" + max_abs.to_string())
}

///|
test "oracle scan096.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x00\x00\x00\x00\x30\x05\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x60\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.75, -4.375, -4.0, -3.625, -4.875, -4.5, -4.125, -3.75, -5.0, -4.625, -4.25,
    -3.875,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [2, 5, 8, 11, 1, 4, 7, 10, 0, 3, 6, 9]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan096.grib2|" + max_abs.to_string())
}

///|
test "oracle scan112.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x00\x00\x00\x00\x30\x05\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x70\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.75, -4.625, -4.0, -3.875, -4.875, -4.5, -4.125, -3.75, -5.0, -4.375, -4.25,
    -3.625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [2, 3, 8, 9, 1, 4, 7, 10, 0, 5, 6, 11]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan112.grib2|" + max_abs.to_string())
}

///|
test "oracle scan128.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x10\x17\xdf\x80\x30\x85\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x80\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.625, -4.75, -4.875, -5.0, -4.125, -4.25, -4.375, -4.5, -3.625, -3.75, -3.875,
    -4.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan128.grib2|" + max_abs.to_string())
}

///|
test "oracle scan144.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x10\x17\xdf\x80\x30\x85\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x90\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -4.625, -4.75, -4.875, -5.0, -4.5, -4.375, -4.25, -4.125, -3.625, -3.75, -3.875,
    -4.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [3, 2, 1, 0, 4, 5, 6, 7, 11, 10, 9, 8]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan144.grib2|" + max_abs.to_string())
}

///|
test "oracle scan160.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x10\x17\xdf\x80\x30\x85\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xa0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.875, -4.25, -4.625, -5.0, -3.75, -4.125, -4.5, -4.875, -3.625, -4.0, -4.375,
    -4.75,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [9, 6, 3, 0, 10, 7, 4, 1, 11, 8, 5, 2]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan160.grib2|" + max_abs.to_string())
}

///|
test "oracle scan176.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x10\x17\xdf\x80\x30\x85\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xb0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.625, -4.25, -4.375, -5.0, -3.75, -4.125, -4.5, -4.875, -3.875, -4.0, -4.625,
    -4.75,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [11, 6, 5, 0, 10, 7, 4, 1, 9, 8, 3, 2]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan176.grib2|" + max_abs.to_string())
}

///|
test "oracle scan192.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x10\x17\xdf\x80\x30\x05\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xc0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.625, -3.75, -3.875, -4.0, -4.125, -4.25, -4.375, -4.5, -4.625, -4.75, -4.875,
    -5.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan192.grib2|" + max_abs.to_string())
}

///|
test "oracle scan208.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x10\x17\xdf\x80\x30\x05\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xd0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.625, -3.75, -3.875, -4.0, -4.5, -4.375, -4.25, -4.125, -4.625, -4.75, -4.875,
    -5.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [11, 10, 9, 8, 4, 5, 6, 7, 3, 2, 1, 0]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan208.grib2|" + max_abs.to_string())
}

///|
test "oracle scan224.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc7\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x10\x17\xdf\x80\x30\x05\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xe0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x19\x07\x00\x00\x80\x08\x00\x60\x04\x00\x28\x01\x80\x0e\x00\x80\x04\x80\x28\x01\x60\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.625, -4.0, -4.375, -4.75, -3.75, -4.125, -4.5, -4.875, -3.875, -4.25, -4.625,
    -5.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [11, 8, 5, 2, 10, 7, 4, 1, 9, 6, 3, 0]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan224.grib2|" + max_abs.to_string())
}

///|
test "oracle scan240.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x10\x17\xdf\x80\x30\x05\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xf0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0a\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x08\x06\x00\xde\xf0\x00\x00\x00\x16\x07\x00\x00\x80\x0c\x00\x80\x05\x00\x30\x02\x00\x12\x00\xa0\x05\x80\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(6))

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    -3.875, -4.0, -4.625, 0.0, -3.75, 0.0, -4.5, -4.875, -3.625, -4.25, -4.375, -5.0,
  ]
  let valid = [
    true, true, true, false, true, false, true, true, true, true, true, true,
  ]
  let source = [9, 8, 3, 2, 10, 7, 4, 1, 11, 6, 5, 0]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scan240.grib2|" + max_abs.to_string())
}

///|
test "oracle bitmap.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x3f\x80\x00\x00\x80\x03\x00\x00\x11\x00\x00\x00\x00\x07\x06\x00\xbc\x00\x00\x00\x10\x07\x00\x00\x4e\x1c\x00\x03\x00\x02\x00\x01\x40\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 2)
  assert_eq(f.cols(), 3)
  let expected : Array[Double] = [1.0, 0.0, 9999.0, 4.0, 5.0, 6.0]
  let valid = [true, false, true, true, true, true]
  let source = [0, 1, 2, 3, 4, 5]
  let latitudes : Array[Double] = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
  let longitudes : Array[Double] = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0]
  let mut max_abs = 0.0
  for r in 0..<2 {
    for c in 0..<3 {
      let i = r * 3 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|bitmap.grib2|" + max_abs.to_string())
}

///|
test "oracle constant.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x40\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 2)
  assert_eq(f.cols(), 3)
  let expected : Array[Double] = [7.0, 7.0, 7.0, 7.0, 7.0, 7.0]
  let valid = [true, true, true, true, true, true]
  let source = [0, 1, 2, 3, 4, 5]
  let latitudes : Array[Double] = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
  let longitudes : Array[Double] = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0]
  let mut max_abs = 0.0
  for r in 0..<2 {
    for c in 0..<3 {
      let i = r * 3 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|constant.grib2|" + max_abs.to_string())
}

///|
test "oracle negative-scale.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xbb\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\xc3\xa0\x80\x00\x00\x00\x00\x02\x0a\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x0d\x07\x00\x06\xf3\x6d\x42\x8b\xad\x20\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 2)
  assert_eq(f.cols(), 3)
  let expected : Array[Double] = [-3.21, -2.1, -1.02, 0.01, 2.37, 4.01]
  let valid = [true, true, true, true, true, true]
  let source = [0, 1, 2, 3, 4, 5]
  let latitudes : Array[Double] = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
  let longitudes : Array[Double] = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0]
  let mut max_abs = 0.0
  for r in 0..<2 {
    for c in 0..<3 {
      let i = r * 3 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|negative-scale.grib2|" + max_abs.to_string())
}

///|
test "oracle scipy.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xcd\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x00\x1e\x84\x80\x00\x00\x00\x00\x30\x00\x00\x00\x00\x10\x17\xdf\x80\x05\x5d\x4a\x80\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\x40\x40\x00\x00\x80\x0c\x00\x00\x11\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x1f\x07\xa0\x00\x54\x00\x2c\x00\x17\x00\x05\x00\x02\xc0\x01\x80\x00\xd0\x00\x00\x00\x04\x00\x04\x00\x03\x00\x00\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    23.0, 24.0, 25.0, 26.0, 13.0, 14.0, 15.0, 16.0, 3.0, 4.0, 5.0, 6.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  let latitudes : Array[Double] = [
    2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|scipy.grib2|" + max_abs.to_string())
}

///|
test "oracle polar.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xcd\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x80\x0c\x00\x00\x11\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x1f\x07\x00\x00\x08\x00\x08\x00\x06\x00\x05\x00\x03\x00\x01\xc0\x01\x00\x00\xa0\x00\x58\x00\x30\x00\x1a\x00\x00\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 3)
  assert_eq(f.cols(), 4)
  let expected : Array[Double] = [
    0.0, 2.0, 4.0, 6.0, 10.0, 12.0, 14.0, 16.0, 20.0, 22.0, 24.0, 26.0,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true,
  ]
  let source = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  let latitudes : Array[Double] = [
    90.0, 90.0, 90.0, 90.0, 0.0, 0.0, 0.0, 0.0, -90.0, -90.0, -90.0, -90.0,
  ]
  let longitudes : Array[Double] = [
    0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0, 0.0, 90.0, 180.0, 270.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<3 {
    for c in 0..<4 {
      let i = r * 4 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|polar.grib2|" + max_abs.to_string())
}

///|
test "oracle max-width.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xcb\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x1d\x07\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\x04\x00\x37\x37\x37\x37",
  ).unwrap()

  assert_eq(f.rows(), 2)
  assert_eq(f.cols(), 3)
  let expected : Array[Double] = [
    0.0, 1.0, 2.0, 4294967295.0, 2147483648.0, 1024.0,
  ]
  let valid = [true, true, true, true, true, true]
  let source = [0, 1, 2, 3, 4, 5]
  let latitudes : Array[Double] = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
  let longitudes : Array[Double] = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0]
  let mut max_abs = 0.0
  for r in 0..<2 {
    for c in 0..<3 {
      let i = r * 3 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|max-width.grib2|" + max_abs.to_string())
}

///|
test "oracle noaa-gfs-repacked.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\x15\x01\x00\x07\x00\x00\x02\x01\x01\x07\xea\x02\x15\x00\x00\x00\x00\x01\x00\x00\x00\x48\x03\x00\x00\x00\x00\x30\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x06\x00\x00\x00\x00\xff\xff\xff\xff\x04\x2c\x1d\x80\x01\xc9\xc3\x80\x30\x03\xdf\xd2\x40\x02\x34\x93\x40\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x02\x00\x51\x00\x00\x00\x01\x00\x00\x00\x00\x67\x00\x00\x00\x00\x02\xff\x00\x00\x00\x00\x00\x00\x00\x00\x15\x05\x00\x00\x00\x30\x00\x00\x46\xc0\xfe\xb2\x00\x00\x00\x02\x0c\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x4d\x07\x72\x37\x4e\x7d\x77\x77\x80\x38\x35\x86\xc8\xab\x12\xe2\x32\x2c\xd2\xbf\x3e\x53\x9e\x48\x47\xb7\x00\x01\x9e\x39\x53\x14\x2d\xd2\xdc\x4b\x06\x17\x13\x12\x3a\x36\x53\x59\x1c\x93\xc3\x66\x16\x77\x34\x22\xdb\x24\xb2\x06\x2a\xf6\x2f\x7e\x27\xc1\x21\x11\x4a\x13\x81\x37\x2d\xe5\x97\x71\xc6\xf4\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().discipline, 0)
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(0))

  assert_eq(f.rows(), 6)
  assert_eq(f.cols(), 8)
  let expected : Array[Double] = [
    265.3034765625, 265.7334765625, 267.1034765625, 266.1434765625, 267.5434765625,
    268.0434765625, 268.59347656250003, 269.2234765625, 250.0534765625, 252.6534765625,
    254.20347656250001, 254.0634765625, 257.0034765625, 256.2934765625, 258.59347656250003,
    266.7834765625, 247.0334765625, 251.1734765625, 256.2034765625, 254.9134765625,
    254.3634765625, 254.3534765625, 259.0334765625, 262.6234765625, 250.0834765625,
    252.73347656250002, 255.7234765625, 255.6034765625, 251.6034765625, 256.6634765625,
    263.3634765625, 263.5834765625, 255.3734765625, 254.3434765625, 252.9034765625,
    252.2134765625, 253.9034765625, 262.8634765625, 267.2134765625, 266.8834765625,
    252.32347656250002, 250.3334765625, 250.1534765625, 250.1434765625, 254.3734765625,
    261.34347656250003, 265.2334765625, 264.8334765625,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true,
  ]
  let source = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
    42, 43, 44, 45, 46, 47,
  ]
  let latitudes : Array[Double] = [
    70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 70.0, 69.0, 69.0, 69.0, 69.0, 69.0,
    69.0, 69.0, 69.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 68.0, 67.0, 67.0,
    67.0, 67.0, 67.0, 67.0, 67.0, 67.0, 66.0, 66.0, 66.0, 66.0, 66.0, 66.0, 66.0,
    66.0, 65.0, 65.0, 65.0, 65.0, 65.0, 65.0, 65.0, 65.0,
  ]
  let longitudes : Array[Double] = [
    30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 30.0, 31.0, 32.0, 33.0, 34.0,
    35.0, 36.0, 37.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 30.0, 31.0,
    32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0,
    37.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0,
  ]
  let mut max_abs = 0.0
  for r in 0..<6 {
    for c in 0..<8 {
      let i = r * 8 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|noaa-gfs-repacked.grib2|" + max_abs.to_string())
}

///|
test "real field to SciPy station chain noaa-gfs-repacked.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\x15\x01\x00\x07\x00\x00\x02\x01\x01\x07\xea\x02\x15\x00\x00\x00\x00\x01\x00\x00\x00\x48\x03\x00\x00\x00\x00\x30\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x06\x00\x00\x00\x00\xff\xff\xff\xff\x04\x2c\x1d\x80\x01\xc9\xc3\x80\x30\x03\xdf\xd2\x40\x02\x34\x93\x40\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x02\x00\x51\x00\x00\x00\x01\x00\x00\x00\x00\x67\x00\x00\x00\x00\x02\xff\x00\x00\x00\x00\x00\x00\x00\x00\x15\x05\x00\x00\x00\x30\x00\x00\x46\xc0\xfe\xb2\x00\x00\x00\x02\x0c\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x4d\x07\x72\x37\x4e\x7d\x77\x77\x80\x38\x35\x86\xc8\xab\x12\xe2\x32\x2c\xd2\xbf\x3e\x53\x9e\x48\x47\xb7\x00\x01\x9e\x39\x53\x14\x2d\xd2\xdc\x4b\x06\x17\x13\x12\x3a\x36\x53\x59\x1c\x93\xc3\x66\x16\x77\x34\x22\xdb\x24\xb2\x06\x2a\xf6\x2f\x7e\x27\xc1\x21\x11\x4a\x13\x81\x37\x2d\xe5\x97\x71\xc6\xf4\x37\x37\x37\x37",
  ).unwrap()
  let queries : Array[(Double, Double)] = [(68.25, 31.5), (67.0, 33.0)]
  let expected : Array[Double] = [253.6234765625, 255.6034765625]
  for i, (lat, lon) in queries {
    assert_true(
      (f.interpolate_latlon(lat, lon).unwrap() - expected[i]).abs() < 1.0e-9,
    )
  }
}

///|
test "oracle ecmwf-ifs-repacked.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x01\x0c\x00\x00\x00\x15\x01\x00\x62\x00\x00\x20\x00\x01\x07\xea\x02\x15\x00\x00\x00\x00\x01\x00\x00\x00\x11\x02\x00\x01\x00\x01\x00\x09\x04\x01\x30\x30\x30\x31\x00\x00\x00\x48\x03\x00\x00\x00\x00\x30\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x08\x00\x00\x00\x06\x00\x00\x00\x00\xff\xff\xff\xff\x05\x10\xff\x40\x0b\x2d\x05\xe0\x30\x04\xfd\xec\x70\x0b\x47\xb9\xd0\x00\x03\xd0\x90\x00\x03\xd0\x90\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x02\xff\x9e\x00\x00\x00\x01\x00\x00\x00\x00\x67\x00\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x30\x00\x00\x43\x6f\x70\x22\x80\x0b\x00\x00\x0c\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x4d\x07\x80\x08\x40\x88\x08\xc0\x90\x09\x40\x94\x09\x80\x50\x05\x00\x54\x05\x40\x58\x05\x80\x58\x05\xc0\x28\x02\xc0\x2c\x02\xc0\x30\x03\x00\x38\x03\xc0\x20\x02\x40\x24\x02\x80\x28\x02\xc0\x2c\x02\xc0\x0c\x01\x00\x10\x01\x00\x10\x01\x00\x10\x01\x00\x00\x00\x00\x04\x00\x40\x04\x00\x40\x08\x00\x80\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.product().discipline, 0)
  assert_eq(f.product().category, 0)
  assert_eq(f.product().parameter, 0)
  assert_eq(f.product().time_unit, 1)
  assert_eq(f.product().forecast_time, Some(0))

  assert_eq(f.rows(), 6)
  assert_eq(f.cols(), 8)
  let expected : Array[Double] = [
    240.43801879882812, 240.46926879882812, 240.50051879882812, 240.53176879882812,
    240.56301879882812, 240.59426879882812, 240.59426879882812, 240.62551879882812,
    240.06301879882812, 240.06301879882812, 240.09426879882812, 240.09426879882812,
    240.12551879882812, 240.12551879882812, 240.12551879882812, 240.15676879882812,
    239.75051879882812, 239.78176879882812, 239.78176879882812, 239.78176879882812,
    239.81301879882812, 239.81301879882812, 239.87551879882812, 239.90676879882812,
    239.68801879882812, 239.71926879882812, 239.71926879882812, 239.75051879882812,
    239.75051879882812, 239.78176879882812, 239.78176879882812, 239.78176879882812,
    239.53176879882812, 239.56301879882812, 239.56301879882812, 239.56301879882812,
    239.56301879882812, 239.56301879882812, 239.56301879882812, 239.56301879882812,
    239.43801879882812, 239.43801879882812, 239.46926879882812, 239.46926879882812,
    239.46926879882812, 239.46926879882812, 239.50051879882812, 239.50051879882812,
  ]
  let valid = [
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true, true, true, true, true,
    true, true, true, true, true, true, true, true, true,
  ]
  let source = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
    42, 43, 44, 45, 46, 47,
  ]
  let latitudes : Array[Double] = [
    85.0, 85.0, 85.0, 85.0, 85.0, 85.0, 85.0, 85.0, 84.75, 84.75, 84.75, 84.75, 84.75,
    84.75, 84.75, 84.75, 84.5, 84.5, 84.5, 84.5, 84.5, 84.5, 84.5, 84.5, 84.25, 84.25,
    84.25, 84.25, 84.25, 84.25, 84.25, 84.25, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0,
    84.0, 84.0, 83.75, 83.75, 83.75, 83.75, 83.75, 83.75, 83.75, 83.75,
  ]
  let longitudes : Array[Double] = [
    187.5, 187.75, 188.0, 188.25, 188.5, 188.75, 189.0, 189.25, 187.5, 187.75, 188.0,
    188.25, 188.5, 188.75, 189.0, 189.25, 187.5, 187.75, 188.0, 188.25, 188.5, 188.75,
    189.0, 189.25, 187.5, 187.75, 188.0, 188.25, 188.5, 188.75, 189.0, 189.25, 187.5,
    187.75, 188.0, 188.25, 188.5, 188.75, 189.0, 189.25, 187.5, 187.75, 188.0, 188.25,
    188.5, 188.75, 189.0, 189.25,
  ]
  let mut max_abs = 0.0
  for r in 0..<6 {
    for c in 0..<8 {
      let i = r * 8 + c
      let p = f.point(r, c).unwrap()
      assert_eq(p.source_index, source[i])
      assert_true((p.latitude - latitudes[i]).abs() < 0.000002)
      assert_true((p.longitude - longitudes[i]).abs() < 0.000002)
      assert_eq(f.mask()[i], valid[i])
      if valid[i] {
        let error = (f.get(r, c).unwrap() - expected[i]).abs()
        if error > max_abs {
          max_abs = error
        }
        assert_true(error <= 1.0e-10 + expected[i].abs() * 1.0e-12)
      } else {
        assert_eq(f.get(r, c), None)
        assert_true(f.values()[i].is_nan())
      }
    }
  }
  println("GRIB_METRIC|ecmwf-ifs-repacked.grib2|" + max_abs.to_string())
}

///|
test "real field to SciPy station chain ecmwf-ifs-repacked.grib2" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x01\x0c\x00\x00\x00\x15\x01\x00\x62\x00\x00\x20\x00\x01\x07\xea\x02\x15\x00\x00\x00\x00\x01\x00\x00\x00\x11\x02\x00\x01\x00\x01\x00\x09\x04\x01\x30\x30\x30\x31\x00\x00\x00\x48\x03\x00\x00\x00\x00\x30\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x08\x00\x00\x00\x06\x00\x00\x00\x00\xff\xff\xff\xff\x05\x10\xff\x40\x0b\x2d\x05\xe0\x30\x04\xfd\xec\x70\x0b\x47\xb9\xd0\x00\x03\xd0\x90\x00\x03\xd0\x90\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x02\xff\x9e\x00\x00\x00\x01\x00\x00\x00\x00\x67\x00\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x30\x00\x00\x43\x6f\x70\x22\x80\x0b\x00\x00\x0c\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x4d\x07\x80\x08\x40\x88\x08\xc0\x90\x09\x40\x94\x09\x80\x50\x05\x00\x54\x05\x40\x58\x05\x80\x58\x05\xc0\x28\x02\xc0\x2c\x02\xc0\x30\x03\x00\x38\x03\xc0\x20\x02\x40\x24\x02\x80\x28\x02\xc0\x2c\x02\xc0\x0c\x01\x00\x10\x01\x00\x10\x01\x00\x10\x01\x00\x00\x00\x00\x04\x00\x40\x04\x00\x40\x08\x00\x80\x37\x37\x37\x37",
  ).unwrap()
  let queries : Array[(Double, Double)] = [(84.5625, 187.875), (84.25, 188.25)]
  let expected : Array[Double] = [239.85598754882812, 239.75051879882812]
  for i, (lat, lon) in queries {
    assert_true(
      (f.interpolate_latlon(lat, lon).unwrap() - expected[i]).abs() < 1.0e-9,
    )
  }
}

///|
test "independent SciPy periodic scalar samples and provenance" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xcd\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x00\x1e\x84\x80\x00\x00\x00\x00\x30\x00\x00\x00\x00\x10\x17\xdf\x80\x05\x5d\x4a\x80\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\x40\x40\x00\x00\x80\x0c\x00\x00\x11\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x1f\x07\xa0\x00\x54\x00\x2c\x00\x17\x00\x05\x00\x02\xc0\x01\x80\x00\xd0\x00\x00\x00\x04\x00\x04\x00\x03\x00\x00\x37\x37\x37\x37",
  ).unwrap()
  let queries : Array[(Double, Double)] = [
    (0.25, 45),
    (1.5, 315),
    (1.0, 0),
    (1.0, 360),
    (2.0, 180),
  ]
  let expected : Array[Double] = [6.0, 19.5, 13.0, 13.0, 25.0]
  for i, (lat, lon) in queries {
    let s = f.sample({ id: "station", latitude: lat, longitude: lon, })
    assert_true((s.value.unwrap() - expected[i]).abs() < 1.0e-10)
    let mut weight = 0.0
    let mut sum = 0.0
    for c in s.contributors {
      weight += c.weight
      sum += c.weight * c.value
    }
    assert_true((weight - 1.0).abs() < 1.0e-12)
    assert_true((sum - s.value.unwrap()).abs() < 1.0e-12)
  }
  assert_eq(f.interpolate_latlon(1.0, -45.0), f.interpolate_latlon(1.0, 315.0))
  let a = f.interpolate_latlon(1.0, 359.999999).unwrap()
  let b = f.interpolate_latlon(1.0, -0.000001).unwrap()
  assert_true((a - b).abs() < 1.0e-12)
  let selected = @grib2.select_fields([f], 0, 0, 0)
  assert_eq(selected.length(), 1)
  let points = f
    .crop({ south: 0.0, north: 2.0, west: 270.0, east: 0.0, })
    .unwrap()
  assert_eq(points.length(), 6)
  assert_eq(
    f.crop({ south: 2.0, north: 0.0, west: 0.0, east: 0.0, }) is Err(_),
    true,
  )
}

///|
test "bitmap, exact nodes, regional bounds and JSON null" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x00\x98\x96\x80\x30\x00\x00\x00\x00\x00\xb7\x1b\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x3f\x80\x00\x00\x80\x03\x00\x00\x11\x00\x00\x00\x00\x07\x06\x00\xbc\x00\x00\x00\x10\x07\x00\x00\x4e\x1c\x00\x03\x00\x02\x00\x01\x40\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.interpolate_latlon(1.0, 10.0), Some(1.0))
  assert_eq(f.interpolate_latlon(1.0, 10.5), None)
  assert_eq(f.interpolate_latlon(1.0, 12.0), Some(9999.0))
  assert_eq(f.interpolate_latlon(1.5, 10.0), None)
  assert_eq(f.interpolate_latlon(0.0, 9.0), None)
  assert_eq(f.interpolate_latlon(0.0, 13.0), None)
  let samples = f.sample_stations([
    { id: "missing", latitude: 1.0, longitude: 11.0, },
    { id: "valid", latitude: 0.0, longitude: 11.0, },
  ])
  assert_eq(samples[0].value, None)
  assert_eq(samples[1].value, Some(5.0))
  assert_true(samples[0].to_json() is { "value": Null, .. })
  match samples[1].to_json() {
    { "value": Number(v, ..), .. } => assert_eq(v, 5.0)
    _ => fail("expected numeric JSON value")
  }
}

///|
test "polar scalar regularisation is continuous and raw data unchanged" {
  let f = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xcd\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x10\x17\xdf\x80\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x80\x0c\x00\x00\x11\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x1f\x07\x00\x00\x08\x00\x08\x00\x06\x00\x05\x00\x03\x00\x01\xc0\x01\x00\x00\xa0\x00\x58\x00\x30\x00\x1a\x00\x00\x37\x37\x37\x37",
  ).unwrap()
  assert_eq(f.get(0, 0), Some(0.0))
  for lon in [0.0, 90.0, 270.0, 360.0] {
    assert_eq(f.interpolate_latlon(90.0, lon), Some(3.0))
  }
  assert_true(
    (f.interpolate_latlon(89.9999999, 0.0).unwrap() - 3.0).abs() < 1.0e-6,
  )
  assert_eq(f.interpolate_latlon(-90.0, 180.0), Some(23.0))
}
