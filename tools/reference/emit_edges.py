from pathlib import Path
import struct,json
R=Path(__file__).parent; P=Path(__file__).resolve().parents[2]
def blob(d):return 'b"'+''.join(f'\\x{x:02x}' for x in d)+'"'
def sections(d):
    out={}; i=16
    while i<len(d)-4:
        n=int.from_bytes(d[i:i+4],'big'); out[d[i+4]]=(i,d[i:i+n]); i+=n
    return out
def message(parts,base):
    body=b''.join(parts)+b'7777'; return base[:8]+(16+len(body)).to_bytes(8,'big')+body
base=(R/'fixtures/bitmap.grib2').read_bytes(); s=sections(base)
scan=(R/'fixtures/scipy.grib2').read_bytes(); ss=sections(scan)
multi_parts=[s[1][1],b'\0\0\0\x08\x02\xaa\xbb\xcc',s[3][1],s[4][1],s[5][1],s[6][1],s[7][1],s[4][1],s[5][1],b'\0\0\0\x06\x06\xfe',s[7][1]]
multi=message(multi_parts,base)
reset=message([s[i][1] if i!=6 else b'\0\0\0\x06\x06\xfe' for i in [1,3,4,5,6,7]],base)
cases=[]
def altered(name,d,offset,value):
    a=bytearray(d); a[offset]=value; cases.append((name,bytes(a)))
for sec,off in [(3,13),(4,8),(5,10)]:altered('unsupported'+str(sec),base,s[sec][0]+off,1)
altered('staggered',base,s[3][0]+71,1)
altered('badmagic',base,0,0)
altered('bitmap-predefined',base,s[6][0]+5,1)
altered('bad-count',base,s[5][0]+8,0)
altered('bad-width',base,s[5][0]+19,33)
badscale=bytearray(base);badscale[s[5][0]+15:s[5][0]+17]=b'\xff\xff';cases.append(('missing-scale',bytes(badscale)))
altered('bad-ni',base,s[3][0]+33,0)
altered('edition',base,7,1)
altered('badterminator',base,len(base)-1,0)
for length in [0,4,0x7fffffff,0xffffffff]:
    a=bytearray(base); a[s[3][0]:s[3][0]+4]=length.to_bytes(4,'big');cases.append(('length'+str(length),bytes(a)))
cases.append(('incomplete-section3',message([s[1][1],s[3][1]],base)))
cases.append(('bitmap-reset',base+reset))
# True non-default angular unit: 1/1000 degree, headers represented in those units.
basic=bytearray(scan); g0=ss[3][0]
basic[g0+38:g0+42]=(1).to_bytes(4,'big'); basic[g0+42:g0+46]=(1000).to_bytes(4,'big')
for off in [46,50,55,59,63,67]:
    v=int.from_bytes(basic[g0+off:g0+off+4],'big');basic[g0+off:g0+off+4]=(v//1000).to_bytes(4,'big')
# Same grid crossing date line, unchanged data.
date=bytearray(base); g0=s[3][0]
date[g0+50:g0+54]=(350000000).to_bytes(4,'big');date[g0+59:g0+63]=(10000000).to_bytes(4,'big');date[g0+63:g0+67]=(10000000).to_bytes(4,'big')
edge=['// Contract edge paths; binary mutations are intentional malformed inputs.\n']
edge.append(f'''///|
test "all byte truncations fail without panic" {{
  let data={blob(base)}
  for n in 0..<data.length() {{assert_true(@grib2.read_fields(data[:n].to_owned()) is Err(_))}}
}}
///|
test "optional section2, inherited grid, bitmap254 and multiple messages" {{
  let fields=@grib2.read_fields({blob(multi)}).unwrap()
  assert_eq(fields.length(),2)
  assert_eq(fields[0].mask(),fields[1].mask())
  assert_eq(fields[0].get(0,0),fields[1].get(0,0))
  assert_eq(fields[1].local_use(),Some(b"\\x00\\x00\\x00\\x08\\x02\\xaa\\xbb\\xcc"))
  assert_eq(fields[1].origin().field,1)
  let concatenated=@grib2.read_fields({blob(base+base)}).unwrap()
  assert_eq(concatenated.length(),2)
  assert_eq(concatenated[1].origin().message,1)
  assert_eq(concatenated[1].origin().byte_offset,{len(base)})
  assert_true(@grib2.read_message({blob(base+base)}) is Err(InvalidRequest(_)))
}}
///|
test "basic-angle units and regional dateline topology" {{
  let f=@grib2.read_message({blob(basic)}).unwrap()
  assert_eq(f.point(1,2).unwrap().latitude,1.0)
  assert_eq(f.point(1,2).unwrap().longitude,180.0)
  let d=@grib2.read_message({blob(date)}).unwrap()
  assert_eq(d.interpolate_latlon(0.0,-10.0),Some(4.0))
  assert_eq(d.interpolate_latlon(0.0,0.0),Some(5.0))
  assert_eq(d.interpolate_latlon(0.0,180.0),None)
}}
''')
for name,data in cases:
    edge.append(f'///|\ntest "reject {name}" {{ assert_true(@grib2.read_fields({blob(data)}) is Err(_)) }}\n')
edge.append(f'''///|
test "typed product identifiers, forecast and surfaces" {{
  let p=@grib2.read_message({blob(base)}).unwrap().product()
  assert_eq(p.discipline,0)
  assert_eq(p.category,0)
  assert_eq(p.parameter,0)
  assert_eq(p.time_unit,1)
  assert_eq(p.forecast_time,Some(0))
  assert_eq(p.first_surface.kind,1)
  assert_eq(p.second_surface.kind,255)
}}
''')
(P/'errors_test.mbt').write_text('\n'.join(edge))
print('Emitted',len(cases),'malformed/matrix edge cases plus truncation and multi-message tests')
