///|
/// One decoded input field evaluated against the complete encoded query.
/// index is relative to the supplied view; Origin retains the original identity.
pub(all) struct FieldQueryEntry {
  index : Int
  matches : Bool
  origin : Origin
  product : Product
} derive(ToJson, Debug)

///|
/// Complete, input-ordered metadata snapshot. No rows are omitted or truncated.
pub(all) struct FieldQueryReport {
  field_count : Int
  match_count : Int
  entries : Array[FieldQueryEntry]
} derive(ToJson, Debug)

///|
/// Inspect every field without choosing one or changing unique/batch selection.
/// Product metadata is copied; no values, physical units or calendars are converted.
pub fn inspect_field_query(
  fields : ArrayView[GriddedField],
  query : FieldQuery,
) -> Result[FieldQueryReport, GribError] {
  if query.reference_time is Some(t) && t.length() != 6 {
    return Err(InvalidRequest("reference_time must contain six components"))
  }
  let entries : Array[FieldQueryEntry] = []
  let mut match_count = 0
  for index, field in fields {
    let matches = query.matches(field.product_info)
    if matches {
      match_count += 1
    }
    entries.push({
      index,
      matches,
      origin: field.origin(),
      product: field.product(),
    })
  }
  Ok({ field_count: fields.length(), match_count, entries, })
}
