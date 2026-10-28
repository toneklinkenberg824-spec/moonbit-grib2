from pathlib import Path
from fractions import Fraction
import struct,json,hashlib,sys
R=Path(__file__).parent
P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
def sections(b):
    out={};i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big');out[b[i+4]]=bytearray(b[i:i+n]);i+=n
    return out
def u(b,i,x,n=4):b[i:i+n]=int(x).to_bytes(n,'big')
def sm(x):return (0x80000000|-x) if x<0 else x
def blob(b):return 'b"'+''.join(f'\\x{v:02x}' for v in b)+'"'
def message(ss,order=(1,3,4,5,6,7)):
    body=b''.join(ss[k] for k in order)+b'7777'
    return base[:8]+(16+len(body)).to_bytes(8,'big')+body
def grid(**kw):
    ss=sections(base);g=ss[3]
    pos={'ni':30,'nj':34,'basic':38,'subdiv':42,'lat1':46,'lon1':50,'lat2':55,'lon2':59,'dx':63,'dy':67}
    for k,x in kw.items():
        if k=='scan':g[71]=x
        else:u(g,pos[k],sm(x) if k.startswith('lat') else x)
    # Keep the existing 3x2 constant7 packing; changed shapes retain six points.
    return message(ss)
bad=[
 ('encoded_longitude361',dict(lon1=361000000,lon2=363000000)),
 ('encoded_last_longitude372',dict(lon2=372000000)),
 ('encoded_north_over90',dict(lat1=90000001,lat2=89000001)),
 ('encoded_south_below90',dict(lat1=-89000001,lat2=-90000001)),
 ('inferred_north_over90',dict(scan=64,lat1=89000001,lat2=90000000)),
 ('inferred_south_below90',dict(lat1=-89000001,lat2=-90000000)),
 ('extent_over360',dict(basic=1,subdiv=2000000,lat1=2000000,lat2=0,lon1=0,lon2=0,dx=360000001,dy=2000000)),
]
tests=[];records=[]
for name,kw in bad:
    b=grid(**kw);records.append({'name':name,'sha256':hashlib.sha256(b).hexdigest(),'raw':kw,'expected':'InvalidGrid','basis':'WMO92.1.7/8 physical domain; integer angular extents, not binary64 slack'})
    tests.append(f'''///|
test "encoding07 reject {name}" {{
  assert_true(@grib2.read_message({blob(b)}) is Err(InvalidGrid(_)))
}}
''')
# Include finite legal boundaries that would be lost by a naive strict binary64 test.
den=next(d for d in range(2,500) if (90*d)*(1.0/d)>90.0)
north=grid(basic=1,subdiv=den,lat1=90*den,lat2=89*den,lon1=0,lon2=2*den,dx=den,dy=den)
south=grid(basic=1,subdiv=den,lat1=-89*den,lat2=-90*den,lon1=0,lon2=2*den,dx=den,dy=den)
for name,b,row,expected in [('exact_north',north,0,90.0),('exact_south',south,1,-90.0)]:
    records.append({'name':name,'sha256':hashlib.sha256(b).hexdigest(),'unit':str(Fraction(1,den)),'exact_latitude':expected,'premultiplied_double':(90*den)*(1.0/den)})
    tests.append(f'''///|
test "encoding07 legal {name} has physical public coordinate" {{
  let f=@grib2.read_message({blob(b)}).unwrap()
  let p=f.point({row},0).unwrap()
  assert_eq(p.latitude,{expected})
  let s=f.sample({{id:"pole",latitude:p.latitude,longitude:p.longitude}})
  assert_true((s.value.unwrap()-7.0).abs()<1.0e-12)
  for c in s.contributors {{assert_eq(c.latitude,{expected})}}
  let nodes=f.crop({{south:{expected},north:{expected},west:0.0,east:360.0}}).unwrap()
  assert_eq(nodes.length(),3)
}}
''')
wrap0=grid(lon1=0,lon2=360000000,dx=180000000)
wrap360=grid(lon1=360000000,lon2=2000000,dx=1000000)
tests.append(f'''///|
test "encoding07 legal longitude0 and360" {{
  for b in [{blob(wrap0)},{blob(wrap360)}] {{
    let f=@grib2.read_message(b).unwrap()
    assert_eq(f.point(0,0).unwrap().longitude,0.0)
    assert_eq(f.interpolate_latlon(1.0,0.0),Some(7.0))
  }}
}}
''')
empty=message(sections(base),order=(1,))
for name,data in [('empty_alone',empty),('empty_prefix',empty+base),('empty_suffix',base+empty),('empty_middle',base+empty+base)]:
    tests.append(f'''///|
test "encoding07 reject {name} in all or error stream" {{
  assert_true(@grib2.read_fields({blob(data)}) is Err(CorruptedBitstream(_)))
  assert_true(@grib2.read_message({blob(data)}) is Err(_))
}}
''')
# Unchanged semantics: independent sign-magnitude/unsigned metadata edge oracle.
meta=[]
for fraw,sraw,vraw in [(0x80000000,0x80,0x80000001),(0x80000006,0xfe,0xfffffffe),(0x7fffffff,0x7f,0),(0xfffffffe,0xff,0xffffffff),(0xffffffff,0,42)]:
    ss=sections(base);p=ss[4];p[17]=13;u(p,18,fraw);p[22]=100;p[23]=sraw;u(p,24,vraw)
    p[28]=103;p[29]=0x82;u(p,30,0x80000000)
    b=message(ss)
    f=None if fraw==0xffffffff else (-(fraw&0x7fffffff) if fraw&0x80000000 else fraw)
    s=None if sraw==255 else (-(sraw&127) if sraw&128 else sraw)
    v=None if vraw==0xffffffff else vraw
    meta.append({'bytes':b,'forecast_time':f,'scale':s,'scaled_value':v,'raw':[fraw,sraw,vraw]})
    opt=lambda x,suffix='':'None' if x is None else f'Some({x}{suffix})'
    tests.append(f'''///|
test "encoding07 signed forecast and unsigned surface {fraw:x}" {{
  let f=@grib2.read_message({blob(b)}).unwrap()
  let p=f.product()
  assert_eq(p.forecast_time,{opt(f)})
  assert_eq(p.time_unit,13)
  assert_eq(p.first_surface.scale,{opt(s)})
  assert_eq(p.first_surface.scaled_value,{opt(v,'U')})
  assert_eq(p.second_surface.scale,Some(-2))
  assert_eq(p.second_surface.scaled_value,Some(2147483648U))
}}
''')
observations=[]
if '--eccodes' in sys.argv:
    import eccodes as ec
    for m in meta:
        h=ec.codes_new_from_message(m['bytes'])
        obs={}
        for key,expected in [('forecastTime',m['forecast_time']),('scaleFactorOfFirstFixedSurface',m['scale']),('scaledValueOfFirstFixedSurface',m['scaled_value'])]:
            value=None if ec.codes_is_missing(h,key) else ec.codes_get(h,key)
            # Windows ecCodes' default integer getter can expose UInt32 through
            # a signed C long. Preserve that observation separately from raw-byte
            # unsigned semantics and ask the double accessor as an independent check.
            if key=='scaledValueOfFirstFixedSurface' and expected is not None and expected>=0x80000000:
                obs['unsigned_default_integer_matches']=value==expected
                obs['unsigned_double_accessor']=ec.codes_get_double(h,key)
            elif key=='forecastTime' and expected is None:
                obs['all_ones_missing_matches_regulation']=value is None
            else:assert value==expected,(key,value,expected)
            obs[key]=value
        ec.codes_release(h);observations.append(obs)
    print('ecCodes',ec.codes_get_api_version(),'observed',len(meta),'metadata edge fields; accessor divergences retained')
(R/'REFERENCE.json').write_text(json.dumps({'basis':['https://codes.ecmwf.int/grib/format/grib2/regulations/','https://codes.ecmwf.int/grib/format/grib2/overview/','https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_temp3-0.shtml','https://raw.githubusercontent.com/ecmwf/eccodes/2.50.0/definitions/grib2/templates/template.4.horizontal.def'],'geometry':records,'pole_denominator':den,'metadata':[{k:v for k,v in m.items() if k!='bytes'} for m in meta],'eccodes_observations':observations,'empty_message':'Section0+Section1+Section8; required3–7 absent; every concatenation position must error'},indent=2))
(P/'encoding07_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
(R/'invalid-grid.grib2').write_bytes(grid(**bad[0][1]));(R/'empty-prefix.grib2').write_bytes(empty+base);(R/'valid-pole.grib2').write_bytes(north)
print('Generated',len(tests),'encoding/message validation regressions; pole denominator',den)
