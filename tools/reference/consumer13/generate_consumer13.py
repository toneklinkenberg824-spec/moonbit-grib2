from pathlib import Path
import json,hashlib,struct
P=Path(__file__).resolve().parents[3]
R=Path(__file__).parent
E=P/'examples/nyacsv13';E.mkdir(parents=True,exist_ok=True)
def mb_bytes(data):return 'b"'+''.join('\\x'+format(x,'02x') for x in data)+'"'
real=(P/'testdata/noaa-gfs-repacked.grib2').read_bytes()+(P/'testdata/ecmwf-ifs-repacked.grib2').read_bytes()
old=(P/'testdata/forecast09/forecast-states.grib2').read_bytes()
n=int.from_bytes(old[8:16],'big');m=int.from_bytes(old[n+8:n+16],'big');synthetic=bytearray(old[:n+m])
off=16
while synthetic[off+4]!=5:off+=int.from_bytes(synthetic[off:off+4],'big')
assert int.from_bytes(synthetic[off:off+4],'big')==21
assert synthetic[off+9:off+11]==b'\x00\x00' and synthetic[off+15:off+20]==b'\x00'*5
assert struct.unpack('>f',synthetic[off+11:off+15])[0]==111
synthetic[off+11:off+15]=struct.pack('>f',0)
(E/'synthetic-zero-analysis.grib2').write_bytes(synthetic)
query=(P/'cmd/direct/main.mbt').read_text(encoding='utf-8').split('///|\n// Existing',1)[0]
consume=r'''///|
/// Application boundary for complete records from this producer, not a general
/// fragmented/untrusted CSV reader. Keep only the header and current parsed row.
fn consume_records(
  case_name : String,
  records : Iter[String],
  maximum_rows? : Int,
) -> Unit raise {
  let options : @csv.CSVOptions = {
    delimiter: ',',
    allow_newlines_in_quotes: true,
    quote_char: '"',
    skip_empty_lines: true,
    trim_spaces: false,
  }
  let header = records.next().unwrap()
  let schema = @csv.CSV::parse_string(header, options=options)
  let expected_header = [
    "request_key", "station_id", "latitude", "longitude", "value", "algorithm",
    "message", "field", "byte_offset", "product_json", "contributors_json",
  ]
  assert_eq(schema.header(), expected_header)
  assert_eq(schema.data().length(), 0)
  let mut consumed = 0
  while true {
    if maximum_rows is Some(n) && consumed >= n { break }
    match records.next() {
      None => break
      Some(record) => {
        // A logical CSV record may contain quoted physical CR/LF.
        let csv = @csv.CSV::parse_string(header + record, options=options)
        assert_eq(csv.header(), expected_header)
        assert_eq(csv.shape(), (1, 11))
        let row = csv.data()[0]
        assert_eq(row.length(), 11)
        let value : Json = if row[4] == "" {
          Json::null()
        } else {
          @string.parse_double(row[4][:]).to_json()
        }
        let product = @json.parse(row[9][:])
        let contributors = @json.parse(row[10][:])
        let application_row : Json = {
          "kind": "row",
          "case": case_name.to_json(),
          "cells": row.to_json(),
          "value": value,
          "product": product,
          "contributors": contributors,
        }
        println(application_row.stringify())
        consumed += 1
      }
    }
  }
  let summary : Json = {
    "kind": "summary",
    "case": case_name.to_json(),
    "consumed_rows": consumed.to_json(),
  }
  println(summary.stringify())
}

///|
fn main raise {
  let real = @grib2.read_fields(REAL_BYTES).unwrap()
  let requests : Array[@grib2.FieldRequest] = [
    { key: " GFS,\"温度\"\r\n原报😀 ", query: export_query(real[0].product()) },
    { key: "IFS", query: export_query(real[1].product()) },
  ]
  let stations : Array[@grib2.Station] = [
    { id: " 0012,\"港\"\r\n换行😀 \t", latitude: 68.25, longitude: 31.5 },
    { id: "", latitude: 84.5625, longitude: 187.875 },
  ]
  consume_records(
    "real",
    @grib2.sample_requested_csv_records(real, requests, stations).unwrap(),
  )
  consume_records(
    "preview",
    @grib2.sample_requested_csv_records(real, requests, stations).unwrap(),
    maximum_rows=1,
  )
  let synthetic = @grib2.read_fields(SYNTHETIC_BYTES).unwrap()
  let numeric_requests : Array[@grib2.FieldRequest] = [
    { key: "missing-time", query: export_query(synthetic[0].product()) },
    { key: "analysis0", query: export_query(synthetic[1].product()) },
  ]
  let numeric_stations : Array[@grib2.Station] = [
    { id: "0007", latitude: 1.0, longitude: 10.0 },
    { id: " \t,\"港\"\r\n内陆😀 ", latitude: 0.0, longitude: 10.5 },
  ]
  consume_records(
    "numeric",
    @grib2.sample_requested_csv_records(synthetic, numeric_requests, numeric_stations).unwrap(),
  )
  consume_records(
    "empty",
    @grib2.sample_requested_csv_records([], [], []).unwrap(),
  )
}
'''
consume=consume.replace('REAL_BYTES',mb_bytes(real)).replace('SYNTHETIC_BYTES',mb_bytes(synthetic))
(E/'main.mbt').write_text(query+consume,encoding='utf-8')
(E/'moon.mod').write_text('name = "local/grib2-nyacsv13-consumer"\n\nimport {\n  "zhou-wei97/grib2@0.1.0",\n  "moonbit-community/NyaCSV@0.3.3",\n}\n',encoding='utf-8')
(E/'moon.pkg').write_text('import {\n  "zhou-wei97/grib2" @grib2,\n  "moonbit-community/NyaCSV" @csv,\n  "moonbitlang/core/json",\n  "moonbitlang/core/string",\n}\n\npkgtype(kind: "executable")\n',encoding='utf-8')
reference={
  'dependency':{'repository':'https://github.com/moonbit-community/NyaCSV','commit':'fe4448e1e45a25f6fca151320c766519e80162c9','declared_version':'0.3.3','binding':'Fixed-source moon.work, no registry install claim'},
  'real':{'keys':[' GFS,"温度"\r\n原报😀 ','IFS'],'station_ids':[' 0012,"港"\r\n换行😀 \t',''],'values':[253.6234765625,None,None,239.85598754882812],'centres':[7,7,98,98],'messages':[0,0,1,1],'byte_offsets':[0,0,len((P/'testdata/noaa-gfs-repacked.grib2').read_bytes()),len((P/'testdata/noaa-gfs-repacked.grib2').read_bytes())],'reference':'Two archived export10 SciPy values reused for consumer conversion, no new sampling acceptance/download run'},
  'numeric':{'keys':['missing-time','analysis0'],'station_ids':['0007',' \t,"港"\r\n内陆😀 '],'values':[None,0,222,222],'forecast_times':[None,None,0,0],'fixture':'synthetic-zero-analysis.grib2','sha256':hashlib.sha256(synthetic).hexdigest(),'derivation':'Existing forecast09 first two messages, change only first simple-packing reference IEEE754 R=111 to R=0; E=D=0 and width=0 verified; bitmap/metadata unchanged. Independently expected valid first-field value0 and bitmap gap None.'},
  'summaries':{'real':4,'preview':1,'numeric':4,'empty':0},
}
(E/'REFERENCE.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Actual independent parser consumer module generated.')
