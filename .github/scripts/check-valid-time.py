"""Hand-frozen civil-calendar vectors, independent datetime/raw headers and real hosts."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'testdata/valid-time'
EXPECTED_SHA256='42e6938e1f503eddfdaf5868d99f8e7b328673a04614b4b04c021faca99cf60e'
FACTORS={0:60,1:3600,2:86400,10:10800,11:21600,12:43200,13:1}


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def digest(data):return hashlib.sha256(data).hexdigest()


def calendar_oracle(case):
    lead,unit,ref=case['lead'],case['unit'],case['reference']
    if lead is None:return {'error':'missing-forecast-time'}
    if unit not in FACTORS:return {'error':'unsupported-time-unit','unit':unit}
    if len(ref)!=6:return {'error':'invalid-reference-time'}
    try:
        date=dt.datetime(*[*ref[:5],59 if ref[5]==60 else ref[5]])
    except (ValueError,OverflowError):return {'error':'invalid-reference-time'}
    if ref[5]==60:return {'error':'unsupported-leap-second'}
    try:
        result=date+dt.timedelta(seconds=lead*FACTORS[unit])
    except OverflowError:return {'error':'out-of-range'}
    return {'valid_time':{k:getattr(result,k) for k in ('year','month','day','hour','minute','second')}}


def handwritten(case):
    if 'error' in case:
        return {'error':case['error'],**({'unit':case['unit']} if case['error']=='unsupported-time-unit' else {})}
    return {'valid_time':dict(zip(('year','month','day','hour','minute','second'),case['expected'],strict=True))}


def raw_products(data):
    """Independent Section1/4 metadata reader; never calls the MoonBit library."""
    entries=[];offset=0;message=0
    while offset<len(data):
        assert data[offset:offset+4]==b'GRIB' and data[offset+7]==2
        length=int.from_bytes(data[offset+8:offset+16],'big');assert data[offset+length-4:offset+length]==b'7777'
        point=offset+16;field=0;product=None;identity=None;scanning=None
        while point<offset+length-4:
            size=int.from_bytes(data[point:point+4],'big');section=data[point:point+size];assert size>=5 and point+size<=offset+length-4
            number=section[4]
            if number==1:
                identity={'centre':int.from_bytes(section[5:7],'big'),'subcentre':int.from_bytes(section[7:9],'big'),'master_table':section[9],'local_table':section[10],
                          'reference_time':[int.from_bytes(section[12:14],'big'),*section[14:19]]}
            elif number==3:
                assert section[12:14]==b'\0\0';scanning=section[71]
            elif number==4:
                assert section[7:9]==b'\0\0'
                def surface(start):
                    kind,scale=section[start:start+2];result={'kind':kind};value=int.from_bytes(section[start+2:start+6],'big')
                    if scale!=255:result['scale']=-(scale&127) if scale&128 else scale
                    if value!=0xffffffff:result['scaled_value']=value
                    return result
                product={'discipline':data[offset+6],'category':section[9],'parameter':section[10],**identity,'time_unit':section[17],
                         'first_surface':surface(22),'second_surface':surface(28)}
                encoded=int.from_bytes(section[18:22],'big')
                if encoded!=0xffffffff:product['forecast_time']=-(encoded&0x7fffffff) if encoded&0x80000000 else encoded
            elif number==7:
                entries.append({'index':len(entries),'origin':{'message':message,'field':field,'byte_offset':offset,'scanning_mode':scanning},'product':product});field+=1
            point+=size
        assert point==offset+length-4;offset+=length;message+=1
    assert offset==len(data)
    return entries


OUTCOME='''fn time_outcome(product : @grib2.Product) -> Json {
  match product.valid_time() {
    Ok(time) => { "valid_time": time.to_json() }
    Err(MissingForecastTime) => { "error": "missing-forecast-time" }
    Err(UnsupportedTimeUnit(unit)) => { "error": "unsupported-time-unit", "unit": unit.to_json() }
    Err(InvalidReferenceTime) => { "error": "invalid-reference-time" }
    Err(UnsupportedLeapSecond) => { "error": "unsupported-leap-second" }
    Err(TimeOutOfRange) => { "error": "out-of-range" }
  }
}
'''


def portable_source(fixture,cases):
    source='''///|
'''+OUTCOME+'''\n///|
fn product(reference : Array[Int], unit : Int, lead : Int?) -> @grib2.Product {
  { discipline: 0,category: 0,parameter: 0,centre: 98,subcentre: 0,
    master_table: 4,local_table: 0,reference_time: reference,time_unit: unit,
    forecast_time: lead,first_surface: {kind:103,scale:Some(0),scaled_value:Some(2U)},
    second_surface: {kind:255,scale:None,scaled_value:None} }
}
///|
fn emit(name : String, product : @grib2.Product) -> Unit {
  let before = product.to_json().stringify()
  let time = time_outcome(product)
  let row : Json = {"source":"public","case":name.to_json(),"product":product.to_json(),"time":time,"unchanged":(before == product.to_json().stringify()).to_json()}
  println(row.stringify())
}
///|
fn main {
  let fields = @grib2.read_fields(b"'''+''.join('\\x'+format(b,'02x') for b in fixture)+'''").unwrap()
  for index, field in fields {
    let p = field.product()
    let before = p.to_json().stringify()
    let time = time_outcome(p)
    let row : Json = {"source":"file","index":index.to_json(),"origin":field.origin().to_json(),"product":p.to_json(),"time":time,"unchanged":(before == field.product().to_json().stringify()).to_json()}
    println(row.stringify())
  }
'''
    for c in cases:
        lead='None' if c['lead'] is None else 'Some('+str(c['lead'])+')'
        source+='  emit('+json.dumps(c['name'])+', product('+json.dumps(c['reference'])+','+str(c['unit'])+','+lead+'))\n'
    source+='''  let hours = @grib2.select_unique_field(fields,@grib2.FieldQuery::new(0,0,0,time_unit=1,forecast_time=6,reference_time=[2024,2,29,0,0,0])).unwrap()
  let minutes = @grib2.select_unique_field(fields,@grib2.FieldQuery::new(0,0,0,time_unit=0,forecast_time=360,reference_time=[2024,2,29,0,0,0])).unwrap()
  let q : Json = {"source":"raw-query","hours_origin":hours.origin().to_json(),"minutes_origin":minutes.origin().to_json(),"hours_product":hours.product().to_json(),"minutes_product":minutes.product().to_json(),"same_valid_time":(hours.product().valid_time() == minutes.product().valid_time()).to_json()}
  println(q.stringify())
}
'''
    return source


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',required=True,type=Path);parser.add_argument('--moon',default='moon');args=parser.parse_args()
    work=args.work.resolve();assert not work.exists(),'Use a new work directory; retain failures';work.mkdir(parents=True);(work/'logs').mkdir();commands=[]
    def run(name,command,success=True):
        p=subprocess.run(list(map(str,command)),cwd=work,capture_output=True)
        label=f'{len(commands):02d}-'+name
        for extension,content in [('stdout',p.stdout),('stderr',p.stderr)]:(work/'logs'/(label+'.'+extension)).write_bytes(content)
        commands.append({'label':name,'command':list(map(str,command)),'exitCode':p.returncode,'expectedSuccess':success});write(work/'COMMANDS.json',commands)
        assert (p.returncode==0)==success,(name,p.stderr.decode('utf-8',errors='replace')[-2400:]);return p
    raw_expected=(DATA/'EXPECTED.json').read_bytes();assert digest(raw_expected)==EXPECTED_SHA256;expected=json.loads(raw_expected);cases=expected['cases']
    for c in cases:assert calendar_oracle(c)==handwritten(c),c['name']
    fixture=(DATA/'calendar.grib2').read_bytes();assert digest(fixture)==expected['fileSHA256'] and len(fixture)==expected['fileBytes']
    raw=raw_products(fixture);by_name={c['name']:c for c in cases};selected=[by_name[name] for name in expected['fileCases']];assert len(raw)==len(selected)==43
    for actual,c in zip(raw,selected,strict=True):
        assert actual['origin']==c['origin'] and actual['product']['reference_time']==c['reference'] and actual['product']['time_unit']==c['unit'] and actual['product'].get('forecast_time')==c['lead']
    module=work/'consumer';module.mkdir();(module/'moon.mod').write_text('name = "local/valid-time-consumer"\nimport { "toneklinkenberg824-spec/grib2@0.1.0", }\n',encoding='utf-8')
    (module/'moon.pkg').write_text('import { "toneklinkenberg824-spec/grib2", }\npkgtype(kind: "executable")\n',encoding='utf-8');(module/'main.mbt').write_text(portable_source(fixture,cases),encoding='utf-8')
    receiver=work/'receiver';receiver.mkdir()
    for name in ('main.mbt','moon.mod','moon.pkg','pkg.generated.mbti'):shutil.copyfile(ROOT/'examples/node-valid-time'/name,receiver/name)
    (work/'moon.work').write_text('members = '+json.dumps([str(ROOT),str(module),str(receiver)])+'\n',encoding='utf-8')
    outputs={}
    for target in ('js','wasm-gc'):
        p=run('portable-'+target,[args.moon,'-C',module,'run','.','--target',target]);rows=[json.loads(line) for line in p.stdout.splitlines() if line.strip()]
        assert len(rows)==43+len(cases)+1
        for row,entry,c in zip(rows[:43],raw,selected,strict=True):assert row=={'source':'file',**entry,'time':handwritten(c),'unchanged':True}
        for row,c in zip(rows[43:-1],cases,strict=True):
            assert row['source']=='public' and row['case']==c['name'] and row['time']==handwritten(c) and row['unchanged'] is True
            assert row['product']['reference_time']==c['reference'] and row['product']['time_unit']==c['unit'] and row['product'].get('forecast_time')==c['lead']
        hours,minutes=[by_name[name] for name in ('same-instant-hours','same-instant-minutes')]
        q=rows[-1];assert q['source']=='raw-query' and q['same_valid_time'] is True
        assert q['hours_origin']==hours['origin'] and q['minutes_origin']==minutes['origin']
        assert q['hours_product']['time_unit']==1 and q['hours_product']['forecast_time']==6 and q['minutes_product']['time_unit']==0 and q['minutes_product']['forecast_time']==360
        outputs[target]=rows
    assert outputs['js']==outputs['wasm-gc']
    run('build-node',[args.moon,'-C',receiver,'build','--target','js']);binary=work/'_build/js/debug/build/local/grib2-valid-time/grib2-valid-time.js';assert binary.is_file()
    inputs=[('calendar',fixture),('NOAA',(ROOT/'testdata/noaa-gfs-repacked.grib2').read_bytes())]
    for name,data in inputs:
        path=work/(name+' 预报😀.grib2');path.write_bytes(data);p=run('node-'+name,['node',binary,path]);assert not p.stderr
        actual=json.loads(p.stdout);entries=raw_products(data);wanted=[]
        for entry in entries:
            product=entry['product'];c={'reference':product['reference_time'],'unit':product['time_unit'],'lead':product.get('forecast_time')}
            wanted.append({**entry,'time':calendar_oracle(c)})
        assert actual=={'field_count':len(entries),'fields':wanted}
    for name,data,event in [('unsupported',(ROOT/'testdata/message-spans/unsupported.grib2').read_bytes(),{'phase':'decode','code':'unsupported-template','section':3,'template':1}),
                            ('late-unsupported',fixture+(ROOT/'testdata/message-spans/unsupported.grib2').read_bytes(),{'phase':'decode','code':'unsupported-template','section':3,'template':1}),
                            ('late-corrupt',fixture+b'junk',None),('empty',b'',None)]:
        path=work/(name+'.grib2');path.write_bytes(data);p=run('node-'+name,['node',binary,path],False);assert not p.stdout
        first=json.loads(p.stderr.decode('utf-8').splitlines()[0]);assert first['phase']=='decode'
        if event is not None:assert first==event
        else:assert first['code']=='corrupted-bitstream'
    for name,arguments in [('missing-input',[work/'missing.grib2']),('usage',[])]:
        p=run('node-'+name,['node',binary,*arguments],False);assert not p.stdout
    result={'status':'PASS','publicCasesPerTarget':len(cases),'rawFileFieldsPerTarget':len(raw),'publicTargets':['js','wasm-gc'],'rawQueryNonNormalizationProbePerTarget':1,
        'dualBackendSemanticEquality':True,'rawProductImmutability':True,'handwrittenAndDatetimeOraclesAgree':True,'wideIntegerAndCalendarBounds':True,
        'nodeSuccessProcesses':2,'nodeExpectedFailureProcesses':6,'nodeBuildProcesses':1,'portableBuildRunProcesses':2,'actualProcessInvocations':len(commands),
        'newCalendarVectorsNotOldSpanVectors':True,'oldScientificGeneratorsAndLocalSuitesRerun':False,'frozenExpectedSHA256':EXPECTED_SHA256}
    assert len(commands)==11;write(work/'RESULT.json',result);print(json.dumps(result))


if __name__=='__main__':main()
