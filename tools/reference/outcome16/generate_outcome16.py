from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[3];R=Path(__file__).parent;T=P/'testdata/outcome16';T.mkdir(exist_ok=True)
raw=(P/'testdata/forecast09/forecast-states.grib2').read_bytes();n=int.from_bytes(raw[8:16],'big');m=int.from_bytes(raw[n+8:n+16],'big');base=raw[:n];two=raw[:n+m]
sec={};off=16
while off<len(base)-4:
    size=int.from_bytes(base[off:off+4],'big');sec[base[off+4]]=base[off:off+size];off+=size
def put32(b,i,v):b[i:i+4]=v.to_bytes(4,'big')
def sm(v):return (abs(v)|(0x80000000 if v<0 else 0)).to_bytes(4,'big')
def mb(b):return 'b"'+''.join('\\x'+format(x,'02x') for x in b)+'"'
def polar(name,wind=False,south=False,empty=False,first_gap=False):
    g=bytearray(sec[3]);north=-89 if south else 90;g[46:50]=sm(north*1_000_000);g[55:59]=sm((north-1)*1_000_000)
    p=bytearray(sec[4]);p[9]=2 if wind else 0
    valid=[True]*6
    if empty:valid[:3]=[False]*3
    if first_gap:valid[0]=False
    d=bytearray(sec[5]);put32(d,5,sum(valid))
    if all(valid):bitmap=(6).to_bytes(4,'big')+bytes([6,255])
    else:bitmap=(7).to_bytes(4,'big')+bytes([6,0,sum((1<<(7-i)) for i,v in enumerate(valid) if v)])
    body=sec[1]+g+p+d+bitmap+sec[7]+b'7777';head=bytearray(base[:16]);head[8:16]=(16+len(body)).to_bytes(8,'big');return bytes(head)+body
fixtures={'regional':base,'two_fields':two,'scalar_empty':polar('scalar_empty',empty=True),'wind':polar('wind',wind=True),'south_wind_gap':polar('south_wind_gap',wind=True,south=True,first_gap=True)}
unsupported=bytearray(base);off=16
while unsupported[off+4]!=5:off+=int.from_bytes(unsupported[off:off+4],'big')
unsupported[off+9:off+11]=(3).to_bytes(2,'big');fixtures['unsupported_declaration']=bytes(unsupported)
for name,b in fixtures.items():(T/(name+'.grib2')).write_bytes(b)
helpers='\n'.join('''///|
fn outcome16_NAME() -> Bytes {
  BYTES
}
'''.replace('NAME',name).replace('BYTES',mb(b)) for name,b in fixtures.items())
tests=r'''///|
fn outcome16_failure(f : @grib2.GriddedField, s : @grib2.Station, expected : @grib2.SampleFailure) -> Unit raise {
  match f.sample_result(s) {
    Err(reason) => assert_eq(reason, expected)
    Ok(_) => fail("expected per-station failure")
  }
  let legacy = f.sample(s)
  assert_eq(legacy.value, None)
  assert_eq(legacy.algorithm, "outside-or-missing")
  assert_eq(legacy.contributors.length(), 0)
  assert_eq(legacy.station.id, s.id)
  assert_eq(legacy.origin, f.origin())
  assert_eq(legacy.product, f.product())
}

///|
test "outcome16 regional causes and unchanged available sample" {
  let f = @grib2.read_message(outcome16_regional()).unwrap()
  let invalid : Array[@grib2.Station] = [
    { id: "latitude", latitude: 91.0, longitude: 10.0 },
    { id: "nan", latitude: 0.0 / 0.0, longitude: 10.0 },
    { id: "infinity", latitude: 0.0, longitude: 1.0 / 0.0 },
  ]
  for s in invalid {
    outcome16_failure(f, s, InvalidStation)
  }
  outcome16_failure(f, { id: "north", latitude: 2.0, longitude: 10.0 }, OutsideGrid)
  outcome16_failure(f, { id: "west", latitude: 0.0, longitude: 9.0 }, OutsideGrid)
  outcome16_failure(f, { id: "bitmap", latitude: 1.0, longitude: 10.0 }, MissingData)
  let s : @grib2.Station = { id: "available", latitude: 0.0, longitude: 10.5 }
  let sample = f.sample_result(s).unwrap()
  assert_eq(sample.value, Some(111.0))
  assert_eq(sample.contributors.length(), 2)
  assert_eq(sample.contributors[0].source_index, 3)
  assert_eq(sample.contributors[1].source_index, 4)
  assert_eq(sample.contributors[0].weight, 0.5)
  assert_eq(sample.to_json(), f.sample(s).to_json())
  assert_eq(f.sample_result({ id: "periodic", latitude: 0.0, longitude: 731.0 }).unwrap().value, Some(111.0))
}

///|
test "outcome16 polar policies zero weights and first blocking cause" {
  let empty = @grib2.read_message(outcome16_scalar_empty()).unwrap()
  outcome16_failure(empty, { id: "pole", latitude: 90.0, longitude: 11.0 }, MissingData)
  assert_eq(empty.sample_result({ id: "node", latitude: 89.0, longitude: 10.0 }).unwrap().value, Some(111.0))
  let wind = @grib2.read_message(outcome16_wind()).unwrap()
  outcome16_failure(wind, { id: "wind", latitude: 90.0, longitude: 11.0 }, UnsupportedPolarVector)
  outcome16_failure(wind, { id: "invalid-first", latitude: 91.0, longitude: 11.0 }, InvalidStation)
  assert_eq(wind.sample_result({ id: "node", latitude: 89.0, longitude: 11.0 }).unwrap().value, Some(111.0))
  let south = @grib2.read_message(outcome16_south_wind_gap()).unwrap()
  outcome16_failure(south, { id: "missing-first", latitude: -89.5, longitude: 10.0 }, MissingData)
  outcome16_failure(south, { id: "wind-only", latitude: -90.0, longitude: 10.0 }, UnsupportedPolarVector)
}

///|
test "outcome16 decoder and selector failures remain outer GribError" {
  assert_true(@grib2.read_fields(outcome16_unsupported_declaration()) is Err(UnsupportedTemplate(5, 3)))
  let fields = @grib2.read_fields(outcome16_two_fields()).unwrap()
  assert_true(@grib2.select_unique_field(fields, @grib2.FieldQuery::new(0, 0, 99)) is Err(InvalidRequest(_)))
  assert_true(@grib2.select_unique_field(fields, @grib2.FieldQuery::new(0, 0, 0)) is Err(InvalidRequest(_)))
}

///|
test "outcome16 public failure codes are stable JSON strings" {
  let failures : Array[@grib2.SampleFailure] = [
    InvalidStation, OutsideGrid, MissingData, UnsupportedPolarVector, NonFiniteResult,
  ]
  let expected = ["invalid-station", "outside-grid", "missing-data", "unsupported-polar-vector", "nonfinite-result"]
  let codes : Array[Json] = []
  for i, reason in failures {
    let code = ToJson::to_json(reason)
    assert_eq(code, expected[i].to_json())
    codes.push(code)
  }
  println("OUTCOME16|codes|" + codes.to_json().stringify())
}
'''
(P/'outcome16_test.mbt').write_text(helpers+tests,encoding='utf-8')
report=r'''///|
fn report(name : String, field : @grib2.GriddedField, station : @grib2.Station) -> Unit {
  let event : Json = match field.sample_result(station) {
    Ok(sample) => { "phase": "sample", "case": name.to_json(), "code": "available", "sample": sample.to_json() }
    Err(reason) => { "phase": "sample", "case": name.to_json(), "code": ToJson::to_json(reason), "station": station.to_json(), "origin": field.origin().to_json(), "product": ToJson::to_json(field.product()) }
  }
  println(event.stringify())
}

///|
fn main {
  let regional = @grib2.read_message(REGIONAL).unwrap()
  let wind = @grib2.read_message(WIND).unwrap()
  let empty = @grib2.read_message(EMPTY).unwrap()
  report("available", regional, { id: "inland", latitude: 0.0, longitude: 10.5 })
  report("bitmap", regional, { id: "coast", latitude: 1.0, longitude: 10.0 })
  report("outside", regional, { id: "outside", latitude: 2.0, longitude: 10.0 })
  report("invalid", regional, { id: "bad", latitude: 91.0, longitude: 10.0 })
  report("wind-pole", wind, { id: "pole", latitude: 90.0, longitude: 11.0 })
  report("empty-pole", empty, { id: "pole", latitude: 90.0, longitude: 11.0 })
  let decode_event : Json = match @grib2.read_fields(UNSUPPORTED) {
    Err(UnsupportedTemplate(section, template)) => { "phase": "decode", "code": "unsupported-template", "section": section.to_json(), "template": template.to_json() }
    _ => { "phase": "unexpected" }
  }
  println(decode_event.stringify())
  let fields = @grib2.read_fields(TWO).unwrap()
  for query in [@grib2.FieldQuery::new(0, 0, 99), @grib2.FieldQuery::new(0, 0, 0)] {
    let event : Json = match @grib2.select_unique_field(fields, query) {
      Err(InvalidRequest(message)) => { "phase": "selection", "code": "invalid-request", "message": message.to_json() }
      _ => { "phase": "unexpected" }
    }
    println(event.stringify())
  }
}
'''
for token,name in [('REGIONAL','regional'),('WIND','wind'),('EMPTY','scalar_empty'),('UNSUPPORTED','unsupported_declaration'),('TWO','two_fields')]:report=report.replace(token,mb(fixtures[name]))
E=P/'cmd/outcomes';E.mkdir(exist_ok=True);(E/'main.mbt').write_text(report,encoding='utf-8');(E/'moon.pkg').write_text((P/'cmd/direct/moon.pkg').read_text(encoding='utf-8'),encoding='utf-8')
consumer=r'''///|
fn route(name : String, field : @grib2.GriddedField, station : @grib2.Station) -> Unit {
  let event : Json = match field.sample_result(station) {
    Ok(sample) => { "case": name.to_json(), "action": "keep-value", "sample": sample.to_json() }
    Err(reason) => {
      let action = match reason {
        InvalidStation => "fix-station"
        OutsideGrid => "check-coverage"
        MissingData => "keep-missing"
        UnsupportedPolarVector => "choose-supported-operation"
        NonFiniteResult => "inspect-numeric-result"
      }
      { "case": name.to_json(), "action": action.to_json(), "code": ToJson::to_json(reason) }
    }
  }
  println(event.stringify())
}

///|
fn main {
  let regional = @grib2.read_message(REGIONAL).unwrap()
  let wind = @grib2.read_message(WIND).unwrap()
  route("available", regional, { id: "inland", latitude: 0.0, longitude: 10.5 })
  route("bitmap", regional, { id: "coast", latitude: 1.0, longitude: 10.0 })
  route("outside", regional, { id: "outside", latitude: 2.0, longitude: 10.0 })
  route("invalid", regional, { id: "bad", latitude: 91.0, longitude: 10.0 })
  route("wind-pole", wind, { id: "pole", latitude: 90.0, longitude: 11.0 })
}
'''.replace('REGIONAL',mb(fixtures['regional'])).replace('WIND',mb(fixtures['wind']))
(R/'external-main.mbt.txt').write_text(consumer,encoding='utf-8')
reference={'fixtures':{name:{'file':name+'.grib2','sha256':hashlib.sha256(b).hexdigest()} for name,b in fixtures.items()},'fixture_origin':'Synthetic existing forecast09 constant111 frame; polar metadata/masks/categories adapted. Unsupported declaration is only an unsupported-template header test, not a valid5.3 sample.','sample_cases':{'available':'available','bitmap':'missing-data','outside':'outside-grid','invalid':'invalid-station','wind-pole':'unsupported-polar-vector','empty-pole':'missing-data'},'available':{'value':111,'contributors':[3,4],'weights':[.5,.5]},'selection_messages':['no field matches query','query matches multiple fields'],'failure_codes':['invalid-station','outside-grid','missing-data','unsupported-polar-vector','nonfinite-result'],'nonfinite_result_runtime_reproduction':False}
(T/'REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n',encoding='utf-8');(R/'REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n',encoding='utf-8')
print('Generated4 outcome tests, CLI example and independent typed consumer.')
