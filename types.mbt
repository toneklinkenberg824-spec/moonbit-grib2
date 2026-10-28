///|
pub(all) enum GribError {
  UnsupportedTemplate(Int, Int)
  CorruptedBitstream(String)
  InvalidScanningMode(Int)
  InvalidGrid(String)
  InvalidRequest(String)
} derive(Debug, Eq)

///|
/// Numerical WMO identifiers and original time units are retained, without guessing names.
pub(all) struct Surface {
  kind : Int
  scale : Int?
  scaled_value : UInt?
} derive(Debug, Eq, ToJson)

///|
pub(all) struct Product {
  discipline : Int
  category : Int
  parameter : Int
  centre : Int
  subcentre : Int
  master_table : Int
  local_table : Int
  reference_time : Array[Int]
  time_unit : Int
  forecast_time : Int?
  first_surface : Surface
  second_surface : Surface
} derive(Debug, Eq, ToJson)

///|
pub(all) struct Origin {
  message : Int
  field : Int
  byte_offset : Int
  scanning_mode : Int
} derive(Debug, Eq, ToJson)

///|
/// Values and masks are private: callers cannot invalidate their coordinate association.
pub struct GriddedField {
  nrows : Int
  ncols : Int
  north : Double
  west : Double
  dx : Double
  dy : Double
  cyclic : Bool
  unique_cols : Int
  priv data : Array[Double]
  priv valid : Array[Bool]
  priv source_indices : Array[Int]
  priv product_info : Product
  source : Origin
  local_bytes : Bytes?
}

///|
pub(all) struct Contributor {
  row : Int
  col : Int
  source_index : Int
  latitude : Double
  longitude : Double
  weight : Double
  value : Double
} derive(Debug, ToJson)

///|
pub(all) struct Station {
  id : String
  latitude : Double
  longitude : Double
} derive(Debug, ToJson)

///|
pub(all) struct Sample {
  station : Station
  origin : Origin
  product : Product
  value : Double?
  algorithm : String
  contributors : Array[Contributor]
} derive(Debug)

///|
/// West/east may span the date line; west==east selects that meridian, not the whole world.
pub(all) struct BBox {
  south : Double
  north : Double
  west : Double
  east : Double
} derive(Debug, ToJson)

///|
pub(all) struct GridPoint {
  row : Int
  col : Int
  source_index : Int
  latitude : Double
  longitude : Double
  value : Double?
} derive(Debug)

///|
/// Explicit null keeps missing samples visible to JSON consumers.
pub impl ToJson for Sample with fn to_json(self) {
  {
    "station": ToJson::to_json(self.station),
    "origin": ToJson::to_json(self.origin),
    "product": ToJson::to_json(self.product),
    "value": match self.value {
      Some(v) => v.to_json()
      None => self.value.to_json()
    },
    "algorithm": self.algorithm.to_json(),
    "contributors": self.contributors.to_json(),
  }
}

///|
pub impl ToJson for GridPoint with fn to_json(self) {
  {
    "row": self.row.to_json(),
    "col": self.col.to_json(),
    "source_index": self.source_index.to_json(),
    "latitude": self.latitude.to_json(),
    "longitude": self.longitude.to_json(),
    "value": match self.value {
      Some(v) => v.to_json()
      None => self.value.to_json()
    },
  }
}

///|
pub fn GriddedField::rows(self : GriddedField) -> Int {
  self.nrows
}

///|
pub fn GriddedField::cols(self : GriddedField) -> Int {
  self.ncols
}

///|
pub fn GriddedField::is_global(self : GriddedField) -> Bool {
  self.cyclic
}

///|
pub fn GriddedField::product(self : GriddedField) -> Product {
  {
    ..self.product_info,
    reference_time: self.product_info.reference_time.copy(),
  }
}

///|
pub fn GriddedField::origin(self : GriddedField) -> Origin {
  self.source
}

///|
/// Entire optional Section 2 bytes, including header, inherited within its message.
pub fn GriddedField::local_use(self : GriddedField) -> Bytes? {
  self.local_bytes
}

///|
pub fn GriddedField::get(self : GriddedField, row : Int, col : Int) -> Double? {
  if row < 0 || row >= self.nrows || col < 0 || col >= self.ncols {
    return None
  }
  let index = row * self.ncols + col
  if self.valid[index] {
    Some(self.data[index])
  } else {
    None
  }
}

///|
/// Owned copy containing IEEE NaN in missing cells.
pub fn GriddedField::values(self : GriddedField) -> Array[Double] {
  self.data.copy()
}

///|
pub fn GriddedField::mask(self : GriddedField) -> Array[Bool] {
  self.valid.copy()
}

///|
pub fn GriddedField::point(
  self : GriddedField,
  row : Int,
  col : Int,
) -> GridPoint? {
  if row < 0 || row >= self.nrows || col < 0 || col >= self.ncols {
    return None
  }
  Some({
    row,
    col,
    source_index: self.source_indices[row * self.ncols + col],
    latitude: self.north - row.to_double() * self.dy,
    longitude: wrap(self.west + col.to_double() * self.dx),
    value: self.get(row, col),
  })
}

///|
fn finite(x : Double) -> Bool {
  !x.is_nan() && !x.is_inf()
}

///|
fn wrap(x : Double) -> Double {
  let r = x.mod(360.0)
  let positive = if r < 0.0 { r + 360.0 } else { r }
  if positive == 360.0 {
    0.0
  } else {
    positive
  }
}

///|
/// Only arithmetic roundoff near an encoded pole is tolerated, not a microdegree neighbourhood.
fn is_pole(latitude : Double) -> Bool {
  (latitude.abs() - 90.0).abs() <= 1.0e-12
}

///|
fn near(x : Double, y : Double) -> Bool {
  (x - y).abs() <= 0.000002
}
