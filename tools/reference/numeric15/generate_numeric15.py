from pathlib import Path
from fractions import Fraction
import struct,math,json,hashlib
P=Path(__file__).resolve().parents[3]
R=Path(__file__).parent;T=P/'testdata/numeric15';T.mkdir(exist_ok=True)
original=(P/'testdata/forecast09/forecast-states.grib2').read_bytes();original=original[:int.from_bytes(original[8:16],'big')]
sections={};off=16
while off<len(original)-4:
    n=int.from_bytes(original[off:off+4],'big');sections[original[off+4]]=original[off:off+n];off+=n
MAX=float.fromhex('0x1.fffffffffffffp+1023');divisor=1.
for _ in range(300):divisor/=10
def f32(x):return struct.unpack('>f',struct.pack('>f',x))[0]
def encoding(target):
    ratio=target*divisor;r=f32(ratio)
    if r>ratio:
        bits=int.from_bytes(struct.pack('>f',r),'big')+(1 if r<0 else -1)
        r=struct.unpack('>f',bits.to_bytes(4,'big'))[0]
    guess=round((ratio-r)*2**28)
    choices=[x for x in range(guess-80,guess+81) if 0<=x<2**32 and (r+x*2.0**-28)/divisor==target]
    assert choices,(target,r,guess)
    return r,choices[len(choices)//2]
def u32(b,i,v):b[i:i+4]=v.to_bytes(4,'big')
def sm(v):return (abs(v)|(0x80000000 if v<0 else 0)).to_bytes(4,'big')
def mb(b):return 'b"'+''.join('\\x'+format(x,'02x') for x in b)+'"'
rows={};fixtures={}
def make(name,ni,negative=False,mixed=False,gap=False,wind=False):
    target=-MAX if negative else MAX;r,x=encoding(target);values=[target]*(2*ni);packed=[x]*(2*ni)
    if mixed:
        xl=x-96
        lower=(r+xl*2.0**-28)/divisor
        assert 0<lower<MAX and math.isfinite(lower)
        for i in range(ni//2,ni):values[i]=lower;packed[i]=xl
    valid=[True]*(2*ni)
    if gap:valid[ni+5]=False
    g=bytearray(sections[3]);u32(g,6,2*ni);u32(g,30,ni);u32(g,34,2)
    north=-89 if negative else 90;g[46:50]=sm(north*1_000_000);g[55:59]=sm((north-1)*1_000_000)
    u32(g,50,10_000_000);u32(g,59,(10+ni-1)*1_000_000);u32(g,63,1_000_000);u32(g,67,1_000_000);g[71]=0
    p=bytearray(sections[4]);p[9]=2 if wind else 0;u32(p,18,6 if negative else 0)
    d=bytearray(sections[5]);u32(d,5,sum(valid));d[11:15]=struct.pack('>f',r);d[15:17]=(0x8000+28).to_bytes(2,'big');d[17:19]=(0x8000+300).to_bytes(2,'big');d[19]=32
    if all(valid):bitmap=(6).to_bytes(4,'big')+bytes([6,255])
    else:
        mask=bytearray((len(valid)+7)//8)
        for i,ok in enumerate(valid):
            if ok:mask[i//8]|=1<<(7-i%8)
        bitmap=(6+len(mask)).to_bytes(4,'big')+bytes([6,0])+mask
    packed_bytes=b''.join(v.to_bytes(4,'big') for i,v in enumerate(packed) if valid[i])
    payload=(5+len(packed_bytes)).to_bytes(4,'big')+b'\x07'+packed_bytes
    body=sections[1]+g+p+d+bitmap+payload+b'7777';header=bytearray(original[:16]);header[8:16]=(16+len(body)).to_bytes(8,'big');b=bytes(header)+body
    pole_row=values[ni:] if negative else values[:ni]
    mean=sum(map(Fraction.from_float,pole_row),Fraction())/ni
    band=(mean+Fraction.from_float(target))/2
    rows[name]={'file':name+'.grib2','sha256':hashlib.sha256(b).hexdigest(),'Ni':ni,'north':north,'negative':negative,'R':r,'E':-28,'D':-300,'width':32,'packed':packed,'decoded_binary64_hex':[v.hex() for v in values],'valid':valid,'pole_expected':float(mean),'band_expected':float(band),'reference':'Exact Fraction mean/half-band from finite decoded-node values; no floating weighted summation oracle'}
    fixtures[name]=b;(T/(name+'.grib2')).write_bytes(b);return b
for ni in [11,17,100]:make('positive'+str(ni),ni)
for ni in [11,17]:make('negative'+str(ni),ni,negative=True)
make('varying100',100,mixed=True);make('gap11',11,gap=True);make('wind11',11,wind=True)
helpers='\n'.join('''///|
fn numeric15_NAME() -> @grib2.GriddedField {
  @grib2.read_message(BYTES).unwrap()
}
'''.replace('NAME',name).replace('BYTES',mb(b)) for name,b in fixtures.items())
tests=r'''///|
fn numeric15_near(actual : Double?, expected : Double) -> Unit raise {
  let value = actual.unwrap()
  assert_true(!value.is_nan() && !value.is_inf())
  assert_true((value - expected).abs() / expected.abs() <= 4.0e-15)
}

///|
test "numeric15 finite polar constants and adjacent bands" {
  for field in [numeric15_positive11(), numeric15_positive17(), numeric15_positive100()] {
    for col in 0..<field.cols() { assert_eq(field.get(0, col), Some(1.7976931348623157e308)) }
    let pole = field.sample({ id: "north-pole", latitude: 90.0, longitude: 15.0 })
    assert_eq(pole.value, Some(1.7976931348623157e308))
    assert_eq(pole.algorithm, "bilinear-polar-scalar-mean")
    assert_eq(pole.contributors.length(), field.cols())
    numeric15_near(field.sample({ id: "north-band", latitude: 89.5, longitude: 15.5 }).value, 1.7976931348623157e308)
  }
}

///|
test "numeric15 negative south pole and adjacent band" {
  for field in [numeric15_negative11(), numeric15_negative17()] {
    for col in 0..<field.cols() { assert_eq(field.get(1, col), Some(-1.7976931348623157e308)) }
    let pole = field.sample({ id: "south-pole", latitude: -90.0, longitude: 15.0 })
    assert_eq(pole.value, Some(-1.7976931348623157e308))
    numeric15_near(field.sample({ id: "south-band", latitude: -89.5, longitude: 15.5 }).value, -1.7976931348623157e308)
  }
}

///|
test "numeric15 varying finite near-limit row follows exact mean" {
  let field = numeric15_varying100()
  let pole = field.sample({ id: "varying-pole", latitude: 90.0, longitude: 10.25 })
  numeric15_near(pole.value, POLE_EXPECTED)
  let lower = field.get(0, 99).unwrap()
  assert_true(pole.value.unwrap() >= lower && pole.value.unwrap() <= field.get(0, 0).unwrap())
  numeric15_near(field.sample({ id: "varying-band", latitude: 89.5, longitude: 10.25 }).value, BAND_EXPECTED)
  println("NUMERIC15|varying|" + pole.to_json().stringify())
}

///|
test "numeric15 overflow retry preserves positive-weight gaps and wind policy" {
  let field = numeric15_gap11()
  assert_eq(field.get(1, 5), None)
  let gap = field.sample({ id: "gap", latitude: 89.5, longitude: 15.5 })
  assert_eq(gap.value, None)
  assert_eq(gap.contributors.length(), 0)
  assert_eq(gap.algorithm, "outside-or-missing")
  assert_eq(field.sample({ id: "exact", latitude: 89.0, longitude: 16.0 }).value, Some(1.7976931348623157e308))
  assert_eq(field.sample({ id: "valid-pole", latitude: 90.0, longitude: 16.0 }).value, Some(1.7976931348623157e308))
  let wind = numeric15_wind11()
  assert_eq(wind.sample({ id: "wind-pole", latitude: 90.0, longitude: 15.0 }).value, None)
  assert_eq(wind.sample({ id: "wind-node", latitude: 89.0, longitude: 15.0 }).value, Some(1.7976931348623157e308))
}
'''
tests=tests.replace('POLE_EXPECTED',repr(rows['varying100']['pole_expected'])).replace('BAND_EXPECTED',repr(rows['varying100']['band_expected']))
(P/'numeric15_test.mbt').write_text(helpers+tests,encoding='utf-8')
b=fixtures['positive11']+fixtures['negative11']
main='''///|
// Synthetic finite-limit stress case, not a meteorological observation.
fn main {
  let fields = @grib2.read_fields(BYTES).unwrap()
  let requests : Array[@grib2.FieldRequest] = [
    { key: "north-max", query: @grib2.FieldQuery::new(0, 0, 0, time_unit=1, forecast_time=0) },
    { key: "south-min", query: @grib2.FieldQuery::new(0, 0, 0, time_unit=1, forecast_time=6) },
  ]
  let stations : Array[@grib2.Station] = [
    { id: "north-pole", latitude: 90.0, longitude: 15.0 },
    { id: "south-pole", latitude: -90.0, longitude: 15.0 },
    { id: "north-band", latitude: 89.5, longitude: 15.5 },
    { id: "south-band", latitude: -89.5, longitude: 15.5 },
  ]
  for chunk in @grib2.sample_requested_csv_records(fields, requests, stations).unwrap() {
    println(chunk[:chunk.length() - 1])
  }
}
'''.replace('BYTES',mb(b))
E=P/'cmd/extreme';E.mkdir(exist_ok=True);(E/'main.mbt').write_text(main,encoding='utf-8');(E/'moon.pkg').write_text((P/'cmd/direct/moon.pkg').read_text(encoding='utf-8'),encoding='utf-8')
reference={'cases':rows,'relative_tolerance':4e-15,'constant_pole_assertion':'Exact binary64 MAX/MIN after overflow retry','csv_values':[MAX,None,MAX,None,None,-MAX,None,-MAX],'csv_second_message_offset':len(fixtures['positive11']),'reference_method':'Fraction.from_float gives exact rational decoded-node values; means/half-bands evaluated rationally, rounded once for expected binary64. Fixture preconditions independently assert constant decoded nodes. No new ecCodes/download reference run.','not_meteorological_data':True}
(T/'REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n',encoding='utf-8');(R/'REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n',encoding='utf-8')
print('Generated8 focused numeric fixtures,4 tests and synthetic CSV example.')
