from pathlib import Path
import numpy as np
from generate_deep import make,blob,sections,P,R,base
code=[]
mask=[True,False,True,True,False,False]
expanded=[1.,0.,2.,3.,0.,0.]
for scan in range(0,256,16):
    ip=bool(scan&128);jp=bool(scan&64)
    data=make([1,2,3],bits=2,mask=mask,grid=(3,2,0 if jp else 1,1 if jp else 0,12 if ip else 10,10 if ip else 12,1,1,scan))
    if scan&32:
        a=np.arange(6).reshape(3,2)
        if scan&16:a[1::2]=a[1::2,::-1]
        a=a.T
    else:
        a=np.arange(6).reshape(2,3)
        if scan&16:a[1::2]=a[1::2,::-1]
    if ip:a=a[:,::-1]
    if jp:a=a[::-1]
    order=a.ravel().tolist()
    valid=[mask[i] for i in order];expected=[expanded[i] for i in order]
    code.append(f'''///|
test "deep combined bitmap scan{scan}" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let expected : Array[Double]={expected!r}
  let valid={str(valid).lower()}
  let source={order!r}
  for r in 0..<2 {{for c in 0..<3 {{
    let i=r*3+c
    let p=f.point(r,c).unwrap()
    assert_eq(p.source_index,source[i])
    assert_eq(p.latitude,1.0-r.to_double())
    assert_eq(p.longitude,10.0+c.to_double())
    assert_eq(f.mask()[i],valid[i])
    if valid[i] {{assert_eq(p.value,Some(expected[i]))}} else {{assert_eq(p.value,None)}}
  }}}}
}}
''')
def message(parts):
    body=b''.join(parts)+b'7777';return base[:8]+(16+len(body)).to_bytes(8,'big')+body
first=sections(make([1,2,3],bits=3,mask=mask));middle=sections(make([4]*6));last=sections(make([5,6,7],bits=3,mask=mask))
reuse=b'\0\0\0\6\6\xfe'
chain=message([first[n] for n in [1,3,4,5,6,7]]+[middle[n] for n in [4,5,6,7]]+[last[4],last[5],reuse,last[7]])
reset=message([last[n] if n!=6 else reuse for n in [1,3,4,5,6,7]])
other=sections(make([5,6,7],bits=3,mask=[True,False,True,True],grid=(2,2,1,0,10,11,1,1,0)))
bad_grid_reuse=message([first[n] for n in [1,3,4,5,6,7]]+[other[n] if n!=6 else reuse for n in [3,4,5,6,7]])
pole=make([1,2,3,4,5,6],bits=3,grid=(3,2,90,89,10,12,1,1,0))
shifted=make([23,24,25,26,13,14,15,16,3,4,5,6],bits=5,grid=(4,3,2,0,10,280,90,1,0))
overflow=make([1]*6,bits=1,E=32767,D=0)
underflow=make([1]*6,bits=1,E=-32766,D=0)
code.append(f'''///|
test "deep bitmap254 survives intervening255 but resets at message boundary" {{
  let fields=@grib2.read_fields({blob(chain)}).unwrap()
  assert_eq(fields.length(),3)
  assert_eq(fields[1].mask(),[true,true,true,true,true,true])
  assert_eq(fields[2].mask(),[true,false,true,true,false,false])
  assert_eq(fields[2].get(0,0),Some(5.0))
  assert_eq(fields[2].get(1,0),Some(7.0))
  assert_true(@grib2.read_fields({blob(message([first[n] for n in [1,3,4,5,6,7]])+reset)}) is Err(CorruptedBitstream(_)))
  assert_true(@grib2.read_fields({blob(bad_grid_reuse)}) is Err(CorruptedBitstream(_)))
}}
///|
test "deep regional pole stays within its longitude domain" {{
  let f=@grib2.read_message({blob(pole)}).unwrap()
  assert_eq(f.interpolate_latlon(90.0,10.0),Some(2.0))
  assert_eq(f.interpolate_latlon(90.0,9.0),None)
  assert_eq(f.interpolate_latlon(89.5,10.0),Some(3.0))
}}
///|
test "deep large longitude is reduced before subtracting grid or bbox origin" {{
  let f=@grib2.read_message({blob(shifted)}).unwrap()
  assert_eq(f.interpolate_latlon(1.0,1.0e20),Some(16.0))
  let nodes=f.crop({{south:0.0,north:2.0,west:1.0e20,east:1.0e20}}).unwrap()
  assert_eq(nodes.length(),3)
  for p in nodes {{assert_eq(p.longitude,280.0)}}
}}
///|
test "deep true numeric overflow is rejected and true underflow rounds to zero" {{
  assert_true(@grib2.read_message({blob(overflow)}) is Err(CorruptedBitstream(_)))
  let f=@grib2.read_message({blob(underflow)}).unwrap()
  assert_eq(f.values(),[0.0,0.0,0.0,0.0,0.0,0.0])
}}
''')
(P/'deep_contract_test.mbt').write_text('\n'.join(code),encoding='utf-8')
print('Generated16 combined scan/mask cases and4 scoped contract tests')
