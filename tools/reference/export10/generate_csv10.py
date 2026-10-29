from pathlib import Path
import json,struct,hashlib,ast,re,csv,io
R=Path(__file__).parent;P=Path(__file__).resolve().parents[3]
def blob(b):return 'b"'+''.join(f'\\x{x:02x}' for x in b)+'"'
def mb(s):return json.dumps(s,ensure_ascii=False)
header=['request_key','station_id','latitude','longitude','value','algorithm','message','field','byte_offset','product_json','contributors_json']
s=io.StringIO(newline='');csv.writer(s,quoting=csv.QUOTE_ALL,lineterminator='\r\n').writerow(header);head=s.getvalue()
forecast=(P/'testdata/forecast09/forecast-states.grib2').read_bytes()
tiny=(P/'testdata/sampling08/minimum.grib2').read_bytes()
base=(P/'testdata/constant.grib2').read_bytes()
def constant(value,d=0):
    b=bytearray(base);i=16
    while i<len(b)-4:
        n=int.from_bytes(b[i:i+4],'big')
        if b[i+4]==5:b[i+11:i+15]=struct.pack('>f',value);b[i+15:i+17]=b'\0\0';b[i+17:i+19]=d.to_bytes(2,'big')
        i+=n
    return bytes(b)
zero=constant(0.);negative=constant(-5.,324)
key=' 未指定,"时效"\r\n组😀 ';station='站点,"A"\r\n第二行😀'
tests=[f'''///|
test "csv10 selected forecast rows preserve labels and missing semantics" {{
  let fs=@grib2.read_fields({blob(forecast)}).unwrap()
  let q=@grib2.FieldQuery::new(0,0,0,time_unit=1)
  let requests : Array[@grib2.FieldRequest]=[
    {{key:{mb(key)},query:q.with_forecast_time_filter(MissingTime)}},
    {{key:"分析0",query:q.with_forecast_time_filter(ExactTime(0))}},
  ]
  let stations : Array[@grib2.Station]=[
    {{id:{mb(station)},latitude:1.0,longitude:10.0}},
    {{id:"",latitude:0.0,longitude:10.5}},
    {{id:"outside",latitude:2.0,longitude:10.0}},
  ]
  let groups=@grib2.sample_requested_fields(fs,requests,stations).unwrap()
  let before=groups.to_json().stringify()
  let text=@grib2.station_results_csv(groups)
  assert_eq(groups.to_json().stringify(),before)
  println("CSV10|forecast|"+text.to_json().stringify())
}}
''',f'''///|
test "csv10 zero and signed subnormal values remain numeric" {{
  let zero=@grib2.read_message({blob(zero)}).unwrap()
  let tiny=@grib2.read_message({blob(tiny)}).unwrap()
  let negative=@grib2.read_message({blob(negative)}).unwrap()
  let groups : Array[@grib2.FieldSamples]=[
    {{key:"zero",origin:zero.origin(),product:zero.product(),samples:zero.sample_stations([{{id:"n",latitude:0.5,longitude:10.5}}])}},
    {{key:"tiny",origin:tiny.origin(),product:tiny.product(),samples:tiny.sample_stations([{{id:"n",latitude:0.5,longitude:10.5}}])}},
    {{key:"negative",origin:negative.origin(),product:negative.product(),samples:negative.sample_stations([{{id:"n",latitude:0.5,longitude:10.5}}])}},
  ]
  assert_eq(groups[0].samples[0].value,Some(0.0))
  assert_eq(groups[1].samples[0].value.unwrap().reinterpret_as_uint64(),1UL)
  assert_eq(groups[2].samples[0].value.unwrap().reinterpret_as_uint64(),9223372036854775809UL)
  println("CSV10|numeric|"+@grib2.station_results_csv(groups).to_json().stringify())
}}
''',f'''///|
test "csv10 empty sample dimensions give exactly a header" {{
  let fs=@grib2.read_fields({blob(forecast)}).unwrap()
  let groups=@grib2.sample_requested_fields(fs,[{{key:"known",query:@grib2.FieldQuery::new(0,0,0,forecast_time=0)}}],[]).unwrap()
  let expected={mb(head)}
  assert_eq(@grib2.station_results_csv([]),expected)
  assert_eq(@grib2.station_results_csv(groups),expected)
  assert_eq(groups[0].origin.message,1)
  println("CSV10|empty|"+expected.to_json().stringify())
}}
''']
(P/'csv10_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
oracle=(P/'oracle_test.mbt').read_text(encoding='utf-8');gold=[];fixtures=[]
sources=json.loads((P/'testdata/SOURCES.json').read_text(encoding='utf-8'))
for name in ['noaa-gfs-repacked.grib2','ecmwf-ifs-repacked.grib2']:
    b=(P/'testdata'/name).read_bytes();fixtures.append(b)
    block=next(s for s in oracle.split('///|') if 'real field to SciPy station chain '+name in s)
    queries=ast.literal_eval(re.search(r'let queries[^\n]*=\s*(\[[^\n]+\])',block).group(1))
    values=ast.literal_eval(re.search(r'let expected[^\n]*=\s*(\[[^\n]+\])',block).group(1))
    source=next(s for s in sources if s['repacked_file']==name)
    assert hashlib.sha256(b).hexdigest()==source['repacked_sha256']
    gold.append({'file':name,'sha256':source['repacked_sha256'],'queries':queries,'values':values,'source':source['source'],'license':source['license']})
stations=[]
for provider,g in zip(['GFS','IFS'],gold):
    stations.extend(f'{{id:"{provider}{i}",latitude:{lat},longitude:{lon}}}' for i,(lat,lon) in enumerate(g['queries']))
E=P/'cmd/export';E.mkdir(exist_ok=True)
(E/'moon.pkg').write_text('import {\n  "toneklinkenberg824-spec/grib2" @grib2,\n}\n\noptions("is-main": true)\n',encoding='utf-8')
main=f'''///|
fn export_query(p : @grib2.Product) -> @grib2.FieldQuery {{
  let criterion : @grib2.ForecastTimeFilter=match p.forecast_time {{
    None=>MissingTime
    Some(t)=>ExactTime(t)
  }}
  @grib2.FieldQuery::new(p.discipline,p.category,p.parameter,centre=p.centre,subcentre=p.subcentre,master_table=p.master_table,local_table=p.local_table,time_unit=p.time_unit,reference_time=p.reference_time,first_surface=p.first_surface,second_surface=p.second_surface).with_forecast_time_filter(criterion)
}}
///|
// Existing licensed8x6 repacked5.0 NOAA/IFS fixtures; see testdata/SOURCES.json.
fn main {{
  let fields=@grib2.read_fields({blob(b''.join(fixtures))}).unwrap()
  let requests : Array[@grib2.FieldRequest]=[
    {{key:"NOAA GFS",query:export_query(fields[0].product())}},
    {{key:"ECMWF IFS",query:export_query(fields[1].product())}},
  ]
  let stations : Array[@grib2.Station]=[{','.join(stations)}]
  let groups=@grib2.sample_requested_fields(fields,requests,stations).unwrap()
  let text=@grib2.station_results_csv(groups)
  // println suppliesLF; retain the finalCR so stdout has exactly one finalCRLF.
  println(text[:text.length()-1])
}}
'''
(E/'main.mbt').write_text(main,encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps({'header':header,'quoting':'RFC4180 quoted cells/doubled quotes/CRLF; UTF-8','synthetic':{'key':key,'station':station,'values':[None,111,None,222,222,None],'numeric_bits':[0,1,9223372036854775809]},'real':gold,'real_row_values':gold[0]['values']+[None,None,None,None]+gold[1]['values'],'golden_source':{'file':'oracle_test.mbt','sha256':hashlib.sha256(oracle.encode()).hexdigest(),'basis':'Previously captured independent SciPy expectations, not a new download/scientific reference run'},'example_rows':8,'metadata':'Existing per-Sample Product JSON and contributor schema retained'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Generated',len(tests),'CSV contract tests and8-row NOAA/IFS cmd/export example')
