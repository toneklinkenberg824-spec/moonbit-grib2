from pathlib import Path
import struct,json,hashlib,sys
R=Path(__file__).parent;P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
def parts(b):
    ss={};i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big');ss[b[i+4]]=bytearray(b[i:i+n]);i+=n
    return ss
def u(b,i,x,n=4):b[i:i+n]=int(x).to_bytes(n,'big')
def blob(b):return 'b"'+''.join(f'\\x{x:02x}' for x in b)+'"'
def field(value,kind=100,scale=0,level=85000,hour=12,lead=6,centre=98,subcentre=0,master=4,local=0,second=False,gap=False):
    ss=parts(base);s=ss[1];p=ss[4];d=ss[5]
    u(s,5,centre,2);u(s,7,subcentre,2);s[9]=master;s[10]=local;s[16]=hour
    p[9]=0;p[10]=0;p[17]=1;u(p,18,lead);p[22]=kind;p[23]=scale;u(p,24,level)
    p[28]=100 if second else 255;p[29]=0 if second else 255;u(p,30,70000 if second else 0xffffffff)
    u(d,5,5 if gap else 6);d[11:15]=struct.pack('>f',value);d[15:19]=b'\0'*4;d[19]=0
    ss[6]=bytearray(b'\0\0\0\7\6\0\x7c') if gap else bytearray(b'\0\0\0\6\6\xff')
    ss[7]=bytearray(b'\0\0\0\5\7')
    body=b''.join(ss[k] for k in [1,3,4,5,6,7])+b'7777';return base[:8]+(16+len(body)).to_bytes(8,'big')+body
specs=[('t2m',280,dict(kind=103,level=2)),('t850',270,dict(gap=True)),('t1000',260,dict(level=100000)),('old_run',265,dict(hour=6)),('later_lead',275,dict(lead=12)),('scaled_level',271,dict(scale=1,level=850000)),('other_centre',272,dict(centre=7)),('bounded_layer',269,dict(second=True)),('other_subcentre',273,dict(subcentre=1)),('other_master',274,dict(master=5)),('other_local',276,dict(local=1))]
fixtures=[field(v,**kw) for _,v,kw in specs];data=b''.join(fixtures)
surface=lambda kind=100,scale=0,val=85000:f'{{kind:{kind},scale:Some({scale}),scaled_value:Some({val}U)}}'
empty='{kind:255,scale:None,scaled_value:None}'
def query(**changes):
    kw=dict(centre='98',subcentre='0',master_table='4',local_table='0',time_unit='1',forecast_time='6',reference_time='[2007,3,23,12,0,0]',first_surface=surface(),second_surface=empty)
    kw.update(changes)
    return '@grib2.FieldQuery::new(0,0,0,'+','.join(f'{k}={v}' for k,v in kw.items())+')'
q2=query(first_surface=surface(103,0,2));q850=query()
tests=[f'''fn requests08_fields() -> Array[@grib2.GriddedField] {{@grib2.read_fields({blob(data)}).unwrap()}}
///|
test "requests08 exact layer and run selection" {{
  let fs=requests08_fields()
  let a=@grib2.select_unique_field(fs,{q2}).unwrap()
  let b=@grib2.select_unique_field(fs,{q850}).unwrap()
  assert_eq(a.origin().message,0);assert_eq(a.get(1,0),Some(280.0))
  assert_eq(b.origin().message,1);assert_eq(b.get(1,0),Some(270.0))
  assert_eq(@grib2.select_fields(fs,0,0,0,time_unit=1,forecast_time=6).length(),10)
  assert_true(@grib2.select_unique_field(fs,@grib2.FieldQuery::new(0,0,0)) is Err(InvalidRequest(_)))
}}
''']
queries=[query(centre='7'),query(subcentre='1'),query(master_table='5'),query(local_table='1'),query(second_surface=surface(100,0,70000)),query(reference_time='[2007,3,23,6,0,0]'),query(forecast_time='12'),query(first_surface=surface(100,1,850000))]
tests.append(f'''///|
test "requests08 metadata dimensions and raw surface identity" {{
  let fs=requests08_fields()
  let queries=[{','.join(queries)}]
  let indices=[6,8,9,10,7,3,4,5]
  let values=[272.0,273.0,274.0,276.0,269.0,265.0,275.0,271.0]
  for i,q in queries {{let f=@grib2.select_unique_field(fs,q).unwrap();assert_eq(f.origin().message,indices[i]);assert_eq(f.get(1,0),Some(values[i]))}}
}}
''')
tests.append(f'''///|
test "requests08 absent and duplicate records fail explicitly" {{
  let fs=requests08_fields()
  for q in [{query(time_unit='2')},{query(forecast_time='99')},{query(reference_time='[2008,3,23,12,0,0]')}] {{assert_true(@grib2.select_unique_field(fs,q) is Err(InvalidRequest(_)))}}
  assert_true(@grib2.select_unique_field([],{q850}) is Err(InvalidRequest(_)))
  let duplicate=@grib2.read_fields({blob(fixtures[1]+fixtures[1])}).unwrap()
  assert_true(@grib2.select_unique_field(duplicate,{q850}) is Err(InvalidRequest(_)))
}}
''')
req=f'[{{key:"t850",query:{q850}}},{{key:"t2m",query:{q2}}}]'
stations='[{id:"gap",latitude:1.0,longitude:10.0},{id:"inland",latitude:0.0,longitude:10.5},{id:"outside",latitude:2.0,longitude:10.0}]'
tests.append(f'''///|
test "requests08 named batch preserves order missing and provenance" {{
  let out=@grib2.sample_requested_fields(requests08_fields(),{req},{stations}).unwrap()
  assert_eq(out[0].key,"t850");assert_eq(out[1].key,"t2m")
  assert_eq(out[0].origin.message,1)
  assert_eq(out[0].samples[0].value,None)
  assert_eq(out[0].samples[1].value,Some(270.0))
  assert_eq(out[0].samples[2].value,None)
  assert_eq(out[1].samples[0].value,Some(280.0))
  let c=out[0].samples[1].contributors
  assert_eq(c.length(),2);assert_eq(c[0].source_index,3);assert_eq(c[1].source_index,4)
  assert_eq(c[0].weight,0.5);assert_eq(c[1].weight,0.5)
  assert_eq(out[0].samples[0].contributors.length(),0)
}}
''')
tests.append(f'''///|
test "requests08 batch selection is all or error" {{
  let fs=requests08_fields()
  for bad in [@grib2.FieldQuery::new(0,0,0),{query(forecast_time='99')}] {{
    assert_true(@grib2.sample_requested_fields(fs,[{{key:"ok",query:{q2}}},{{key:"bad",query:bad}}],{stations}) is Err(InvalidRequest(_)))
  }}
  assert_true(@grib2.sample_requested_fields(fs,[{{key:"same",query:{q2}}},{{key:"same",query:{q850}}}],[]) is Err(InvalidRequest(_)))
  assert_true(@grib2.sample_requested_fields(fs,[{{key:"",query:{q2}}}],[]) is Err(InvalidRequest(_)))
}}
''')
tests.append(f'''///|
test "requests08 query and result metadata are detached" {{
  let fs=requests08_fields()
  let time=[2007,3,23,12,0,0]
  let q={query(reference_time='time')}
  time[0]=0
  assert_eq(@grib2.select_unique_field(fs,q).unwrap().origin().message,1)
  assert_true(@grib2.select_unique_field(fs,{query(reference_time='[2007]')}) is Err(InvalidRequest(_)))
  let out=@grib2.sample_requested_fields(fs,{req},{stations}).unwrap()
  out[0].product.reference_time[0]=0
  out[0].samples[1].product.reference_time[0]=1
  assert_eq(fs[1].product().reference_time[0],2007)
  assert_eq(out[1].product.reference_time[0],2007)
}}
''')
tests.append(f'''///|
test "requests08 empty dimensions and named aliases" {{
  assert_eq(@grib2.sample_requested_fields([],[],[]).unwrap().length(),0)
  let out=@grib2.sample_requested_fields(requests08_fields(),{req},[]).unwrap()
  assert_eq(out.length(),2);assert_eq(out[0].samples.length(),0);assert_eq(out[0].origin.message,1)
  let named_aliases=@grib2.sample_requested_fields(requests08_fields(),[{{key:"a",query:{q2}}},{{key:"b",query:{q2}}}],{stations}).unwrap()
  assert_eq(named_aliases[0].samples[0].value,named_aliases[1].samples[0].value)
}}
''')
(P/'requests08_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
E=P/'cmd/layers';E.mkdir(exist_ok=True)
(E/'moon.pkg').write_text('import {\n  "toneklinkenberg824-spec/grib2" @grib2,\n}\n\noptions("is-main": true)\n',encoding='utf-8')
main=f'''///|
// Synthetic layer/run inputs: illustrative constants, not an operational forecast.
fn main {{
  let fields=@grib2.read_fields({blob(fixtures[0]+fixtures[1]+fixtures[2])}).unwrap()
  let requests : Array[@grib2.FieldRequest]=[
    {{key:"temperature_2m",query:{q2}}},
    {{key:"temperature_850hPa",query:{q850}}},
  ]
  let stations : Array[@grib2.Station]=[
    {{id:"coastal-gap",latitude:1.0,longitude:10.0}},
    {{id:"inland",latitude:0.0,longitude:10.5}},
  ]
  let results=@grib2.sample_requested_fields(fields,requests,stations).unwrap()
  println(results.to_json().stringify(indent=2))
}}
'''
(E/'main.mbt').write_text(main,encoding='utf-8')
records=[]
for (name,value,kw),b in zip(specs,fixtures):records.append({'name':name,'value':value,'metadata_overrides':kw,'sha256':hashlib.sha256(b).hexdigest()})
observations=[]
if '--eccodes' in sys.argv:
    import eccodes as ec
    for (_,value,kw),b in zip(specs,fixtures):
        h=ec.codes_new_from_message(b)
        valid=ec.codes_get_values(h).tolist();mask=ec.codes_get_array(h,'bitmap').tolist() if ec.codes_get(h,'bitmapPresent') else [1]*6
        assert all(v==value for v,m in zip(valid,mask) if m)
        assert ec.codes_get(h,'typeOfFirstFixedSurface',int)==kw.get('kind',100)
        assert ec.codes_get(h,'scaledValueOfFirstFixedSurface')==kw.get('level',85000)
        observations.append({'reference_time_hour':ec.codes_get(h,'hour'),'forecast_time':ec.codes_get(h,'forecastTime'),'surface_kind':ec.codes_get(h,'typeOfFirstFixedSurface',int),'surface_scale':ec.codes_get(h,'scaleFactorOfFirstFixedSurface'),'surface_value':ec.codes_get(h,'scaledValueOfFirstFixedSurface'),'mask':mask,'valid_constant':value})
        ec.codes_release(h)
    print('ecCodes',ec.codes_get_api_version(),'independently verified',len(fixtures),'new layer/run fixtures')
(R/'REQUESTS-REFERENCE.json').write_text(json.dumps({'fixtures':records,'oracle':'Manually encoded metadata tuple and constant values; ecCodes decode/metadata observations captured separately','eccodes':observations,'demo_expected':{'keys':['temperature_2m','temperature_850hPa'],'values':[[280,280],[None,270]],'inland_850_sources':[3,4],'inland_850_weights':[.5,.5]}},indent=2),encoding='utf-8')
(R/'requests-fixture.grib2').write_bytes(data)
print('Generated',len(tests),'request workflow tests + cmd/layers example')
