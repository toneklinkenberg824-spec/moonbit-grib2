from pathlib import Path
import json, shutil
import numpy as np
from scipy.interpolate import RegularGridInterpolator
R=Path(__file__).parent
P=Path(__file__).resolve().parents[2]
ref=json.loads((R/'REFERENCE.json').read_text())
real=json.loads((R/'REAL-REFERENCE.json').read_text())
def mb(x):
    if x is None:return 'None'
    if isinstance(x,bool):return str(x).lower()
    if isinstance(x,list):return '['+','.join(mb(v) for v in x)+']'
    return repr(x)
def blob(data):return 'b"'+''.join(f'\\x{x:02x}' for x in data)+'"'
code=['// Generated from ecCodes 2.50.0 / SciPy references, not from product output.\n']
for row in ref['fields']+[{**v,'file':Path(v['repacked']).name,'kind':'real-derived'} for v in real if 'error' not in v]:
    name=row['file']; data=(R/'fixtures'/name).read_bytes(); vals=row['values']
    mask=row.get('mask') or [1]*len(vals)
    ni=row['metadata']['Ni']; nj=row['metadata']['Nj']
    scan=row.get('scan',0)
    # Independent NumPy array transformations of source indices (WMO table3.4).
    if 'scan' in row:
        if scan&32:
            a=np.arange(len(vals)).reshape(ni,nj)
            if scan&16:a[1::2]=a[1::2,::-1]
            a=a.T
        else:
            a=np.arange(len(vals)).reshape(nj,ni)
            if scan&16:a[1::2]=a[1::2,::-1]
        if scan&128:a=a[:,::-1]
        if scan&64:a=a[::-1]
        order=a.ravel().tolist()
        lats=[90-r*90. for r in range(nj) for c in range(ni)]
        lons=[c*90. for r in range(nj) for c in range(ni)]
    else:
        order=sorted(range(len(vals)),key=lambda k:(-row['latitudes'][k],row['longitudes'][k]))
        lats=[row['latitudes'][k] for k in order]; lons=[row['longitudes'][k] for k in order]
    expected=[vals[k] if mask[k] else 0. for k in order]
    valid=[bool(mask[k]) for k in order]
    metadata_checks=''
    for key,field in [('discipline','discipline'),('parameterCategory','category'),('parameterNumber','parameter'),('indicatorOfUnitOfTimeRange','time_unit')]:
        if key in row['metadata']:metadata_checks+=f"  assert_eq(f.product().{field},{row['metadata'][key]})\n"
    if 'forecastTime' in row['metadata']:metadata_checks+=f"  assert_eq(f.product().forecast_time,Some({row['metadata']['forecastTime']}))\n"
    code.append(f'''///|
test "oracle {name}" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
{metadata_checks}
  assert_eq(f.rows(),{nj})
  assert_eq(f.cols(),{ni})
  let expected : Array[Double]={mb(expected)}
  let valid={mb(valid)}
  let source={mb(order)}
  let latitudes : Array[Double]={mb(lats)}
  let longitudes : Array[Double]={mb(lons)}
  let mut max_abs=0.0
  for r in 0..<{nj} {{for c in 0..<{ni} {{
    let i=r*{ni}+c
    let p=f.point(r,c).unwrap()
    assert_eq(p.source_index,source[i])
    assert_true((p.latitude-latitudes[i]).abs()<0.000002)
    assert_true((p.longitude-longitudes[i]).abs()<0.000002)
    assert_eq(f.mask()[i],valid[i])
    if valid[i] {{
      let error=(f.get(r,c).unwrap()-expected[i]).abs()
      if error>max_abs {{max_abs=error}}
      assert_true(error <= 1.0e-10+expected[i].abs()*1.0e-12)
    }}
    else {{assert_eq(f.get(r,c),None); assert_true(f.values()[i].is_nan())}}
  }}}}
  println("GRIB_METRIC|{name}|"+max_abs.to_string())
}}
''')
    if row['kind']=='real-derived':
        y=np.array(lats).reshape(nj,ni)[:,0]
        x=np.array(lons).reshape(nj,ni)[0,:]
        a=np.array(expected).reshape(nj,ni)
        queries=[[float(y[1]*.25+y[2]*.75),float(x[1]*.5+x[2]*.5)], [float(y[3]),float(x[3])]]
        expected_samples=RegularGridInterpolator((y[::-1],x),a[::-1])(queries).tolist()
        code.append(f'''///|
test "real field to SciPy station chain {name}" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let queries : Array[(Double,Double)]={str([tuple(v) for v in queries]).replace(' ','')}
  let expected : Array[Double]={mb(expected_samples)}
  for i,(lat,lon) in queries {{assert_true((f.interpolate_latlon(lat,lon).unwrap()-expected[i]).abs()<1.0e-9)}}
}}
''')
    if name=='scipy.grib2':
        scipy_data=data
    if name=='bitmap.grib2':bitmap_data=data
    if name=='polar.grib2':polar_data=data
q=ref['interpolation']
code.append(f'''///|
test "independent SciPy periodic scalar samples and provenance" {{
  let f=@grib2.read_message({blob(scipy_data)}).unwrap()
  let queries : Array[(Double,Double)]={str([tuple(v) for v in q['queries']]).replace(' ', '')}
  let expected : Array[Double]={mb(q['values'])}
  for i,(lat,lon) in queries {{
    let s=f.sample({{id:"station",latitude:lat,longitude:lon}})
    assert_true((s.value.unwrap()-expected[i]).abs()<1.0e-10)
    let mut weight=0.0
    let mut sum=0.0
    for c in s.contributors {{weight+=c.weight;sum+=c.weight*c.value}}
    assert_true((weight-1.0).abs()<1.0e-12)
    assert_true((sum-s.value.unwrap()).abs()<1.0e-12)
  }}
  assert_eq(f.interpolate_latlon(1.0,-45.0),f.interpolate_latlon(1.0,315.0))
  let a=f.interpolate_latlon(1.0,359.999999).unwrap()
  let b=f.interpolate_latlon(1.0,-0.000001).unwrap()
  assert_true((a-b).abs()<1.0e-12)
  let selected=@grib2.select_fields([f],0,0,0)
  assert_eq(selected.length(),1)
  let points=f.crop({{south:0.0,north:2.0,west:270.0,east:0.0}}).unwrap()
  assert_eq(points.length(),6)
  assert_eq(f.crop({{south:2.0,north:0.0,west:0.0,east:0.0}}) is Err(_),true)
}}
///|
test "bitmap, exact nodes, regional bounds and JSON null" {{
  let f=@grib2.read_message({blob(bitmap_data)}).unwrap()
  assert_eq(f.interpolate_latlon(1.0,10.0),Some(1.0))
  assert_eq(f.interpolate_latlon(1.0,10.5),None)
  assert_eq(f.interpolate_latlon(1.0,12.0),Some(9999.0))
  assert_eq(f.interpolate_latlon(1.5,10.0),None)
  assert_eq(f.interpolate_latlon(0.0,9.0),None)
  assert_eq(f.interpolate_latlon(0.0,13.0),None)
  let samples=f.sample_stations([{{id:"missing",latitude:1.0,longitude:11.0}},{{id:"valid",latitude:0.0,longitude:11.0}}])
  assert_eq(samples[0].value,None)
  assert_eq(samples[1].value,Some(5.0))
  assert_true(samples[0].to_json() is {{ "value": Null, .. }})
  match samples[1].to_json() {{
    {{"value":Number(v,..),..}}=>assert_eq(v,5.0)
    _=>fail("expected numeric JSON value")
  }}
}}
///|
test "polar scalar regularisation is continuous and raw data unchanged" {{
  let f=@grib2.read_message({blob(polar_data)}).unwrap()
  assert_eq(f.get(0,0),Some(0.0))
  for lon in [0.0,90.0,270.0,360.0] {{assert_eq(f.interpolate_latlon(90.0,lon),Some(3.0))}}
  assert_true((f.interpolate_latlon(89.9999999,0.0).unwrap()-3.0).abs()<1.0e-6)
  assert_eq(f.interpolate_latlon(-90.0,180.0),Some(23.0))
}}
''')
(P/'oracle_test.mbt').write_text('\n'.join(code))
# Small reproducible binary input and a real-data-derived example.
(P/'testdata').mkdir(exist_ok=True)
for row in ref['fields']:shutil.copyfile(R/'fixtures'/row['file'],P/'testdata'/row['file'])
for row in real:
    if 'error' not in row:shutil.copyfile(row['repacked'],P/'testdata'/Path(row['repacked']).name)
(P/'cmd/main/main.mbt').write_text(f'''///|
fn main {{
  let field=@grib2.read_message({blob(bitmap_data)}).unwrap()
  let results=field.sample_stations([{{id:"coastal-gap",latitude:1.0,longitude:10.5}},{{id:"inland",latitude:0.0,longitude:10.5}}])
  println(results.to_json().stringify(indent=2))
}}
''')
(P/'cmd/main/moon.pkg').write_text('import { "toneklinkenberg824-spec/grib2" @grib2, }\noptions("is-main": true)\n')
print('Emitted',len(ref['fields'])+sum('error' not in v for v in real),'field references and independent sampling tests')
