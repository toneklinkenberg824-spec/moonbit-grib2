///|
/// Decode all fields from concatenated GRIB2 messages. Any invalid/unsupported field fails explicitly.
pub fn read_fields(
  bytes : Bytes,
  max_points? : Int = 10000000,
) -> Result[Array[GriddedField], GribError] {
  if max_points <= 0 {
    return Err(InvalidRequest("max_points must be positive"))
  }
  let parsed = match @upcore.parse_grib2_file(bytes) {
    Ok(p) => p
    Err(e) => return Err(CorruptedBitstream(e.to_string()))
  }
  if parsed.messages.is_empty() {
    return Err(CorruptedBitstream("empty input"))
  }
  let fields : Array[GriddedField] = []
  for mi, m in parsed.messages {
    if m.edition != 2 || m.section1.length < 21 {
      return Err(CorruptedBitstream("invalid identification"))
    }
    if m.submessages.is_empty() {
      return Err(CorruptedBitstream("message contains no fields"))
    }
    let mut previous_bitmap : Bytes? = None
    let mut previous_points = 0
    let mut local_use : Bytes? = None
    for fi, s in m.submessages {
      if s.section2 is Some(local_section) {
        local_use = Some(section_bytes(m, local_section))
      }
      let g = section_bytes(m, s.section3)
      let p = section_bytes(m, s.section4)
      let d = section_bytes(m, s.section5)
      let b = section_bytes(m, s.section6)
      let payload = section_bytes(m, s.section7)
      if g.length() < 14 || p.length() < 9 || d.length() < 11 || b.length() < 6 {
        return Err(CorruptedBitstream("short header"))
      }
      for (section, id) in [(3, u16(g, 12)), (4, u16(p, 7)), (5, u16(d, 9))] {
        if id != 0 {
          return Err(UnsupportedTemplate(section, id))
        }
      }
      if g.length() != 72 || byte_at(g, 10) != 0 || byte_at(g, 11) != 0 {
        return Err(InvalidGrid("quasi-regular or extended grid"))
      }
      if p.length() != 34 || u16(p, 5) != 0 || d.length() != 21 {
        return Err(CorruptedBitstream("invalid template length"))
      }
      if !finite(
          @unpack.ieee754_single_to_double(u32(d, 11).reinterpret_as_int()),
        ) {
        return Err(CorruptedBitstream("nonfinite encoded reference value"))
      }
      let scan = byte_at(g, 71)
      if (scan & 15) != 0 {
        return Err(InvalidScanningMode(scan))
      }
      for pos in [46, 50, 55, 59] {
        if u32(g, pos) == 0xffffffffU {
          return Err(InvalidGrid("missing grid coordinate"))
        }
      }
      let ni = u32(g, 30).to_uint64()
      let nj = u32(g, 34).to_uint64()
      let n64 = ni * nj
      if ni == 0 ||
        nj == 0 ||
        n64 > max_points.to_uint64() ||
        n64 != u32(g, 6).to_uint64() {
        return Err(InvalidGrid("invalid grid size or max_points exceeded"))
      }
      let nc = ni.to_int()
      let nr = nj.to_int()
      let n = n64.to_int()
      let basic = u32(g, 38)
      let subdiv = u32(g, 42)
      let unit = if basic == 0U {
        0.000001
      } else {
        if basic == 0xffffffffU || subdiv == 0U || subdiv == 0xffffffffU {
          return Err(InvalidGrid("invalid basic angle"))
        }
        basic.to_double() / subdiv.to_double()
      }
      let angle_num = if basic == 0U { 1UL } else { basic.to_uint64() }
      let angle_den = if basic == 0U { 1000000UL } else { subdiv.to_uint64() }
      let first_lon_ticks = u32(g, 50).to_uint64()
      let last_lon_ticks = u32(g, 59).to_uint64()
      let lon_difference = if first_lon_ticks >= last_lon_ticks {
        first_lon_ticks - last_lon_ticks
      } else {
        last_lon_ticks - first_lon_ticks
      }
      // A singleton axis has no interval. Its endpoints must encode the same
      // position, including the exact0/360 longitude alias. Products of two
      // UInt32 quantities fit UInt64; no floating tolerance admits a new span.
      let singleton_i = ni == 1UL &&
        (
          first_lon_ticks == last_lon_ticks ||
          lon_difference * angle_num == 360UL * angle_den
        )
      let singleton_j = nj == 1UL && sm32(g, 46) == sm32(g, 55)
      let missing_di = u32(g, 63) == 0xffffffffU
      let missing_dj = u32(g, 67) == 0xffffffffU
      if (missing_di && !singleton_i) || (missing_dj && !singleton_j) {
        return Err(InvalidGrid("missing grid increments"))
      }
      // Validate in encoded angular ticks before wrapping or rounding to Double.
      // The positive Int point budget bounds each span below Int64::MAX_VALUE.
      let lat_limit = (90UL * angle_den / angle_num).reinterpret_as_int64()
      let lon_limit = 360UL * angle_den / angle_num
      let first_lat = sm32(g, 46).to_int64()
      let last_lat = sm32(g, 55).to_int64()
      let lat_span = ((nj - 1UL) * u32(g, 67).to_uint64()).reinterpret_as_int64()
      let lon_span = (ni - 1UL) * u32(g, 63).to_uint64()
      let ip = (scan & 128) != 0
      let jp = (scan & 64) != 0
      let north_ticks = if jp { first_lat + lat_span } else { first_lat }
      let south_ticks = north_ticks - lat_span
      if first_lat < -lat_limit ||
        first_lat > lat_limit ||
        last_lat < -lat_limit ||
        last_lat > lat_limit ||
        north_ticks > lat_limit ||
        south_ticks < -lat_limit ||
        u32(g, 50).to_uint64() > lon_limit ||
        u32(g, 59).to_uint64() > lon_limit ||
        lon_span > lon_limit {
        return Err(
          InvalidGrid("encoded coordinates or extent outside physical domain"),
        )
      }
      let dx = if missing_di { 0.0 } else { u32(g, 63).to_double() * unit }
      let dy = if missing_dj { 0.0 } else { u32(g, 67).to_double() * unit }
      // At a legal pole the bounded integer numerator is exact in binary64;
      // divide last so unit roundoff cannot move exactly90 outside its domain.
      let north = north_ticks.to_double() *
        angle_num.to_double() /
        angle_den.to_double()
      let first_lon = u32(g, 50).to_uint64().reinterpret_as_int64()
      let west_ticks = if ip {
        first_lon - lon_span.reinterpret_as_int64()
      } else {
        first_lon
      }
      let west = wrap(
        west_ticks.to_double() * angle_num.to_double() / angle_den.to_double(),
      )
      if !finite(dx) ||
        !finite(dy) ||
        (dx <= 0.0 && !singleton_i) ||
        (dy <= 0.0 && !singleton_j) ||
        north > 90.000002 ||
        north - (nr - 1).to_double() * dy < -90.000002 ||
        (nc - 1).to_double() * dx > 360.000002 {
        return Err(InvalidGrid("invalid coordinate extent or increments"))
      }
      // Validate first/last coordinates against the actual scan, including alternating rows/columns.
      let coords : Array[(Int, Int)] = []
      if (scan & 32) != 0 {
        for i in 0..<nc {
          for j in 0..<nr {
            let jj = if (scan & 16) != 0 && i % 2 == 1 { nr - 1 - j } else { j }
            coords.push(
              (
                if jp {
                  nr - 1 - jj
                } else {
                  jj
                },
                if ip {
                  nc - 1 - i
                } else {
                  i
                },
              ),
            )
          }
        }
      } else {
        for j in 0..<nr {
          for i in 0..<nc {
            let ii = if (scan & 16) != 0 && j % 2 == 1 { nc - 1 - i } else { i }
            coords.push(
              (
                if jp {
                  nr - 1 - j
                } else {
                  j
                },
                if ip {
                  nc - 1 - ii
                } else {
                  ii
                },
              ),
            )
          }
        }
      }
      let lr = if jp { 0 } else { nr - 1 }
      let lc = if ip { 0 } else { nc - 1 }
      let last_lon = u32(g, 59).to_double() * unit
      if !near(north - lr.to_double() * dy, sm32(g, 55) * unit) ||
        (
          !near(wrap(west + lc.to_double() * dx - last_lon), 0.0) &&
          !near(wrap(last_lon - west - lc.to_double() * dx), 0.0)
        ) {
        return Err(InvalidGrid("last coordinate contradicts grid extent"))
      }
      let bitmap = match byte_at(b, 5) {
        0 => {
          if b.length() != 6 + (n + 7) / 8 {
            return Err(CorruptedBitstream("bitmap size mismatch"))
          }
          let map = b[6:].to_owned()
          previous_bitmap = Some(map)
          previous_points = n
          Some(map)
        }
        254 => {
          if b.length() != 6 {
            return Err(CorruptedBitstream("bitmap254 length"))
          }
          match previous_bitmap {
            Some(map) => {
              if previous_points != n || map.length() != (n + 7) / 8 {
                return Err(CorruptedBitstream("incompatible reused bitmap"))
              }
              Some(map)
            }
            None =>
              return Err(
                CorruptedBitstream("bitmap254 without previous bitmap"),
              )
          }
        }
        255 => {
          if b.length() != 6 {
            return Err(CorruptedBitstream("bitmap255 length"))
          }
          None
        }
        x => return Err(UnsupportedTemplate(6, x))
      }
      let mask : Array[Bool] = Array::make(n, true)
      let mut count = 0
      for i in 0..<n {
        let ok = match bitmap {
          None => true
          Some(map) => (byte_at(map, i / 8) & (1 << (7 - i % 8))) != 0
        }
        mask[i] = ok
        if ok {
          count += 1
        }
      }
      if u32(d, 5).to_uint64() != count.to_uint64() {
        return Err(CorruptedBitstream("packed value count differs from bitmap"))
      }
      let bits = byte_at(d, 19)
      if u16(d, 15) == 65535 || u16(d, 17) == 65535 {
        return Err(CorruptedBitstream("missing packing scale"))
      }
      if bits > 32 {
        return Err(CorruptedBitstream("bit width exceeds32"))
      }
      let required = (count.to_uint64() * bits.to_uint64() + 7UL) / 8UL
      if payload.length() < 5 || required != (payload.length() - 5).to_uint64() {
        return Err(CorruptedBitstream("packed payload length mismatch"))
      }
      let packed = match
        @unpack.unpack_simple(
          payload[5:].to_owned(),
          u32(d, 11).reinterpret_as_int(),
          u16(d, 15),
          u16(d, 17),
          bits,
          count,
        ) {
        Ok(v) => v.values
        Err(_) => return Err(CorruptedBitstream("simple unpack failed"))
      }
      let data = Array::make(n, 0.0 / 0.0)
      let valid = Array::make(n, false)
      let indices = Array::make(n, 0)
      let mut k = 0
      for i in 0..<n {
        let (r, c) = coords[i]
        let dst = r * nc + c
        indices[dst] = i
        if mask[i] {
          let v = packed[k]
          if !finite(v) {
            return Err(CorruptedBitstream("nonfinite decoded value"))
          }
          data[dst] = v
          valid[dst] = true
          k += 1
        }
      }
      let unique = if nc > 1 && near((nc - 1).to_double() * dx, 360.0) {
        nc - 1
      } else {
        nc
      }
      let cyclic = near(unique.to_double() * dx, 360.0)
      if unique != nc {
        for row in 0..<nr {
          let a = row * nc
          let z = a + nc - 1
          if valid[a] != valid[z] || (valid[a] && data[a] != data[z]) {
            return Err(InvalidGrid("duplicate seam endpoints disagree"))
          }
        }
      }
      fields.push({
        nrows: nr,
        ncols: nc,
        north,
        west,
        dx,
        dy,
        cyclic,
        unique_cols: unique,
        data,
        valid,
        source_indices: indices,
        local_bytes: local_use,
        product_info: product(m, p),
        source: {
          message: mi,
          field: fi,
          byte_offset: m.offset,
          scanning_mode: scan,
        },
      })
    }
  }
  if fields.is_empty() {
    Err(CorruptedBitstream("no fields"))
  } else {
    Ok(fields)
  }
}

///|
/// Require exactly one field, preventing silent loss of additional messages or fields.
pub fn read_message(
  bytes : Bytes,
  max_points? : Int = 10000000,
) -> Result[GriddedField, GribError] {
  match read_fields(bytes, max_points~) {
    Err(e) => Err(e)
    Ok(fields) =>
      if fields.length() == 1 {
        Ok(fields[0])
      } else {
        Err(InvalidRequest("expected one field; use read_fields"))
      }
  }
}
