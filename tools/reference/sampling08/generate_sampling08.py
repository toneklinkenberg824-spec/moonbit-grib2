from pathlib import Path
from fractions import Fraction
import struct,json,hashlib
R=Path(__file__).parent
P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
def sections(b):
    out={};i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big');out[b[i+4]]=bytearray(b[i:i+n]);i+=n
    return out
def u(b,i,x,n=4):b[i:i+n]=int(x).to_bytes(n,'big')
def sm(x):return 0x80000000|-x if x<0 else x
def blob(b):return 'b"'+''.join(f'\\x{v:02x}' for v in b)+'"'
def lit(x):
    s=repr(x)
    return s.replace('e','.0e') if 'e' in s and '.' not in s.split('e')[0] else s
def field(values,ni=2,nj=2,north=1,mask=None,e=-1074,d=0,ref=0.,bits=3):
    ss=sections(base);g=ss[3];n=ni*nj
    u(g,6,n);u(g,30,ni);u(g,34,nj);u(g,46,sm(north*1000000));u(g,55,sm((north-nj+1)*1000000));u(g,50,10000000);u(g,59,(9+ni)*1000000)
    u(g,63,1000000);u(g,67,1000000);g[71]=0
    if mask is None:mask=[True]*n
    packed=[v for v,m in zip(values,mask) if m]
    ds=ss[5];u(ds,5,len(packed));ds[11:15]=struct.pack('>f',ref);u(ds,15,0x8000|-e if e<0 else e,2);u(ds,17,0x8000|-d if d<0 else d,2);ds[19]=bits
    if all(mask):ss[6]=bytearray(b'\0\0\0\6\6\xff')
    else:
        b=''.join('1' if m else '0' for m in mask);b+='0'*((-len(b))%8)
        ss[6]=bytearray((6+len(b)//8).to_bytes(4,'big')+b'\6\0'+int(b,2).to_bytes(len(b)//8,'big'))
    stream=''.join(f'{v:0{bits}b}' for v in packed) if bits else '';stream+='0'*((-len(stream))%8)
    b=int(stream,2).to_bytes(len(stream)//8,'big') if stream else b''
    ss[7]=bytearray((5+len(b)).to_bytes(4,'big')+b'\7'+b)
    body=b''.join(ss[k] for k in [1,3,4,5,6,7])+b'7777'
    return base[:8]+(16+len(body)).to_bytes(8,'big')+body
tiny=Fraction(1,1<<1074)
cases=[]
for v in [1,2,3]:cases.append((f'constant_{v}_ulp',[v]*4,dict(),.5,10.5,tiny*v,[Fraction(1,4)]*4))
cases.append(('mixed_round_once',[1,1,1,3],dict(),.5,10.5,tiny*Fraction(3,2),[Fraction(1,4)]*4))
cases.append(('edge_zero_missing',[1,1,0,0],dict(mask=[True,True,False,False]),1.,10.5,tiny,[Fraction(1,2)]*2))
cases.append(('pole_equal',[1,1,1,2,3,4],dict(ni=3,nj=2,north=90),90.,10.5,tiny,[Fraction(1,3)]*3))
cases.append(('pole_adjacent',[1,1,1,2,3,4],dict(ni=3,nj=2,north=90),89.5,10.5,tiny*Fraction(7,4),[Fraction(1,6)]*3+[Fraction(1,4)]*2))
cases.append(('pole_masked',[1,0,1,2,3,4],dict(ni=3,nj=2,north=90,mask=[True,False,True,True,True,True]),90.,10.5,tiny,[Fraction(1,2)]*2))
cases.append(('negative_constant',[0]*4,dict(bits=0,ref=-5.,d=324,e=0),.5,10.5,Fraction.from_float(float(Fraction(-5,10**324))),[Fraction(1,4)]*4))
cases.append(('normal_constant',[1]*4,dict(e=-1022),.5,10.5,Fraction(1,1<<1022),[Fraction(1,4)]*4))
cases.append(('ordinary_values',[1,2,3,4],dict(e=0),.5,10.5,Fraction(5,2),[Fraction(1,4)]*4))
tests=[];records=[]
for name,vs,kw,lat,lon,expected,weights in cases:
    b=field(vs,**kw);want=float(expected)
    records.append({'name':name,'sha256':hashlib.sha256(b).hexdigest(),'packed':vs,'packing':kw,'station':[lat,lon],'exact_expected':str(expected),'rounded_expected':want,'expected_binary64_bits':struct.unpack('>Q',struct.pack('>d',want))[0],'weights':[str(w) for w in weights],'oracle':'Exact Fraction sum of decoded binary64 field values and analytic rational weights, rounded once; no product output'})
    tests.append(f'''///|
test "sampling08 {name}" {{
  let f=@grib2.read_message({blob(b)}).unwrap()
  let s=f.sample({{id:"tiny",latitude:{lat},longitude:{lon}}})
  let expected : Double={lit(want)}
  assert_eq(s.value,Some(expected))
  assert_eq(s.value.unwrap().reinterpret_as_uint64(),{records[-1]['expected_binary64_bits']}UL)
  assert_eq(s.contributors.length(),{len(weights)})
  let weights : Array[Double>=[{','.join(lit(float(w)) for w in weights)}]
  for i,c in s.contributors {{assert_eq(c.weight,weights[i])}}
}}
'''.replace('Array[Double>','Array[Double]'))
missing=field([1]*4,mask=[True,False,True,True]);allmissing=field([0]*4,mask=[False]*4)
tests.append(f'''///|
test "sampling08 positive weight missing remains absent" {{
  for b in [{blob(missing)},{blob(allmissing)}] {{
    let f=@grib2.read_message(b).unwrap()
    let s=f.sample({{id:"missing",latitude:0.5,longitude:10.5}})
    assert_eq(s.value,None);assert_eq(s.contributors.length(),0)
  }}
}}
''')
(P/'sampling08_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps({'basis':'Accepted scalar coordinate bilinear/polar policy; WMO5.0 decode formula then exact analytic weighted mean','source':'https://codes.ecmwf.int/grib/format/grib2/regulations/','cases':records,'normal_path':'The minimum normal and ordinary-value regressions ensure the established arithmetic path remains valid'},indent=2),encoding='utf-8')
(R/'consumer-fixture.grib2').write_bytes(field([1]*4))
print('Generated',len(tests),'sampling regressions from exact Fraction expectations')
