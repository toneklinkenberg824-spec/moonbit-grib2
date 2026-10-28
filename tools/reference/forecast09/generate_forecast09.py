from pathlib import Path
import struct,json,hashlib
R=Path(__file__).parent;P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
def parts(b):
    ss={};i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big');ss[b[i+4]]=bytearray(b[i:i+n]);i+=n
    return ss
def u(b,i,v,n=4):b[i:i+n]=v.to_bytes(n,'big')
def blob(b):return 'b"'+''.join(f'\\x{x:02x}' for x in b)+'"'
def make(raw,value,gap=False):
    ss=parts(base);p=ss[4];d=ss[5]
    p[9]=0;p[10]=0;p[17]=1;u(p,18,raw);p[22]=103;p[23]=0;u(p,24,2)
    p[28]=255;p[29]=255;u(p,30,0xffffffff)
    u(d,5,5 if gap else 6);d[11:15]=struct.pack('>f',value);d[15:19]=b'\0'*4;d[19]=0
    ss[6]=bytearray(b'\0\0\0\7\6\0\x7c') if gap else bytearray(b'\0\0\0\6\6\xff');ss[7]=bytearray(b'\0\0\0\5\7')
    body=b''.join(ss[i] for i in [1,3,4,5,6,7])+b'7777'
    return base[:8]+(16+len(body)).to_bytes(8,'big')+body
cases=[(0xffffffff,111,None,True),(0,222,0,False),(6,333,6,False),(0x80000006,444,-6,False)]
fixtures=[make(raw,value,gap) for raw,value,_,gap in cases];data=b''.join(fixtures)
q='@grib2.FieldQuery::new(0,0,0,time_unit=1,reference_time=[2007,3,23,12,0,0],first_surface={kind:103,scale:Some(0),scaled_value:Some(2U)},second_surface={kind:255,scale:None,scaled_value:None})'
old=f'''///|
test "forecast09 before existing wildcard cannot express missing only" {{
  let fs=@grib2.read_fields({blob(data)}).unwrap()
  assert_eq(fs[0].product().forecast_time,None)
  assert_eq(fs[1].product().forecast_time,Some(0))
  assert_true(@grib2.select_unique_field(fs,{q}) is Err(InvalidRequest(_)))
  let exact=@grib2.select_unique_field(fs,@grib2.FieldQuery::new(0,0,0,forecast_time=0)).unwrap()
  assert_eq(exact.origin().message,1)
  println("BEFORE_GAP: wildcard=ambiguous; exact0=message1; encoded-missing=message0 requires manual filter")
}}
'''
(P/'forecast09_before_test.mbt').write_text(old,encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps({'basis':'WMO92.1.4 all-one missing and92.1.5 sign-magnitude; no calendar conversion','cases':[{'raw_forecast':raw,'expected_forecast':lead,'value':value,'gap':gap,'sha256':hashlib.sha256(b).hexdigest(),'length':len(b)} for (raw,value,lead,gap),b in zip(cases,fixtures)],'sources':['https://codes.ecmwf.int/grib/format/grib2/regulations/'],'example_expected':{'keys':['未指定时效','分析0','预报6'],'values':[[None,111],[222,222],[333,333]],'messages':[0,1,2],'forecast_metadata':[None,0,6]}},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'forecast-fixture.grib2').write_bytes(data)
header=f'''fn forecast09_fields() -> Array[@grib2.GriddedField] {{@grib2.read_fields({blob(data)}).unwrap()}}
///|
fn forecast09_query() -> @grib2.FieldQuery {{{q}}}
'''
tests=[f'''///|
test "forecast09 distinguish missing zero positive negative and wildcard" {{
  let fs=forecast09_fields();let q=forecast09_query()
  assert_eq(q.forecast_time_filter(),AnyTime)
  assert_true(@grib2.select_unique_field(fs,q) is Err(InvalidRequest(_)))
  let filters : Array[@grib2.ForecastTimeFilter]=[MissingTime,ExactTime(0),ExactTime(6),ExactTime(-6)]
  let times=[None,Some(0),Some(6),Some(-6)]
  let values=[111.0,222.0,333.0,444.0]
  for i,filter in filters {{
    let refined=q.with_forecast_time_filter(filter)
    assert_eq(refined.forecast_time_filter(),filter)
    let f=@grib2.select_unique_field(fs,refined).unwrap()
    assert_eq(f.origin().message,i);assert_eq(f.product().forecast_time,times[i]);assert_eq(f.get(1,0),Some(values[i]))
  }}
}}
''',f'''///|
test "forecast09 immutable criterion transitions preserve other filters" {{
  let fs=forecast09_fields()
  let original=@grib2.FieldQuery::new(0,0,0,time_unit=1,forecast_time=6)
  let missing=original.with_forecast_time_filter(MissingTime)
  assert_eq(original.forecast_time,Some(6));assert_eq(original.forecast_time_filter(),ExactTime(6))
  assert_eq(missing.forecast_time,None);assert_eq(missing.forecast_time_filter(),MissingTime)
  assert_eq(@grib2.select_unique_field(fs,original).unwrap().origin().message,2)
  assert_eq(@grib2.select_unique_field(fs,missing).unwrap().origin().message,0)
  assert_eq(@grib2.select_unique_field(fs,missing.with_forecast_time_filter(ExactTime(0))).unwrap().origin().message,1)
  assert_true(@grib2.select_unique_field(fs,missing.with_forecast_time_filter(AnyTime)) is Err(InvalidRequest(_)))
  let wrong=@grib2.FieldQuery::new(0,0,0,time_unit=13).with_forecast_time_filter(MissingTime)
  assert_true(@grib2.select_unique_field(fs,wrong) is Err(InvalidRequest(_)))
  let wrong_layer=@grib2.FieldQuery::new(0,0,0,first_surface={{kind:100,scale:Some(0),scaled_value:Some(85000U)}}).with_forecast_time_filter(MissingTime)
  assert_true(@grib2.select_unique_field(fs,wrong_layer) is Err(InvalidRequest(_)))
}}
''']
unicode_key=json.dumps('未指定时效,"原始"\n组',ensure_ascii=False)
unicode_station=json.dumps('站点 A,"夜间"\n第二行',ensure_ascii=False)
tests.append(f'''///|
test "forecast09 named batch keeps raw missing metadata and Unicode labels" {{
  let fs=forecast09_fields();let q=forecast09_query()
  let requests : Array[@grib2.FieldRequest]=[{{key:{unicode_key},query:q.with_forecast_time_filter(MissingTime)}},{{key:"分析0",query:q.with_forecast_time_filter(ExactTime(0))}}]
  let stations : Array[@grib2.Station]=[{{id:{unicode_station},latitude:1.0,longitude:10.0}},{{id:"内陆",latitude:0.0,longitude:10.5}}]
  let out=@grib2.sample_requested_fields(fs,requests,stations).unwrap()
  assert_eq(out[0].key,{unicode_key});assert_eq(out[0].samples[0].station.id,{unicode_station})
  assert_eq(out[0].product.forecast_time,None);assert_eq(out[1].product.forecast_time,Some(0))
  assert_eq(out[0].origin.message,0);assert_eq(out[1].origin.byte_offset,{len(fixtures[0])})
  assert_eq(out[0].samples[0].value,None);assert_eq(out[0].samples[1].value,Some(111.0))
  assert_eq(out[1].samples[0].value,Some(222.0))
  assert_eq(out[0].samples[1].contributors[0].source_index,3)
  assert_eq(out[0].samples[1].contributors[1].source_index,4)
}}
''')
tests.append(f'''///|
test "forecast09 missing-only absent duplicate and ambiguous batch fail" {{
  let q=forecast09_query().with_forecast_time_filter(MissingTime)
  let absent=@grib2.read_fields({blob(fixtures[1]+fixtures[2])}).unwrap()
  assert_true(@grib2.select_unique_field(absent,q) is Err(InvalidRequest(_)))
  let duplicate=@grib2.read_fields({blob(fixtures[0]+fixtures[0])}).unwrap()
  assert_true(@grib2.select_unique_field(duplicate,q) is Err(InvalidRequest(_)))
  assert_true(@grib2.sample_requested_fields(forecast09_fields(),[{{key:"ok",query:q}},{{key:"ambiguous",query:q.with_forecast_time_filter(AnyTime)}}],[]) is Err(InvalidRequest(_)))
}}
''')
(P/'forecast09_test.mbt').write_text(header+'\n'.join(tests),encoding='utf-8')
E=P/'cmd/forecast';E.mkdir(exist_ok=True)
(E/'moon.pkg').write_text('import {\n  "zhou-wei97/grib2" @grib2,\n}\n\noptions("is-main": true)\n',encoding='utf-8')
(E/'main.mbt').write_text(f'''///|
// Synthetic forecast identity example, not an operational forecast.
fn main {{
  let fields=@grib2.read_fields({blob(data)}).unwrap()
  let base_query={q}
  let requests : Array[@grib2.FieldRequest]=[
    {{key:"未指定时效",query:base_query.with_forecast_time_filter(MissingTime)}},
    {{key:"分析0",query:base_query.with_forecast_time_filter(ExactTime(0))}},
    {{key:"预报6",query:base_query.with_forecast_time_filter(ExactTime(6))}},
  ]
  let stations : Array[@grib2.Station]=[
    {{id:"海岸",latitude:1.0,longitude:10.0}},
    {{id:"内陆",latitude:0.0,longitude:10.5}},
  ]
  let results=@grib2.sample_requested_fields(fields,requests,stations).unwrap()
  println(results.to_json().stringify(indent=2))
}}
''',encoding='utf-8')
print('Generated old-API gap control,',len(tests),'new forecast filter tests and cmd/forecast')
