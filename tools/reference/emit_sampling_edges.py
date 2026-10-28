from pathlib import Path
import eccodes as ec
R=Path(__file__).parent; P=Path(__file__).resolve().parents[2]
def blob(d):return 'b"'+''.join(f'\\x{x:02x}' for x in d)+'"'
def make(ni,nj,lat1,lat2,lon2,dy,vals):
    h=ec.codes_grib_new_from_samples('regular_ll_sfc_grib2')
    for k,v in {'Ni':ni,'Nj':nj,'latitudeOfFirstGridPointInDegrees':lat1,'latitudeOfLastGridPointInDegrees':lat2,'longitudeOfFirstGridPointInDegrees':0,'longitudeOfLastGridPointInDegrees':lon2,'iDirectionIncrementInDegrees':90,'jDirectionIncrementInDegrees':dy,'scanningMode':0,'packingType':'grid_simple','bitsPerValue':17}.items():ec.codes_set(h,k,v)
    if any(v is None for v in vals):
        ec.codes_set(h,'bitmapPresent',1);ec.codes_set(h,'missingValue',1e30)
    ec.codes_set_values(h,[1e30 if v is None else v for v in vals])
    data=ec.codes_get_message(h);ec.codes_release(h);return data
dup=make(5,2,1,0,360,1,[1,2,3,4,1,11,12,13,14,11])
bad=make(5,2,1,0,360,1,[1,2,3,4,99,11,12,13,14,11])
pole=make(4,3,90,-90,270,90,[None,2,4,6,10,12,14,16,None,None,None,None])
wind=bytearray((R/'fixtures/polar.grib2').read_bytes()); i=16
while wind[i+4]!=4:i+=int.from_bytes(wind[i:i+4],'big')
wind[i+9]=2;wind[i+10]=2
code=f'''///|
test "duplicate longitude endpoint is checked and counted once" {{
  let f=@grib2.read_message({blob(dup)}).unwrap()
  assert_eq(f.cols(),5)
  assert_eq(f.is_global(),true)
  assert_eq(f.interpolate_latlon(1.0,315.0),Some(2.5))
  assert_eq(f.crop({{south:0.0,north:1.0,west:0.0,east:360.0}}).unwrap().length(),8)
  assert_true(@grib2.read_message({blob(bad)}) is Err(InvalidGrid(_)))
}}
///|
test "polar masks, vector exclusion, invalid requests and resource limit" {{
  let f=@grib2.read_message({blob(pole)}).unwrap()
  assert_eq(f.interpolate_latlon(90.0,0.0),Some(4.0))
  assert_eq(f.interpolate_latlon(-90.0,0.0),None)
  assert_eq(f.interpolate_latlon(-45.0,0.0),None)
  assert_eq(f.interpolate_latlon(0.0,0.0),Some(10.0))
  assert_eq(f.interpolate_latlon(91.0,0.0),None)
  assert_eq(f.interpolate_latlon(0.0,0.0/0.0),None)
  let w=@grib2.read_message({blob(wind)}).unwrap()
  assert_eq(w.interpolate_latlon(90.0,0.0),None)
  assert_true(@grib2.read_message({blob(dup)},max_points=2) is Err(InvalidGrid(_)))
  assert_true(@grib2.read_message({blob(dup)},max_points=0) is Err(InvalidRequest(_)))
}}
'''
(P/'sampling_edges_test.mbt').write_text(code)
print('Emitted duplicate-seam, scalar/vector-pole, mask and resource-limit edge references')
