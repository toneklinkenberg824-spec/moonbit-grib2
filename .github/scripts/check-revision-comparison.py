"""Independent original bits/rational station oracle for paired revision comparisons."""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'testdata/revision-comparison'
EXPECTED_SHA256='1f17f35d5ec9fa0d72c80fdf3b8cf4fbe9722422aa3f87394f2cbd448c0e3e1c'


def write(path,value,bom=False):path.write_text(('\ufeff' if bom else '')+json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def digest(data):return hashlib.sha256(data).hexdigest()


def signed(value,bits):return -(value&((1<<(bits-1))-1)) if value>>(bits-1) else value


def raw_models(data):
    out=[];offset=0
    while offset<len(data):
        assert data[offset:offset+4]==b'GRIB' and data[offset+7]==2
        length=int.from_bytes(data[offset+8:offset+16],'big');assert data[offset+length-4:offset+length]==b'7777'
        p=offset+16;sections={}
        while p<offset+length-4:
            size=int.from_bytes(data[p:p+4],'big');assert size>=5 and p+size<=offset+length-4;sections[data[p+4]]=data[p:p+size];p+=size
        assert p==offset+length-4 and set(sections)=={1,3,4,5,6,7}
        s1,s3,s4,s5,s6,s7=[sections[n] for n in (1,3,4,5,6,7)]
        assert s3[12:14]==s4[7:9]==s5[9:11]==b'\0\0' and int.from_bytes(s3[30:34],'big')==3 and int.from_bytes(s3[34:38],'big')==2 and s3[71]==0
        def surface(start):
            result={'kind':s4[start]};scale=s4[start+1];value=int.from_bytes(s4[start+2:start+6],'big')
            if scale!=255:result['scale']=signed(scale,8)
            if value!=0xffffffff:result['scaled_value']=value
            return result
        product={'discipline':data[offset+6],'category':s4[9],'parameter':s4[10],'centre':int.from_bytes(s1[5:7],'big'),'subcentre':int.from_bytes(s1[7:9],'big'),'master_table':s1[9],'local_table':s1[10],
            'reference_time':[int.from_bytes(s1[12:14],'big'),*s1[14:19]],'time_unit':s4[17],'first_surface':surface(22),'second_surface':surface(28)}
        lead=int.from_bytes(s4[18:22],'big')
        if lead!=0xffffffff:product['forecast_time']=signed(lead,32)
        ref=Fraction.from_float(struct.unpack('>f',s5[11:15])[0]);binary=signed(int.from_bytes(s5[15:17],'big'),16);decimal=signed(int.from_bytes(s5[17:19],'big'),16);bits=s5[19]
        assert bits in (0,8) and decimal in (0,-308)
        mask=[True]*6 if s6[5]==255 else [bool(s6[6]&(1<<(7-i))) for i in range(6)]
        assert sum(mask)==int.from_bytes(s5[5:9],'big')
        packed=iter(s7[5:]);values=[]
        for valid in mask:
            values.append(float((ref+(next(packed) if bits else 0)*Fraction(2)**binary)/Fraction(10)**decimal) if valid else None)
        assert len(s7)==5+(sum(mask) if bits else 0)
        out.append({'index':len(out),'origin':{'message':len(out),'field':0,'byte_offset':offset,'scanning_mode':0},'product':product,'north':signed(int.from_bytes(s3[46:50],'big'),32)/1000000,
                    'west':int.from_bytes(s3[50:54],'big')/1000000,'values':values,'rawBytes':length,'rawSHA256':digest(data[offset:offset+length])})
        offset+=length
    assert offset==len(data);return out


def sample(model,station):
    latitude,longitude=station['latitude'],station['longitude']
    if isinstance(latitude,str) or isinstance(longitude,str) or not math.isfinite(latitude) or not math.isfinite(longitude) or not -90<=latitude<=90:return {'failure':'invalid-station'}
    y=Fraction(str(model['north']))-Fraction(str(latitude));x=(Fraction(str(longitude))%360-Fraction(str(model['west'])))%360
    if not 0<=y<=1 or not 0<=x<=2:return {'failure':'outside-grid'}
    r0,c0=int(y),int(x);r1,c1=min(r0+1,1),min(c0+1,2);ty,tx=y-r0,x-c0
    nodes=[(r0,c0,(1-ty)*(1-tx)),(r0,c1,(1-ty)*tx),(r1,c0,ty*(1-tx)),(r1,c1,ty*tx)];contributors=[];total=Fraction(0)
    for r,c,w in nodes:
        if not w:continue
        value=model['values'][r*3+c]
        if value is None:return {'failure':'missing-data'}
        total+=w*Fraction.from_float(float(value))
        contributors.append({'row':r,'col':c,'source_index':r*3+c,'latitude':model['north']-r,'longitude':model['west']+c,'weight':float(w),'value':value})
    return {'sample':{'station':station,'origin':model['origin'],'product':model['product'],'value':float(total),'algorithm':'bilinear-latlon','contributors':contributors}}


def rows_oracle(left,right,stations):
    rows=[]
    for station in stations:
        a,b=sample(left,station),sample(right,station)
        if 'failure' in a or 'failure' in b:difference={'error':'sampling-unavailable'}
        else:
            value=b['sample']['value']-a['sample']['value'];difference={'value':value} if math.isfinite(value) else {'error':'nonfinite-difference'}
        rows.append({'station':station,'left':a,'right':b,'difference':difference})
    return rows


def agrees(actual,expected):
    if isinstance(expected,dict):return isinstance(actual,dict) and actual.keys()==expected.keys() and all(agrees(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(agrees(a,b) for a,b in zip(actual,expected,strict=True))
    if isinstance(expected,(int,float)) and not isinstance(expected,bool) and abs(expected)>1e300:
        return isinstance(actual,(int,float)) and math.isfinite(actual) and abs(actual/expected-1)<=1e-12
    return actual==expected


def public_source(fixture,cases,stations):
    source='''///|
fn state(fields : Array[@grib2.GriddedField]) -> String {
  let snapshot : Array[Json] = fields.map(f => {"product":f.product().to_json(),"values":f.values().to_json(),"mask":f.mask().to_json(),"origin":f.origin().to_json()})
  snapshot.to_json().stringify()
}
///|
fn emit(name : String, fields : Array[@grib2.GriddedField], left : Int,right : Int,stations : Array[@grib2.Station],before : String) -> Unit {
  let result : Json = match fields[left].compare_stations(fields[right],stations) {
    Ok(rows) => {"rows":rows.to_json()}
    Err(error) => {"error":error.to_json()}
  }
  let out : Json = {"case":name.to_json(),"result":result,"unchanged":(state(fields)==before).to_json()}
  println(out.stringify())
}
///|
fn main {
  let fields = @grib2.read_fields(b"'''+''.join('\\x'+format(b,'02x') for b in fixture)+'''").unwrap()
  let before=state(fields)
  let stations : Array[@grib2.Station] = [
'''
    for s in stations:source+='    {id:'+json.dumps(s['id'],ensure_ascii=False)+',latitude:'+str(s['latitude'])+',longitude:'+str(s['longitude'])+'},\n'
    source+='  ]\n'
    for c in cases:source+='  emit('+json.dumps(c['name'])+',fields,'+str(c['left'])+','+str(c['right'])+','+('[]' if c.get('empty') else 'stations')+',before)\n'
    return source+'}\n'


def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--moon',default='moon');args=p.parse_args();work=args.work.resolve();assert not work.exists(),'Use a fresh work directory';work.mkdir(parents=True);(work/'logs').mkdir();commands=[]
    def run(name,command,success=True):
        process=subprocess.run(list(map(str,command)),cwd=work,capture_output=True);label=f'{len(commands):02d}-'+name
        for suffix,content in [('stdout',process.stdout),('stderr',process.stderr)]:(work/'logs'/(label+'.'+suffix)).write_bytes(content)
        commands.append({'label':name,'command':list(map(str,command)),'exitCode':process.returncode,'expectedSuccess':success});write(work/'COMMANDS.json',commands)
        assert (process.returncode==0)==success,(name,process.stderr.decode('utf-8',errors='replace')[:2000]);return process
    raw_expected=(DATA/'EXPECTED.json').read_bytes();assert digest(raw_expected)==EXPECTED_SHA256;expected=json.loads(raw_expected);fixture=(DATA/'fields.grib2').read_bytes()
    for name,pin in expected['files'].items():assert digest((DATA/name).read_bytes())==pin['sha256'] and (DATA/name).stat().st_size==pin['bytes']
    models=raw_models(fixture);assert len(models)==len(expected['models'])==24
    for actual,frozen in zip(models,expected['models'],strict=True):assert actual=={k:v for k,v in frozen.items() if k!='name'}
    assert json.loads((DATA/'stations.json').read_text(encoding='utf-8'))==expected['stations'];stations=expected['stations'];cases=expected['cases'];names={m['name']:m['index'] for m in expected['models']}
    # Four explicit error-order probes use the already-frozen priority contract.
    extra=[('parameter-before-time','different-parameter','missing-time',{'code':'parameter-mismatch'}),('table-before-surface','different-centre','different-first_kind',{'code':'table-mismatch'}),
           ('surface-before-time','different-first_kind','missing-time',{'code':'surface-mismatch'}),('left-time-before-right','missing-time','unsupported-time',{'code':'left-time','reason':{'code':'missing-forecast-time'}})]
    cases=[*cases,*[{'name':n,'left':names[a],'right':names[b],'error':e} for n,a,b,e in extra]]
    want={}
    for c in cases:
        rows=rows_oracle(models[c['left']],models[c['right']],[] if c.get('empty') else stations) if 'error' not in c else None
        want[c['name']]={'error':c['error']} if 'error' in c else {'rows':rows}
        if 'handDifference' in c:
            assert [r['left'].get('sample',{}).get('value') for r in rows]==c['handLeft'] and [r['right'].get('sample',{}).get('value') for r in rows]==c['handRight']
            assert [r['difference'].get('value') for r in rows]==c['handDifference']
        if 'interiorHandDifference' in c:assert rows[3]['difference']['value']==c['interiorHandDifference']
    assert all('nonfinite-difference'==r['difference'].get('error') for r in want['difference-overflow']['rows'] if 'sample' in r['left'] and 'sample' in r['right'])
    write(work/'INDEPENDENT-EXPECTED.json',want)
    module=work/'consumer';module.mkdir();(module/'moon.mod').write_text('name = "local/revision-public"\nimport { "toneklinkenberg824-spec/grib2@0.1.0", }\n',encoding='utf-8');(module/'moon.pkg').write_text('import { "toneklinkenberg824-spec/grib2", }\npkgtype(kind: "executable")\n',encoding='utf-8');(module/'main.mbt').write_text(public_source(fixture,cases,stations),encoding='utf-8')
    receiver=work/'receiver';receiver.mkdir()
    for name in ('main.mbt','moon.mod','moon.pkg','pkg.generated.mbti'):shutil.copyfile(ROOT/'examples/node-revision-compare'/name,receiver/name)
    (work/'moon.work').write_text('members = '+json.dumps([str(ROOT),str(module),str(receiver)])+'\n',encoding='utf-8');outputs={}
    for target in ('js','wasm-gc'):
        result=run('public-'+target,[args.moon,'-C',module,'run','.','--target',target]);rows=[json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        assert len(rows)==len(cases)==30
        for row,c in zip(rows,cases,strict=True):assert agrees(row,{'case':c['name'],'result':want[c['name']],'unchanged':True}),(target,c['name'],row,want[c['name']])
        outputs[target]=rows
    assert outputs['js']==outputs['wasm-gc'];run('build-node',[args.moon,'-C',receiver,'build','--target','js']);binary=work/'_build/js/debug/build/local/grib2-revision-compare/grib2-revision-compare.js';assert binary.is_file()
    left=work/'左 修订😀.grib2';right=work/'右 修订😀.grib2';left.write_bytes((DATA/'left.grib2').read_bytes());right.write_bytes((DATA/'right.grib2').read_bytes());station_path=work/'站点😀.json';write(station_path,stations,True)
    def invoke(name,lpath=left,lindex='1',rpath=right,rindex='0',station_file=station_path,event=None,success=True):
        result=run(name,['node',binary,lpath,lindex,rpath,rindex,station_file],success)
        if not success:
            assert not result.stdout
            if event is not None:assert json.loads(result.stderr.decode('utf-8').splitlines()[0])==event
            return None
        assert not result.stderr;return json.loads(result.stdout)
    def verify_file_result(actual,lpath,li,rpath,ri,input_stations):
        lm=raw_models(lpath.read_bytes())[li];rm=raw_models(rpath.read_bytes())[ri];rows=rows_oracle(lm,rm,input_stations);available=sum('value' in r['difference'] for r in rows)
        assert agrees(actual,{'operation':'right-minus-left','valid_time':expected['validTime'],'left':{k:lm[k] for k in ('index','origin','product')},'right':{k:rm[k] for k in ('index','origin','product')},
            'station_count':len(rows),'available_count':available,'unavailable_count':len(rows)-available,'rows':rows})
    actual=invoke('paired-files');verify_file_result(actual,left,1,right,0,stations)
    actual=invoke('swapped-files',right,'0',left,'0x1');verify_file_result(actual,right,0,left,1,stations)
    empty=work/'empty-stations.json';write(empty,[]);actual=invoke('empty-stations',station_file=empty);verify_file_result(actual,left,1,right,0,[])
    nan_station=[{'id':'NaN','latitude':'NaN','longitude':10}];nan_path=work/'nan-station.json';write(nan_path,nan_station);actual=invoke('nan-station',station_file=nan_path);verify_file_result(actual,left,1,right,0,nan_station)
    fields=DATA/'fields.grib2';actual=invoke('different-grids',fields,'2',fields,str(names['different-grid']));verify_file_result(actual,fields,2,fields,names['different-grid'],stations)
    actual=invoke('nonfinite-difference',fields,str(names['large-negative']),fields,str(names['large-positive']));verify_file_result(actual,fields,names['large-negative'],fields,names['large-positive'],stations)
    for c in [cases[9],cases[12],cases[16],next(c for c in cases if c['name']=='right-missing'),next(c for c in cases if c['name']=='valid-time-mismatch')]:
        invoke('error-'+c['name'],fields,str(c['left']),fields,str(c['right']),event={'phase':'comparison','error':c['error']},success=False)
    for name,li,ri,side in [('invalid-left','0.5','0','left'),('invalid-right','1','bad','right'),('overflow-index','2147483648','0','left')]:invoke(name,lpath=work/'not-read.grib2',lindex=li,rindex=ri,event={'phase':'selection','code':'invalid-field-index','side':side},success=False)
    for name,li,ri,side in [('negative-left','-1','0','left'),('outside-right','1','2','right')]:invoke(name,lindex=li,rindex=ri,event={'phase':'selection','code':'field-index-out-of-range','side':side,'field_count':2},success=False)
    unsupported=(ROOT/'testdata/message-spans/unsupported.grib2').read_bytes();bad=work/'late-unsupported.grib2';bad.write_bytes(right.read_bytes()+unsupported)
    invoke('late-right-decode',rpath=bad,event={'phase':'decode','code':'unsupported-template','section':3,'template':1},success=False)
    invoke('missing-input',lpath=work/'missing.grib2',success=False)
    broken=work/'broken-stations.json';broken.write_text('[',encoding='utf-8');invoke('bad-stations',station_file=broken,success=False)
    result=run('usage',['node',binary],False);assert not result.stdout
    assert left.read_bytes()==(DATA/'left.grib2').read_bytes() and right.read_bytes()==(DATA/'right.grib2').read_bytes()
    node=[c for c in commands if c['command'][0]=='node'];result={'status':'PASS','frozenComparisonCases':26,'additionalPriorityProbes':4,'publicCasesPerTarget':30,'publicTargets':['js','wasm-gc'],
        'completeIndependentRationalRows':True,'originalBitsProductsAndContributors':True,'bothSamplingFailuresAndOverflow':True,'dualBackendEquality':True,'sourceFieldStateUnchanged':True,
        'nodeSuccessProcesses':sum(c['expectedSuccess'] for c in node),'nodeExpectedFailureProcesses':sum(not c['expectedSuccess'] for c in node),'nodeBuildProcesses':1,'publicBuildRunProcesses':2,
        'actualProcessInvocations':len(commands),'frozenExpectedSHA256':EXPECTED_SHA256,'oldScientificOrTimeOrSpanSuitesLocallyRerun':False}
    write(work/'RESULT.json',result);print(json.dumps(result))


if __name__=='__main__':main()
