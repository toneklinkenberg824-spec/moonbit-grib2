///|
// Synthetic raw-node extraction consumer; no operational weather data or file FFI.
fn emit_json(value : Json) -> Unit {
  println(value.stringify())
}

///|
fn emit(name : String, field : @grib2.GriddedField, bbox : @grib2.BBox) -> Unit {
  let cursor = field.crop_iter(bbox).unwrap()
  let points = cursor.collect()
  emit_json({
    "case": name.to_json(),
    "origin": field.origin().to_json(),
    "points": points.to_json(),
    "legacy": field.crop(bbox).unwrap().to_json(),
    "afterEnd": [cursor.next().to_json(), cursor.next().to_json()].to_json(),
  })
}

///|
fn emit_invalid(
  name : String,
  field : @grib2.GriddedField,
  bbox : @grib2.BBox,
) -> Unit raise {
  let error = match field.crop_iter(bbox) {
    Err(@grib2.InvalidRequest(message)) => message
    _ => fail("crop_iter must reject the box before returning an iterator")
  }
  let legacy_error = match field.crop(bbox) {
    Err(@grib2.InvalidRequest(message)) => message
    _ => fail("crop must retain its invalid bbox error")
  }
  emit_json({
    "case": name.to_json(),
    "error": error.to_json(),
    "legacyError": legacy_error.to_json(),
  })
}

///|
fn lifecycle(fields : Array[@grib2.GriddedField]) -> Unit {
  let regional = fields[0]
  let regional_box : @grib2.BBox = {
    south: 0.0,
    north: 1.0,
    west: 359.0,
    east: 1.0,
  }
  let mut seen = 0
  let cursor = regional
    .crop_iter(regional_box)
    .unwrap()
    .map(fn(point) {
      seen += 1
      point
    })
  let after_construction = seen
  let first = cursor.next().unwrap()
  let after_first = seen
  let second = cursor.next().unwrap()
  let after_second = seen
  let remaining = cursor.collect()
  let after_resume = seen
  emit_json({
    "case": "regional-pull-resume".to_json(),
    "origin": regional.origin().to_json(),
    "afterConstruction": after_construction.to_json(),
    "afterFirst": after_first.to_json(),
    "afterSecond": after_second.to_json(),
    "afterResume": after_resume.to_json(),
    "prefix": [first, second].to_json(),
    "remaining": remaining.to_json(),
    "afterEnd": cursor.next().to_json(),
  })
  let global_box : @grib2.BBox = {
    south: -90.0,
    north: 90.0,
    west: 0.0,
    east: 360.0,
  }
  let a = fields[1].crop_iter(global_box).unwrap()
  let b = fields[1].crop_iter(global_box).unwrap()
  let a0 = a.next().unwrap()
  let b0 = b.next().unwrap()
  let a1 = a.next().unwrap()
  emit_json({
    "case": "global-independent-iterators".to_json(),
    "first": [a0, a1].to_json(),
    "second": [b0].to_json(),
  })
  let empty = regional
    .crop_iter({ south: 2.0, north: 3.0, west: 0.0, east: 360.0, })
    .unwrap()
  emit_json({
    "case": "empty-exhaustion".to_json(),
    "afterEnd": [
      empty.next().to_json(),
      empty.next().to_json(),
      empty.next().to_json(),
    ].to_json(),
  })
}

///|
fn large_prefix() -> Unit {
  let field = @grib2.read_message(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb3\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x10\x00\x00\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x00\x00\xff\xff\xff\xff\x03\x0c\x7c\xb0\x00\x00\x00\x00\x30\x00\x00\x00\x00\x03\x0c\x7c\xb0\x00\x00\xc3\x50\x00\x00\xc3\x50\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\xff\xff\xff\xff\x67\x00\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x10\x00\x00\x00\x00\x40\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x05\x07\x37\x37\x37\x37",
  ).unwrap()
  let mut seen = 0
  let cursor = field
    .crop_iter({ south: 0.0, north: 51.15, west: 0.0, east: 51.15, })
    .unwrap()
    .map(fn(point) {
      seen += 1
      point
    })
  let first = cursor.next().unwrap()
  let second = cursor.next().unwrap()
  emit_json({
    "case": "large-prefix".to_json(),
    "origin": field.origin().to_json(),
    "shape": [field.rows(), field.cols()].to_json(),
    "seen": seen.to_json(),
    "points": [first, second].to_json(),
  })
}

///|
fn main raise {
  let fields = @grib2.read_fields(
    b"\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x06\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x00\xff\xff\xff\xff\x00\x0f\x42\x40\x15\x65\xe7\xc0\x30\x00\x00\x00\x00\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x0f\x42\x40\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x05\x00\x00\x3f\x80\x00\x00\x80\x03\x00\x00\x11\x00\x00\x00\x00\x07\x06\x00\xbc\x00\x00\x00\x10\x07\x00\x00\x4e\x1c\x00\x03\x00\x02\x00\x01\x40\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc2\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x05\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x05\x5d\x4a\x80\x00\x00\x00\x00\x30\x85\x5d\x4a\x80\x15\x75\x2a\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\x00\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\xff\xff\xff\xff\x67\x00\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x06\x06\xff\x00\x00\x00\x14\x07\x0a\x14\x1e\x28\x0a\x32\x00\x46\x50\x32\x5a\x64\x6e\x78\x5a\x37\x37\x37\x37\x47\x52\x49\x42\xff\xff\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc6\x00\x00\x00\x15\x01\x00\x62\x00\x00\x04\x00\x01\x07\xd7\x03\x17\x0c\x00\x00\x00\x02\x00\x00\x00\x48\x03\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x00\xff\xff\xff\xff\x85\x5d\x4a\x80\x10\x17\xdf\x80\x30\x05\x5d\x4a\x80\x00\x00\x00\x00\x05\x5d\x4a\x80\x05\x5d\x4a\x80\xf0\x00\x00\x00\x22\x04\x00\x00\x00\x00\x00\x00\x00\xff\x80\x00\x00\x00\x01\x00\x00\x00\x06\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x15\x05\x00\x00\x00\x0a\x00\x00\xc0\xa0\x00\x00\x80\x0c\x00\x00\x0d\x00\x00\x00\x00\x08\x06\x00\xde\xf0\x00\x00\x00\x16\x07\x00\x00\x80\x0c\x00\x80\x05\x00\x30\x02\x00\x12\x00\xa0\x05\x80\x00\x37\x37\x37\x37",
  ).unwrap()
  emit("regional-cross", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 359.0,
    east: 1.0,
  })
  emit("regional-west-edge", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 359.0,
    east: 0.0,
  })
  emit("regional-zero-meridian", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 0.0,
    east: 0.0,
  })
  emit("regional-long-way", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 1.0,
    east: 359.0,
  })
  emit("regional-between-columns", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 0.25,
    east: 0.75,
  })
  emit("regional-between-rows", fields[0], {
    south: 0.25,
    north: 0.75,
    west: 0.0,
    east: 360.0,
  })
  emit("regional-outside", fields[0], {
    south: 2.0,
    north: 3.0,
    west: 0.0,
    east: 360.0,
  })
  emit("global-full", fields[1], {
    south: -90.0,
    north: 90.0,
    west: 0.0,
    east: 360.0,
  })
  emit("global-cross", fields[1], {
    south: -90.0,
    north: 90.0,
    west: 270.0,
    east: 90.0,
  })
  emit("global-zero-meridian", fields[1], {
    south: -90.0,
    north: 90.0,
    west: 0.0,
    east: 0.0,
  })
  emit("global-valid-zero", fields[1], {
    south: 0.0,
    north: 0.0,
    west: 90.0,
    east: 90.0,
  })
  emit("global-raw-pole", fields[1], {
    south: 90.0,
    north: 90.0,
    west: 0.0,
    east: 360.0,
  })
  emit("global-negative-longitude", fields[1], {
    south: -90.0,
    north: 90.0,
    west: -90.0,
    east: 90.0,
  })
  emit("global-large-longitude", fields[1], {
    south: -90.0,
    north: 90.0,
    west: 1.0e+20,
    east: 1.0e+20,
  })
  emit("scan240-full", fields[2], {
    south: -90.0,
    north: 90.0,
    west: 0.0,
    east: 360.0,
  })
  emit("scan240-equator", fields[2], {
    south: 0.0,
    north: 0.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("reversed-latitude", fields[0], {
    south: 1.0,
    north: 0.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("south-below-limit", fields[0], {
    south: -91.0,
    north: 0.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("north-above-limit", fields[0], {
    south: 0.0,
    north: 91.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("nan-south", fields[0], {
    south: 0.0 / 0.0,
    north: 1.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("infinite-north", fields[0], {
    south: 0.0,
    north: 1.0 / 0.0,
    west: 0.0,
    east: 360.0,
  })
  emit_invalid("nan-west", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 0.0 / 0.0,
    east: 0.0,
  })
  emit_invalid("infinite-east", fields[0], {
    south: 0.0,
    north: 1.0,
    west: 0.0,
    east: -1.0 / 0.0,
  })
  lifecycle(fields)
  large_prefix()
}
