from pathlib import Path
import json,hashlib
R=Path(__file__).parent;P=Path(__file__).resolve().parents[3]
def blob(b):return 'b"'+''.join(f'\\x{x:02x}' for x in b)+'"'
def mb(s):return json.dumps(s,ensure_ascii=False)
data=(P/'testdata/forecast09/forecast-states.grib2').read_bytes()
key=' 未指定,"时效"\r\n组😀 ';station='站点,"A"\r\n第二行😀'
code=f'''fn stream11_groups() -> Array[@grib2.FieldSamples] {{
  let fields=@grib2.read_fields({blob(data)}).unwrap()
  let q=@grib2.FieldQuery::new(0,0,0,time_unit=1)
  @grib2.sample_requested_fields(fields,[{{key:{mb(key)},query:q.with_forecast_time_filter(MissingTime)}},{{key:"分析0",query:q.with_forecast_time_filter(ExactTime(0))}}],[{{id:{mb(station)},latitude:1.0,longitude:10.0}},{{id:"inland",latitude:0.0,longitude:10.5}}]).unwrap()
}}
///|
test "stream11 complete multiline records equal full CSV" {{
  let groups=stream11_groups();let before=groups.to_json().stringify()
  let chunks : Array[String]=[];let out=StringBuilder()
  for chunk in @grib2.station_csv_records(groups) {{chunks.push(chunk);out.write_string(chunk)}}
  assert_eq(chunks.length(),5)
  assert_eq(out.to_string(),@grib2.station_results_csv(groups))
  assert_eq(groups.to_json().stringify(),before)
  println("STREAM11|chunks|"+chunks.to_json().stringify())
}}
///|
test "stream11 separately created iterators are independent and fused" {{
  let groups=stream11_groups()
  let a=@grib2.station_csv_records(groups);let b=@grib2.station_csv_records(groups)
  let header=a.next();assert_eq(b.next(),header)
  let first=a.next();let second=a.next()
  assert_eq(b.next(),first);assert_eq(b.next(),second)
  let rest_a : Array[String]=[];let rest_b : Array[String]=[]
  for chunk in a {{rest_a.push(chunk)}}
  for chunk in b {{rest_b.push(chunk)}}
  assert_eq(rest_a.length(),2);assert_eq(rest_a,rest_b)
  assert_eq(a.next(),None);assert_eq(a.next(),None);assert_eq(b.next(),None)
}}
///|
test "stream11 skips empty groups and always has one header" {{
  let g=stream11_groups()
  let empty : @grib2.FieldSamples={{..g[0],samples:[]}}
  let mixed=[empty,g[0],empty,g[1],empty]
  let out=StringBuilder()
  for chunk in @grib2.station_csv_records(mixed) {{out.write_string(chunk)}}
  assert_eq(out.to_string(),@grib2.station_results_csv(g))
  for groups in [[],[empty,empty]] {{
    let stream=@grib2.station_csv_records(groups)
    assert_eq(stream.next(),Some(@grib2.station_results_csv([])))
    assert_eq(stream.next(),None);assert_eq(stream.next(),None)
  }}
}}
///|
test "stream11 prefix and10000 station traversal without full CSV buffer" {{
  let fields=@grib2.read_fields({blob(data)}).unwrap()
  let stations : Array[@grib2.Station]=Array::make(10000,{{id:"bulk",latitude:0.0,longitude:10.5}})
  let groups=@grib2.sample_requested_fields(fields,[{{key:"bulk",query:@grib2.FieldQuery::new(0,0,0,time_unit=1).with_forecast_time_filter(MissingTime)}}],stations).unwrap()
  let stream=@grib2.station_csv_records(groups)
  let header=stream.next().unwrap();let first=stream.next().unwrap()
  println("STREAM11|prefix|"+[header,first].to_json().stringify())
  let mut count=2;let mut total=header.length()+first.length();let mut maximum=first.length()
  for chunk in stream {{count+=1;total+=chunk.length();if chunk.length()>maximum {{maximum=chunk.length()}}}}
  assert_eq(count,10001)
  assert_eq(total,header.length()+10000*first.length())
  assert_eq(maximum,first.length());assert_eq(stream.next(),None)
  let stats : Json={{"records":count.to_json(),"serialized_units":total.to_json(),"maximum_record_units":maximum.to_json(),"prefix_records":(2).to_json()}}
  println("STREAM11|stats|"+stats.stringify())
}}
'''
(P/'stream11_test.mbt').write_text(code,encoding='utf-8')
source=(P/'cmd/export/main.mbt').read_text(encoding='utf-8')
start=source.rindex('  let text = @grib2.station_results_csv(groups)')
main=source[:start]+'''  for chunk in @grib2.station_csv_records(groups) {
    // Each record endsCRLF; println supplies its finalLF.
    println(chunk[:chunk.length()-1])
  }
}
'''
E=P/'cmd/stream';E.mkdir(exist_ok=True)
(E/'main.mbt').write_text(main,encoding='utf-8');(E/'moon.pkg').write_bytes((P/'cmd/export/moon.pkg').read_bytes())
baseline=P/'testdata/export10/NOAA-IFS-stations.csv'
ref={'synthetic':{'key':key,'station':station,'values':[None,111,222,222],'data_records':4,'total_records':5},'bulk':{'stations':10000,'records_including_header':10001,'prefix_records':2,'value':111,'claim':'Counts/string units only; no latency or RSS measurement'},'real_baseline':{'file':'testdata/export10/NOAA-IFS-stations.csv','sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'rows':8},'source_data_sha256':hashlib.sha256(data).hexdigest(),'record_semantics':'Header then one complete logical CSV record, even when quoted labels contain newlines'}
(R/'REFERENCE.json').write_text(json.dumps(ref,ensure_ascii=False,indent=2),encoding='utf-8')
print('Generated4 streaming contract cases + cmd/stream using the existing NOAA/IFS example inputs')
