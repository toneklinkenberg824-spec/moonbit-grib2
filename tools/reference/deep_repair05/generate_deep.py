from pathlib import Path
from fractions import Fraction
import struct,json,math,hashlib
import numpy as np
R=Path(__file__).parent
P=Path(__file__).resolve().parents[3]
def blob(data):return 'b"'+''.join(f'\\x{x:02x}' for x in data)+'"'
def mb_floats(values):
    def f(x):
        s=repr(x)
        if 'e' in s and '.' not in s.split('e')[0]:s=s.replace('e','.0e')
        return s
    return '['+','.join(f(v) for v in values)+']'
def sections(data):
    s={};i=16
    while i<len(data)-4:
        n=int.from_bytes(data[i:i+4],'big');s[data[i+4]]=data[i:i+n];i+=n
    return s
base=(P/'testdata/constant.grib2').read_bytes(); original=sections(base)
def make(values,bits=3,E=0,D=0,ref=0.,mask=None,grid=None,product=None):
    parts={n:bytearray(v) for n,v in original.items()}
    g=parts[3]
    if grid:
        ni,nj,north,south,west,east,dx,dy,scan=grid
        for pos,value in [(6,ni*nj),(30,ni),(34,nj),(46,round(abs(north)*1e6)|(0x80000000 if north<0 else 0)),(50,round(west*1e6)),(55,round(abs(south)*1e6)|(0x80000000 if south<0 else 0)),(59,round(east*1e6)),(63,round(dx*1e6)),(67,round(dy*1e6))]:g[pos:pos+4]=value.to_bytes(4,'big')
        g[71]=scan
    if product:
        unit,time,category,param=product
        parts[4][17]=unit;parts[4][18:22]=time.to_bytes(4,'big');parts[4][9]=category;parts[4][10]=param
    d=parts[5]
    d[5:9]=len(values).to_bytes(4,'big');d[11:15]=struct.pack('>f',ref)
    for pos,value in [(15,E),(17,D)]:d[pos:pos+2]=((0x8000|abs(value)) if value<0 else value).to_bytes(2,'big')
    d[19]=bits
    if mask is not None:
        payload=sum((1<<(7-i)) for i,b in enumerate(mask) if b)
        parts[6]=bytearray(b'\0\0\0\7\6\0'+bytes([payload]))
    encoded=''.join(f'{x:0{bits}b}' for x in values) if bits else ''
    encoded+='0'*((-len(encoded))%8)
    payload=int(encoded,2).to_bytes(len(encoded)//8,'big') if encoded else b''
    parts[7]=bytearray((5+len(payload)).to_bytes(4,'big')+b'\7'+payload)
    body=b''.join(parts[n] for n in [1,3,4,5,6,7])+b'7777'
    return base[:8]+(16+len(body)).to_bytes(8,'big')+body
tests=[];records=[]
cases=[('normal-width-'+str(b)+'-scale'+str(j),b,[-5,0,7][j],[-2,0,2][j],-1.25,[0,1,2,3,(1<<b)-1,1]) for b in [2,11,13,17,31,32] for j in range(3)]
cases += [('balanced-1024',1,1024,308,0.,[1]*6),('small-term-recovered',1,-1075,-308,0.,[1]*6),('subnormal-recovered',1,0,324,10.,[0]*6),('small-reference-recovered',1,0,-324,1e-30,[0]*6),('balanced-max-positive',1,32766,9863,0.,[1]*6),('balanced-max-negative',1,-32766,-9863,0.,[1]*6)]
cases += [('subnormal-constant-same-formula',0,3,324,10.,[0]*6),('large-constant-same-formula',0,3,-324,1e-30,[0]*6)]
for name,b,E,D,ref,values in cases:
    data=make(values,b,E,D,ref)
    real_ref=struct.unpack('>f',struct.pack('>f',ref))[0]
    expected=[float((Fraction.from_float(real_ref)+Fraction(x)*Fraction(2)**E)*Fraction(10)**(-D)) for x in values]
    records.append({'name':name,'bits':b,'E':E,'D':D,'R_float32':real_ref,'X':values,'fraction_expected_float':expected,'sha256':hashlib.sha256(data).hexdigest()})
    tests.append(f'''///|
test "deep numeric {name}" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let expected : Array[Double]={mb_floats(expected)}
  let mut max_relative=0.0
  for i in 0..<6 {{
    let actual=f.values()[i]
    assert_true(!actual.is_nan() && !actual.is_inf())
    if expected[i]!=0.0 {{assert_true(actual!=0.0)}}
    if expected[i]!=0.0 {{let relative=((actual-expected[i])/expected[i]).abs();if relative>max_relative {{max_relative=relative}}}}
    if expected[i].abs()<1.0e-290 {{assert_true((actual-expected[i]).abs()<=5.0e-324)}}
    else {{assert_true((actual-expected[i]).abs()<=expected[i].abs()*2.0e-12+1.0e-300)}}
  }}
  println("DEEP_NUMERIC|{name}|"+max_relative.to_string())
}}
''')
# Encoded nonfinite reference is rejected even with no valid payload values.
for label,value in [('nan',float('nan')),('inf',float('inf')),('negative-inf',float('-inf'))]:
    data=make([],bits=1,ref=value,mask=[False]*6)
    tests.append(f'///|\ntest "deep reject nonfinite empty {label}" {{assert_true(@grib2.read_message({blob(data)}) is Err(CorruptedBitstream(_)))}}\n')
near_pole=make([1,2,3,4,5,6],grid=(3,2,89.999999,89.999998,10,12,1,.000001,0))
node=make([5],mask=[False,False,False,False,True,False,False,False,False],grid=(3,3,10,9.8,10,10.2,.1,.1,0)) if False else None
# Nine-bit bitmap requires a second byte: build a3x3 fixture through a full field then insert its mask.
node=make(list(range(1,10)),bits=4,grid=(3,3,10,9.8,10,10.2,.1,.1,0))
ns=sections(node);ns[5]=ns[5][:5]+(1).to_bytes(4,'big')+ns[5][9:];ns[6]=b'\0\0\0\10\6\0\x08\0';ns[7]=b'\0\0\0\6\7\x50';body=b''.join(ns[n] for n in [1,3,4,5,6,7])+b'7777';node=node[:8]+(16+len(body)).to_bytes(8,'big')+body
global_data=(P/'testdata/scipy.grib2').read_bytes()
queries=[1e20,-1e20,1e308,-1e308]
def periodic_value(lon):
    x=math.fmod(lon,360.)%360; return float(np.interp(x,[0,90,180,270,360],[13,14,15,16,13]))
expected=[periodic_value(x) for x in queries]
tests.append(f'''///|
test "deep finite large longitude modulo" {{
  let f=@grib2.read_message({blob(global_data)}).unwrap()
  let queries : Array[Double]={mb_floats(queries)}
  let expected : Array[Double]={mb_floats(expected)}
  for i,q in queries {{assert_true((f.interpolate_latlon(1.0,q).unwrap()-expected[i]).abs()<1.0e-12)}}
}}
///|
test "deep microdegree row is not an actual pole" {{
  let f=@grib2.read_message({blob(near_pole)}).unwrap()
  assert_eq(f.interpolate_latlon(89.999999,10.0),Some(1.0))
  assert_eq(f.interpolate_latlon(90.0,10.0),None)
}}
///|
test "deep exact public node ignores zero-weight missing corners" {{
  let f=@grib2.read_message({blob(node)}).unwrap()
  let p=f.point(1,1).unwrap()
  assert_eq(f.get(1,1),Some(5.0))
  assert_eq(f.interpolate_latlon(p.latitude,p.longitude),Some(5.0))
  assert_eq(f.interpolate_latlon(9.9,10.1),Some(5.0))
  assert_eq(f.interpolate_latlon(9.90000000001,10.1),None)
}}
''')
# Extra contract coverage: unit filtering must not silently convert identical forecast integers.
unit_fields=[make([1]*6,product=(u,6,0,0)) for u in [1,2,13]]
unit_data=b''.join(unit_fields)
tests.append(f'''///|
test "deep parameter and original time unit selection" {{
  let fs=@grib2.read_fields({blob(unit_data)},max_points=6).unwrap()
  assert_eq(fs.length(),3)
  assert_eq(@grib2.select_fields(fs,0,0,0,forecast_time=6).length(),3)
  for unit in [1,2,13] {{assert_eq(@grib2.select_fields(fs,0,0,0,time_unit=unit,forecast_time=6).length(),1)}}
  assert_eq(@grib2.select_fields(fs,0,0,1).length(),0)
  assert_eq(@grib2.select_fields(fs,0,0,0,time_unit=0).length(),0)
  assert_true(@grib2.read_fields({blob(unit_fields[0])},max_points=5) is Err(InvalidGrid(_)))
}}
''')
(P/'deep_repair_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
privacy=f'''fn main {{
  let f=@grib2.read_message({blob(base)}).unwrap()
  f.data[0]=123.0
  println(f.get(0,0).unwrap())
  f.valid[0]=false
  println(f.get(0,0) is None)
  f.source_indices[0] = -9
  println(f.point(0,0).unwrap().source_index)
  f.product_info.reference_time[0]=0
  println(f.product().reference_time[0])
}}
'''
(R/'external-before-mutation.mbt').write_text(privacy)
(R/'external-workspace/consumer/main.mbt').write_text(privacy)
(R/'REFERENCE.json').write_text(json.dumps({'numeric_oracle':'Exact fractions from float32 R + integer X, powers2 and10, rounded once by Python float; no product output','numeric_cases':records,'longitude_oracle':'Python math.fmod + independent numpy.interp periodic values','queries':queries,'longitude_expected':expected,'pole_oracle':'89.999999 is one encoded microdegree below90; exact node remains1','node_oracle':'Only center node valid5; public point must sample back to5'},indent=2),encoding='utf-8')
print('Generated',len(cases),'numeric cases,3 nonfinite header cases and4 domain/filter regressions')
