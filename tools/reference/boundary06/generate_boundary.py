from pathlib import Path
from fractions import Fraction
import json,hashlib,struct
R=Path(__file__).parent
P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
def split(b):
    out={};i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big');out[b[i+4]]=bytearray(b[i:i+n]);i+=n
    return out
def blob(b):return 'b"'+''.join(f'\\x{v:02x}' for v in b)+'"'
def sm(x):return ((-x)|0x80000000) if x<0 else x
def field(*,basic=0,subdiv=0xffffffff,lat=10000000,lon=10000000,step=1,mask=None,ip=False):
    ss=split(base)
    def u(b,i,x):b[i:i+4]=int(x).to_bytes(4,'big')
    g=ss[3];u(g,6,9);u(g,30,3);u(g,34,3);u(g,38,basic);u(g,42,subdiv)
    # Canonical north/west are supplied as integer angular ticks.
    u(g,46,sm(lat));u(g,50,lon+2*step if ip else lon)
    u(g,55,sm(lat-2*step));u(g,59,lon if ip else lon+2*step)
    u(g,63,step);u(g,67,step);g[71]=128 if ip else 0
    values=list(range(1,10))
    if ip:values=[v for j in range(3) for v in values[j*3:(j+1)*3][::-1]]
    if mask is None:mask=[True]*9
    packed=[v for v,m in zip(values,mask) if m]
    d=ss[5];u(d,5,len(packed));d[11:15]=struct.pack('>f',0);d[15:19]=b'\0'*4;d[19]=4
    if all(mask):ss[6]=bytearray(b'\0\0\0\6\6\xff')
    else:
        bits=''.join('1' if x else '0' for x in mask);pad=bits+'0'*((-len(bits))%8)
        ss[6]=bytearray((6+len(pad)//8).to_bytes(4,'big')+b'\6\0'+int(pad,2).to_bytes(len(pad)//8,'big'))
    bits=''.join(f'{v:04b}' for v in packed);pad=bits+'0'*((-len(bits))%8)
    payload=int(pad,2).to_bytes(len(pad)//8,'big') if pad else b''
    ss[7]=bytearray((5+len(payload)).to_bytes(4,'big')+b'\7'+payload)
    body=b''.join(ss[k] for k in [1,3,4,5,6,7])+b'7777'
    return base[:8]+(16+len(body)).to_bytes(8,'big')+body
cases=[('microdegree',dict()),('nanodegree',dict(basic=1,subdiv=1000000000,lat=1000000000,lon=1000000000)),('fine_reverse',dict(basic=1,subdiv=4000000000,lat=1000000000,lon=1000000000,ip=True))]
tests=[];records=[]
for name,kw in cases:
    data=field(**kw)
    unit=Fraction(1,1000000) if kw.get('basic',0)==0 else Fraction(kw['basic'],kw['subdiv'])
    lat=kw.get('lat',10000000)*unit;lon=kw.get('lon',10000000)*unit
    records.append({'name':name,'sha256':hashlib.sha256(data).hexdigest(),'unit':str(unit),'north':str(lat),'west':str(lon),'canonical_values':list(range(1,10)),'oracle':'Exact integer angular ticks and canonical1..9; API point/sample round trip must preserve node value'})
    tests.append(f'''///|
test "boundary06 {name} all public nodes round trip" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  for r in 0..<3 {{for c in 0..<3 {{
    let p=f.point(r,c).unwrap()
    assert_eq(f.get(r,c),Some((1+r*3+c).to_double()))
    let s=f.sample({{id:"node",latitude:p.latitude,longitude:p.longitude}})
    assert_eq(s.value,p.value)
    assert_eq(s.contributors.length(),1)
    assert_eq(s.contributors[0].source_index,p.source_index)
    assert_eq(s.contributors[0].weight,1.0)
  }}}}
}}
''')
    tests.append(f'''///|
test "boundary06 {name} crop exact public nodes and closed edges" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  for r in 0..<3 {{for c in 0..<3 {{
    let p=f.point(r,c).unwrap()
    let nodes=f.crop({{south:p.latitude,north:p.latitude,west:p.longitude,east:p.longitude}}).unwrap()
    assert_eq(nodes.length(),1)
    assert_eq(nodes[0].row,r);assert_eq(nodes[0].col,c)
  }}}}
  let a=f.point(0,0).unwrap();let z=f.point(2,1).unwrap()
  let nodes=f.crop({{south:z.latitude,north:a.latitude,west:a.longitude,east:z.longitude}}).unwrap()
  assert_eq(nodes.length(),6)
  for i,p in nodes {{assert_eq(p.row,i/2);assert_eq(p.col,i%2)}}
  let empty=f.crop({{south:z.latitude,north:a.latitude,west:a.longitude+f.dx*0.25,east:a.longitude+f.dx*0.5}}).unwrap()
  assert_eq(empty.length(),0)
}}
''')
    tests.append(f'''///|
test "boundary06 {name} no neighbour extrapolation" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let a=f.point(0,0).unwrap();let z=f.point(2,2).unwrap()
  assert_eq(f.interpolate_latlon(z.latitude-f.dy*0.125,z.longitude),None)
  assert_eq(f.interpolate_latlon(a.latitude+f.dy*0.125,a.longitude),None)
  assert_eq(f.interpolate_latlon(a.latitude,a.longitude-f.dx*0.125),None)
  assert_eq(f.interpolate_latlon(z.latitude,z.longitude+f.dx*0.125),None)
  // Fine angular units can put an outside inverse coordinate beyond Int32.
  assert_eq(f.interpolate_latlon(-90.0,180.0),None)
}}
''')
# Isolated southeast valid node ensures a restored edge does not acquire tiny missing weights.
mask=[False]*8+[True];data=field(mask=mask)
tests.append(f'''///|
test "boundary06 isolated valid southeast node" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let p=f.point(2,2).unwrap()
  assert_eq(f.interpolate_latlon(p.latitude,p.longitude),Some(9.0))
  assert_eq(f.interpolate_latlon(p.latitude+f.dy*0.125,p.longitude),None)
  assert_eq(f.interpolate_latlon(p.latitude,p.longitude-f.dx*0.125),None)
}}
''')
# A complete real-style dateline grid exercises normalized meridian equality.
data=field(lon=359999998)
tests.append(f'''///|
test "boundary06 dateline meridian extraction" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  for c in 0..<3 {{
    let p=f.point(0,c).unwrap()
    let nodes=f.crop({{south:f.point(2,0).unwrap().latitude,north:p.latitude,west:p.longitude,east:p.longitude}}).unwrap()
    assert_eq(nodes.length(),3)
    for n in nodes {{assert_eq(n.col,c)}}
    assert_eq(f.interpolate_latlon(p.latitude,p.longitude),p.value)
  }}
}}
''')
put=P/'boundary06_test.mbt';put.write_text('\n'.join(tests),encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps({'geometry_basis':'NOAA template3.0 note1; ratio basic angle/subdivisions, default1e-6','url':'https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_temp3-0.shtml','fixtures':records,'acceptance':'Exact public node samples keep their valid value and single contributor; zero-width meridians select only that column, empty intervals remain empty, nearby outside/missing points stay None'},indent=2))
(R/'fixture.grib2').write_bytes(field())
print('Generated',len(tests),'bounded boundary regressions')
