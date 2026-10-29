///|
/// Internal contributor to an interpolation stencil (duplicate cells are combined).
fn add_contributor(
  f : GriddedField,
  out : Array[Contributor],
  r : Int,
  c : Int,
  w : Double,
) -> Unit {
  if w <= 0.0 {
    return
  }
  let value = f.get(r, c).unwrap()
  for i, x in out {
    if x.row == r && x.col == c {
      out[i] = { ..x, weight: x.weight + w, }
      return
    }
  }
  out.push({
    row: r,
    col: c,
    source_index: f.source_indices[r * f.ncols + c],
    latitude: f.north - r.to_double() * f.dy,
    longitude: wrap(f.west + c.to_double() * f.dx),
    weight: w,
    value,
  })
}

///|
/// Pole regularisation is scalar only. Geographic vector components have longitude-dependent bases.
fn scalar_pole(f : GriddedField) -> Bool {
  !(f.product_info.discipline == 0 && f.product_info.category == 2)
}

///|
fn row_stencil(
  f : GriddedField,
  r : Int,
  c0 : Int,
  c1 : Int,
  t : Double,
  w : Double,
  out : Array[Contributor],
) -> SampleFailure? {
  if w <= 0.0 {
    return None
  }
  let latitude = f.north - r.to_double() * f.dy
  if is_pole(latitude) {
    if !scalar_pole(f) {
      return Some(UnsupportedPolarVector)
    }
    let mut n = 0
    for c in 0..<f.unique_cols {
      if f.get(r, c) is Some(_) {
        n += 1
      }
    }
    if n == 0 {
      return Some(MissingData)
    }
    for c in 0..<f.unique_cols {
      if f.get(r, c) is Some(_) {
        add_contributor(f, out, r, c, w / n.to_double())
      }
    }
    return None
  }
  if (1.0 - t > 0.0 && f.get(r, c0) is None) ||
    (t > 0.0 && f.get(r, c1) is None) {
    return Some(MissingData)
  }
  add_contributor(f, out, r, c0, w * (1.0 - t))
  add_contributor(f, out, r, c1, w * t)
  None
}

///|
/// Same scalar interpolation and provenance as sample(), with the first failure cause.
/// Decode/selection errors remain GribError; this only diagnoses a decoded field.
pub fn GriddedField::sample_result(
  self : GriddedField,
  station : Station,
) -> Result[Sample, SampleFailure] {
  let lat = station.latitude
  let lon = station.longitude
  if !finite(lat) || !finite(lon) || lat < -90.0 || lat > 90.0 {
    return Err(InvalidStation)
  }
  let y = if self.nrows == 1 && self.dy == 0.0 {
    if lat != self.north {
      return Err(OutsideGrid)
    }
    0.0
  } else {
    (self.north - lat) / self.dy
  }
  let longitude = wrap(lon)
  let x = if self.ncols == 1 && self.dx == 0.0 {
    if longitude != self.west {
      return Err(OutsideGrid)
    }
    0.0
  } else {
    wrap(longitude - self.west) / self.dx
  }
  // Inverting origin-step arithmetic need not recover an exact integer.
  // Restore exact public nodes before rejecting a rounded edge coordinate.
  // Keep candidates as Double: fine angular units can put outside queries beyond Int.
  let nearest_row = y.round()
  let y = if nearest_row >= 0.0 &&
    nearest_row <= (self.nrows - 1).to_double() &&
    lat == self.north - nearest_row * self.dy {
    nearest_row
  } else {
    y
  }
  let nearest_col = x.round()
  let x = if nearest_col >= 0.0 &&
    nearest_col <= (self.ncols - 1).to_double() &&
    longitude == wrap(self.west + nearest_col * self.dx) {
    nearest_col
  } else {
    x
  }
  if y < -1.0e-10 || y > (self.nrows - 1).to_double() + 1.0e-10 {
    return Err(OutsideGrid)
  }
  if !self.cyclic && x > (self.ncols - 1).to_double() + 1.0e-10 {
    return Err(OutsideGrid)
  }
  let y = @cmp.maximum(0.0, @cmp.minimum(y, (self.nrows - 1).to_double()))
  let x = if self.cyclic {
    x
  } else {
    @cmp.minimum(x, (self.ncols - 1).to_double())
  }
  let r0 = y.floor().to_int()
  let r1 = if r0 + 1 < self.nrows { r0 + 1 } else { r0 }
  let c0 = x.floor().to_int() % self.unique_cols
  let c1 = if self.cyclic {
    (c0 + 1) % self.unique_cols
  } else if c0 + 1 < self.ncols {
    c0 + 1
  } else {
    c0
  }
  let ty = y - y.floor()
  let tx = x - x.floor()
  let out : Array[Contributor] = []
  if row_stencil(self, r0, c0, c1, tx, 1.0 - ty, out) is Some(failure) {
    return Err(failure)
  }
  if row_stencil(self, r1, c0, c1, tx, ty, out) is Some(failure) {
    return Err(failure)
  }
  // Subnormal fields need headroom before multiplying by fractional weights.
  // A power-of-two shift is exact; round back only after accumulating the stencil.
  let min_normal = @math.scalbn(1.0, -1022)
  let mut subnormal = true
  for c in out {
    if c.value.abs() >= min_normal {
      subnormal = false
      break
    }
  }
  let mut value = 0.0
  for c in out {
    let v = if subnormal { @math.scalbn(c.value, 1022) } else { c.value }
    value += c.weight * v
  }
  if subnormal {
    value = @math.scalbn(value, -1022)
  }
  if !finite(value) {
    // A finite convex mean can overflow when rounded weights accumulate near
    // Double.MAX. Retry in unit magnitude and normalise the represented weights.
    let mut magnitude = 0.0
    for c in out {
      magnitude = @cmp.maximum(magnitude, c.value.abs())
    }
    let mut scaled_sum = 0.0
    let mut weight_sum = 0.0
    for c in out {
      scaled_sum += c.weight * (c.value / magnitude)
      weight_sum += c.weight
    }
    let unit_mean = @cmp.maximum(
      -1.0,
      @cmp.minimum(1.0, scaled_sum / weight_sum),
    )
    value = unit_mean * magnitude
  }
  if !finite(value) {
    return Err(NonFiniteResult)
  }
  let polar = is_pole(self.north - r0.to_double() * self.dy) ||
    (ty > 0.0 && is_pole(self.north - r1.to_double() * self.dy))
  Ok({
    station,
    origin: self.source,
    product: self.product(),
    value: Some(value),
    algorithm: if polar {
      "bilinear-polar-scalar-mean"
    } else {
      "bilinear-latlon"
    },
    contributors: out,
  })
}

///|
pub fn GriddedField::interpolate_latlon(
  self : GriddedField,
  lat : Double,
  lon : Double,
) -> Double? {
  self.sample({ id: "", latitude: lat, longitude: lon, }).value
}

///|
/// Batch station results retain field metadata, message identity and weighted source-grid provenance.
pub fn GriddedField::sample_stations(
  self : GriddedField,
  stations : ArrayView[Station],
) -> Array[Sample] {
  stations.iter().map(s => self.sample(s)).collect()
}

///|
/// Node extraction without resampling; each result retains its original scan index.
pub fn GriddedField::crop(
  self : GriddedField,
  bbox : BBox,
) -> Result[Array[GridPoint], GribError] {
  match self.crop_iter(bbox) {
    Ok(points) => Ok(points.collect())
    Err(error) => Err(error)
  }
}

///|
/// Exact identifier/time-unit query, with no hidden conversion between forecast units.
pub fn select_fields(
  fields : ArrayView[GriddedField],
  discipline : Int,
  category : Int,
  parameter : Int,
  time_unit? : Int,
  forecast_time? : Int,
) -> Array[GriddedField] {
  fields
  .iter()
  .filter(f => {
    let p = f.product_info
    p.discipline == discipline &&
    p.category == category &&
    p.parameter == parameter &&
    (time_unit is None || time_unit == Some(p.time_unit)) &&
    (forecast_time is None || forecast_time == p.forecast_time)
  })
  .collect()
}
