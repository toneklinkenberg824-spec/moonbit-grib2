///|
/// Validate the box now, then extract one raw node per next() in row-major order.
/// Coordinates, missing values and original scan indices are identical to crop().
/// Only independent columns are emitted on a closed global grid. Each call owns
/// its cursor; decoded field storage remains resident until the iterator is dropped.
pub fn GriddedField::crop_iter(
  self : GriddedField,
  bbox : BBox,
) -> Result[Iter[GridPoint], GribError] {
  if !finite(bbox.south) ||
    !finite(bbox.north) ||
    !finite(bbox.west) ||
    !finite(bbox.east) ||
    bbox.south > bbox.north ||
    bbox.south < -90.0 ||
    bbox.north > 90.0 {
    return Err(InvalidRequest("invalid bbox"))
  }
  let full = (bbox.east - bbox.west).abs() >= 360.0
  let west = wrap(bbox.west)
  let span = wrap(wrap(bbox.east) - west)
  let mut row = 0
  let mut col = 0
  Ok(
    Iter::new(fn() {
      while row < self.nrows {
        let latitude = self.north - row.to_double() * self.dy
        if latitude >= bbox.south && latitude <= bbox.north {
          while col < self.unique_cols {
            let current_col = col
            col += 1
            let longitude = wrap(self.west + current_col.to_double() * self.dx)
            if full || wrap(longitude - west) <= span {
              return self.point(row, current_col)
            }
          }
        }
        row += 1
        col = 0
      }
      None
    }),
  )
}
