"""Original3.0 singleton-axis bytes, rational profiles and unchanged file receiver."""
import argparse
import copy
import csv
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'testdata/singleton-axes'
EXPECTED_SHA256='deef75605bdb0ab398c3c3483cd711047d1ec9588c1e0f230a74f3e65f7b1cf5'
HEADER=['request_key','station_id','latitude','longitude','value','algorithm','message','field','byte_offset','product_json','contributors_json']


def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def signed(n,bits):return -(n&((1<<(bits-1))-1)) if n>>(bits-1) else n


def raw_fields(raw):
    fields=[];offset=0
    while offset<len(raw):
        assert raw[offset:offset+4]==b'GRIB' and raw[offset+7]==2;length=int.from_bytes(raw[offset+8:offset+16],'big');assert raw[offset+length-4:offset+length]==b'7777';p=offset+16;sections={}
        while p<offset+length-4:
            n=int.from_bytes(raw[p:p+4],'big');assert n>=5 and p+n<=offset+length-4;sections[raw[p+4]]=raw[p:p+n];p+=n
        assert p==offset+length-4 and set(sections)=={1,3,4,5,6,7};s1,g,s4,d,b,payload=[sections[n] for n in (1,3,4,5,6,7)]
        assert len(g)==72 and g[12:14]==s4[7:9]==d[9:11]==b'\0\0' and not g[71]&15
        nc,nr=[int.from_bytes(g[i:i+4],'big') for i in (30,34)];assert nr*nc==int.from_bytes(g[6:10],'big')
        basic,subdiv=[int.from_bytes(g[i:i+4],'big') for i in (38,42)];unit=Fraction(1,1000000) if basic==0 else Fraction(basic,subdiv)
        lat1=signed(int.from_bytes(g[46:50],'big'),32)*unit;lat2=signed(int.from_bytes(g[55:59],'big'),32)*unit;lon1=int.from_bytes(g[50:54],'big')*unit;lon2=int.from_bytes(g[59:63],'big')*unit
        di,dj=[int.from_bytes(g[i:i+4],'big') for i in (63,67)];dx=Fraction(0) if di==0xffffffff else di*unit;dy=Fraction(0) if dj==0xffffffff else dj*unit
        assert d[11:19]==bytes(8) and d[19]==8
        valid=[True]*(nr*nc) if b[5]==255 else [bool(b[6+i//8]&(1<<(7-i%8))) for i in range(nr*nc)]
        assert sum(valid)==int.from_bytes(d[5:9],'big') and len(payload)==5+sum(valid)
        packed=iter(payload[5:]);source_values=[next(packed) if ok else None for ok in valid];scan=g[71]
        if nr==1:order=[(0,c) for c in (range(nc-1,-1,-1) if scan&128 else range(nc))]
        elif nc==1:order=[(r,0) for r in (range(nr-1,-1,-1) if scan&64 else range(nr))]
        else:assert scan==0;order=[(r,c) for r in range(nr) for c in range(nc)]
        values=[None]*(nr*nc);indices=[0]*(nr*nc)
        for i,(r,c) in enumerate(order):values[r*nc+c]=source_values[i];indices[r*nc+c]=i
        def surface(start):
            result={'kind':s4[start]};scale=s4[start+1];v=int.from_bytes(s4[start+2:start+6],'big')
            if scale!=255:result['scale']=signed(scale,8)
            if v!=0xffffffff:result['scaled_value']=v
            return result
        product={'discipline':raw[offset+6],'category':s4[9],'parameter':s4[10],'centre':int.from_bytes(s1[5:7],'big'),'subcentre':int.from_bytes(s1[7:9],'big'),'master_table':s1[9],'local_table':s1[10],
            'reference_time':[int.from_bytes(s1[12:14],'big'),*s1[14:19]],'time_unit':s4[17],'first_surface':surface(22),'second_surface':surface(28)}
        lead=int.from_bytes(s4[18:22],'big')
        if lead!=0xffffffff:product['forecast_time']=signed(lead,32)
        fields.append({'rows':nr,'cols':nc,'north':float(max(lat1,lat2)),'west':float(min(lon1%360,lon2%360)),'dx':float(dx),'dy':float(dy),'cyclic':nc*dx==360,'values':values,'source_indices':indices,
            'raw_dx':None if di==0xffffffff else di,'raw_dy':None if dj==0xffffffff else dj,'scanning_mode':scan,'category':s4[9],
            'origin':{'message':len(fields),'field':0,'byte_offset':offset,'scanning_mode':scan},'product':product,'bytes':length,'sha256':sha(raw[offset:offset+length])})
        offset+=length
    assert offset==len(raw);return fields


def points(model):
    return [{'row':r,'col':c,'source_index':model['source_indices'][r*model['cols']+c],'latitude':model['north']-r*model['dy'],'longitude':(model['west']+c*model['dx'])%360,'value':model['values'][r*model['cols']+c]} for r in range(model['rows']) for c in range(model['cols'])]


def sample(model,station):
    lat,lon=station['latitude'],station['longitude']
    if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90:return {'failure':'invalid-station'}
    if model['rows']==1 and model['dy']==0:
        if lat!=model['north']:return {'failure':'outside-grid'}
        y=Fraction(0)
    else:y=(Fraction(str(model['north']))-Fraction(str(lat)))/Fraction(str(model['dy']))
    if model['cols']==1 and model['dx']==0:
        if lon%360!=model['west']:return {'failure':'outside-grid'}
        x=Fraction(0)
    else:x=(Fraction(str(lon))%360-Fraction(str(model['west'])))%360/Fraction(str(model['dx']))
    if not 0<=y<=model['rows']-1 or (not model['cyclic'] and x>model['cols']-1):return {'failure':'outside-grid'}
    nr,nc=model['rows'],model['cols'];r0=int(y);ty=y-r0;r1=min(r0+1,nr-1)
    # Singleton cyclic columns are the existing uniform periodic column policy.
    c0=int(x)%nc;c1=(c0+1)%nc if model['cyclic'] else min(c0+1,nc-1);tx=x-int(x);nodes={}
    for r,w in [(r0,1-ty),(r1,ty)]:
        if not w:continue
        if abs(model['north']-r*model['dy'])==90:
            if model['category']==2:return {'failure':'unsupported-polar-vector'}
            present=[c for c in range(nc) if model['values'][r*nc+c] is not None]
            if not present:return {'failure':'missing-data'}
            for c in present:nodes[(r,c)]=nodes.get((r,c),Fraction(0))+w/len(present)
        else:
            for c,cw in [(c0,1-tx),(c1,tx)]:
                if not cw:continue
                if model['values'][r*nc+c] is None:return {'failure':'missing-data'}
                nodes[(r,c)]=nodes.get((r,c),Fraction(0))+w*cw
    contributors=[];total=Fraction(0)
    for (r,c),weight in nodes.items():
        value=model['values'][r*nc+c];total+=weight*value;contributors.append({'row':r,'col':c,'source_index':model['source_indices'][r*nc+c],'latitude':model['north']-r*model['dy'],'longitude':(model['west']+c*model['dx'])%360,'weight':float(weight),'value':value})
    polar=abs(model['north']-r0*model['dy'])==90 or (ty>0 and abs(model['north']-r1*model['dy'])==90)
    return {'sample':{'station':station,'origin':model['origin'],'product':model['product'],'value':float(total),'algorithm':'bilinear-polar-scalar-mean' if polar else 'bilinear-latlon','contributors':contributors}}


def legacy(model,station):
    result=sample(model,station)
    return result['sample'] if 'sample' in result else {'station':station,'origin':model['origin'],'product':model['product'],'value':None,'algorithm':'outside-or-missing','contributors':[]}


def agrees(actual,expected):
    if isinstance(expected,dict):return isinstance(actual,dict) and actual.keys()==expected.keys() and all(agrees(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(agrees(a,b) for a,b in zip(actual,expected,strict=True))
    if isinstance(expected,(int,float)) and not isinstance(expected,bool) and isinstance(actual,(int,float)):
        return math.isfinite(actual) and abs(actual-expected)<=1e-12*max(1,abs(expected))
    return actual==expected


def source(fixture,models,bad):
    text='''///|
fn error_json(error : @grib2.GribError) -> Json {
  match error { InvalidGrid(message) => {"code":"invalid-grid","message":message.to_json()}; InvalidRequest(message) => {"code":"invalid-request","message":message.to_json()}; _ => {"code":"unexpected"} }
}
///|
fn emit(index : Int, field : @grib2.GriddedField, stations : Array[@grib2.Station]) -> Unit {
  let before = field.values().to_json().stringify()+field.mask().to_json().stringify()+field.product().to_json().stringify()
  let nodes : Array[@grib2.GridPoint] = []
  for r in 0..<field.rows() { for c in 0..<field.cols() { nodes.push(field.point(r,c).unwrap()) } }
  let samples : Array[Json] = stations.map(s => match field.sample_result(s) { Ok(v) => {"sample":v.to_json()}; Err(e) => {"failure":e.to_json()} })
  let box : @grib2.BBox = {south:-90.0,north:90.0,west:0.0,east:360.0}
  let narrow : @grib2.BBox = {south:field.north,north:field.north,west:field.west,east:field.west}
  let out : Json = {"field":index.to_json(),"rows":field.rows().to_json(),"cols":field.cols().to_json(),"north":field.north.to_json(),"west":field.west.to_json(),"dx":field.dx.to_json(),"dy":field.dy.to_json(),"cyclic":field.is_global().to_json(),
    "origin":field.origin().to_json(),"product":field.product().to_json(),"values":field.values().to_json(),"mask":field.mask().to_json(),"points":nodes.to_json(),"samples":samples.to_json(),"legacy":field.sample_stations(stations).to_json(),
    "crop":field.crop(box).unwrap().to_json(),"iter":field.crop_iter(box).unwrap().collect().to_json(),"narrow":field.crop(narrow).unwrap().to_json(),
    "unchanged":(before==field.values().to_json().stringify()+field.mask().to_json().stringify()+field.product().to_json().stringify()).to_json()}
  println(out.stringify())
}
///|
fn main {
  let fields = @grib2.read_fields(b"'''+''.join('\\x'+format(b,'02x') for b in fixture)+'''").unwrap()
'''
    for i,m in enumerate(models):
        def number(value):
            text=repr(float(value))
            if 'e' in text and '.' not in text.split('e')[0]:text=text.replace('e','.0e',1)
            return text
        stations='['+','.join('{id:'+json.dumps(q['id'])+',latitude:'+number(q['latitude'])+',longitude:'+number(q['longitude'])+'}' for q in m['queries'])+']'
        text+='  emit('+str(i)+',fields['+str(i)+'],'+stations+')\n'
    for m in bad:
        raw=(ROOT/m['path']).read_bytes();text+='  let error = match @grib2.read_fields(b"'+''.join('\\x'+format(b,'02x') for b in raw)+'") { Err(e) => error_json(e); Ok(_) => {"code":"accepted-invalid"} }\n  let row : Json = {"bad":'+json.dumps(m['name'])+',"error":error};println(row.stringify())\n'
    point=(DATA/'point-zero.grib2').read_bytes();line=(DATA/'column-0.grib2').read_bytes()
    text+='  let small = @grib2.read_fields(b"'+''.join('\\x'+format(b,'02x') for b in point)+'",max_points=1).unwrap()\n'
    text+='  let budget = match @grib2.read_fields(b"'+''.join('\\x'+format(b,'02x') for b in line)+'",max_points=2) {Err(e)=>error_json(e);Ok(_)=>{"code":"accepted-invalid"}}\n'
    text+='  let single = match @grib2.read_message(b"'+''.join('\\x'+format(b,'02x') for b in fixture)+'") {Err(e)=>error_json(e);Ok(_)=>{"code":"accepted-invalid"}}\n'
    return text+'  let controls : Json = {"controls":true,"point_budget_one":small.length().to_json(),"line_budget_two":budget,"multi_message":single};println(controls.stringify())\n}\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',required=True,type=Path);parser.add_argument('--moon',default='moon');args=parser.parse_args();work=args.work.resolve();assert not work.exists();work.mkdir(parents=True);(work/'logs').mkdir();commands=[]
    def run(name,command,success=True,cwd=work):
        p=subprocess.run(list(map(str,command)),cwd=cwd,capture_output=True);prefix=f'{len(commands):02d}-'+name
        for suffix,raw in [('stdout',p.stdout),('stderr',p.stderr)]:(work/'logs'/(prefix+'.'+suffix)).write_bytes(raw)
        commands.append({'label':name,'command':list(map(str,command)),'cwd':str(cwd),'exitCode':p.returncode,'expectedSuccess':success});write(work/'COMMANDS.json',commands)
        assert (p.returncode==0)==success,(name,p.stderr.decode('utf-8',errors='replace')[:2500]);return p
    raw_expected=(DATA/'EXPECTED.json').read_bytes();assert sha(raw_expected)==EXPECTED_SHA256;expected=json.loads(raw_expected);fixture=(DATA/'all-supported.grib2').read_bytes();assert sha(fixture)==expected['allSupportedSHA256']
    supported=expected['models'][:expected['supportedFields']];bad=expected['models'][expected['supportedFields']:];decoded=raw_fields(fixture);assert len(decoded)==len(supported)==43
    for m in expected['models']:
        raw=(ROOT/m['path']).read_bytes();assert sha(raw)==m['sha256'] and len(raw)==m['bytes']
        d=raw_fields(raw)[0]
        for k in ('rows','cols','raw_dx','raw_dy','values','source_indices','scanning_mode','category'):assert d[k]==m[k],(m['name'],k)
    wanted=[]
    for i,(m,d) in enumerate(zip(supported,decoded,strict=True)):
        for k in ('rows','cols','north','west','dx','dy','cyclic','origin','values','source_indices'):assert d[k]==m[k],(m['name'],k)
        nodes=points(d);narrow=[n for n in nodes if n['latitude']==d['north'] and n['longitude']==d['west']]
        wanted.append({'field':i,**{k:d[k] for k in ('rows','cols','north','west','dx','dy','cyclic','origin','product')},'values':['NaN' if x is None else x for x in d['values']],'mask':[x is not None for x in d['values']],
            'points':nodes,'samples':[sample(d,q) for q in m['queries']],'legacy':[legacy(d,q) for q in m['queries']],'crop':nodes,'iter':nodes,'narrow':narrow,'unchanged':True})
    by_name={m['name']:i for i,m in enumerate(supported)}
    assert wanted[by_name['column-0']]['samples'][3]['sample']['value']==15 and wanted[by_name['row-0']]['samples'][3]['sample']['value']==45
    assert wanted[by_name['point-zero']]['samples'][0]['sample']['value']==7 and wanted[by_name['global-row']]['samples'][-1]['sample']['value']==25
    assert wanted[by_name['pole-row']]['samples'][0]['sample']['value']==25 and wanted[by_name['pole-vector']]['samples'][0]=={'failure':'unsupported-polar-vector'}
    write(work/'INDEPENDENT-EXPECTED.json',wanted)
    consumer=work/'consumer';consumer.mkdir();(consumer/'moon.mod').write_text('name = "local/singleton-public"\nimport { "zhou-wei97/grib2@0.1.0", }\n',encoding='utf-8');(consumer/'moon.pkg').write_text('import { "zhou-wei97/grib2", }\npkgtype(kind: "executable")\n',encoding='utf-8');(consumer/'main.mbt').write_text(source(fixture,supported,bad),encoding='utf-8')
    receiver=work/'receiver';receiver.mkdir()
    for name in ('main.mbt','moon.mod','moon.pkg','pkg.generated.mbti'):shutil.copyfile(ROOT/'examples/node-file17'/name,receiver/name)
    (work/'moon.work').write_text('members = '+json.dumps([str(ROOT),str(consumer),str(receiver)])+'\n',encoding='utf-8');outputs={}
    for target in ('js','wasm-gc'):
        p=run('targeted-tests-'+target,[args.moon,'test','singleton_axes_test.mbt','--target',target,'--target-dir',work/('unit-'+target)],cwd=ROOT)
        assert re.search(r'Total tests:\s*4,\s*passed:\s*4,\s*failed:\s*0',(p.stdout+p.stderr).decode('utf-8',errors='replace'))
        p=run('public-'+target,[args.moon,'-C',consumer,'run','.','--target',target]);rows=[json.loads(line) for line in p.stdout.splitlines() if line.strip()];assert len(rows)==48
        for actual,want in zip(rows[:43],wanted,strict=True):assert agrees(actual,want),(target,actual['field'],actual,want)
        assert rows[43:47]==[{'bad':m['name'],'error':{'code':'invalid-grid','message':m['error']}} for m in bad]
        assert rows[-1]=={'controls':True,'point_budget_one':1,'line_budget_two':{'code':'invalid-grid','message':'invalid grid size or max_points exceeded'},'multi_message':{'code':'invalid-request','message':'expected one field; use read_fields'}}
        outputs[target]=rows
    assert outputs['js']==outputs['wasm-gc'];run('build-unchanged-node',[args.moon,'-C',receiver,'build','--target','js']);binary=work/'_build/js/debug/build/local/grib2-file17/grib2-file17.js';assert binary.is_file()
    selected=['column-0','column-16','row-0','row-16','point-zero','point-missing','point-all-missing','column-gap','row-gap','global-row','pole-row','pole-vector','basic-angle-column','legacy-positive-row','legacy-positive-global-column']
    for name in selected:
        m=next(m for m in supported if m['name']==name);d=raw_fields((ROOT/m['path']).read_bytes())[0];stations=work/(name+' 站点😀.json');write(stations,m['queries']);target=work/(name+' 输出.csv');p=run('node-'+name,['node',binary,ROOT/m['path'],stations,target,'0'])
        summary=json.loads(p.stdout);samples=[legacy(d,q) for q in m['queries']];failures=[(i,sample(d,q)['failure']) for i,q in enumerate(m['queries']) if 'failure' in sample(d,q)]
        assert agrees(summary,{'output':str(target),'selected_index':0,'rows':len(samples),'unavailable':len(failures),'origin':d['origin'],'product':d['product']})
        events=[json.loads(line) for line in p.stderr.splitlines() if line.strip()];assert events==[{'phase':'sample','station_id':m['queries'][i]['id'],'station_index':i,'code':why} for i,why in failures]
        rows=list(csv.reader(io.StringIO(target.read_bytes().decode('utf-8'),newline='')));assert rows[0]==HEADER and len(rows)==len(samples)+1 and all(len(r)==11 for r in rows)
        for row,s in zip(rows[1:],samples,strict=True):
            assert row[0]=='selected-field' and row[1]==s['station']['id'] and agrees([float(row[2]),float(row[3])],[s['station']['latitude'],s['station']['longitude']])
            assert agrees(None if row[4]=='' else float(row[4]),s['value']) and row[5]==s['algorithm'] and list(map(int,row[6:9]))==[0,0,0]
            assert json.loads(row[9])==s['product'] and agrees(json.loads(row[10]),s['contributors'])
    station_file=work/'empty.json';write(station_file,[])
    for m in bad:
        target=work/(m['name']+'.csv');p=run('node-'+m['name'],['node',binary,ROOT/m['path'],station_file,target,'0'],False);assert not p.stdout and not target.exists()
        assert json.loads(p.stderr.splitlines()[0])=={'phase':'decode','code':'invalid-grid','message':m['error']}
    late=work/'late-invalid.grib2';late.write_bytes(fixture+(ROOT/bad[0]['path']).read_bytes());target=work/'late.csv';p=run('node-late-invalid',['node',binary,late,station_file,target,'0'],False);assert not p.stdout and not target.exists()
    assert json.loads(p.stderr.splitlines()[0])=={'phase':'decode','code':'invalid-grid','message':'missing grid increments'}
    target=work/'existing.csv';target.write_bytes(b'KEEP-EXISTING');p=run('node-existing-output',['node',binary,DATA/'point-zero.grib2',station_file,target,'0'],False);assert not p.stdout and target.read_bytes()==b'KEEP-EXISTING'
    node=[c for c in commands if c['command'][0]=='node'];result={'status':'PASS','supportedFieldsPerTarget':43,'all16ScansInEachLineOrientation':True,'negativeGridControlsPerTarget':4,'publicControlSummaryPerTarget':1,'rootTargetedTestsPerTarget':4,
        'targets':['js','wasm-gc'],'dualBackendEquality':True,'fullIndependentPointsSamplesMasksCropsCSV':True,'hand15_45_7_andGlobalPole25':True,'thinDomainNoExtrapolation':True,'positiveLegacyBehaviorAndErrorControls':True,
        'nodeSuccessProcesses':sum(c['expectedSuccess'] for c in node),'nodeExpectedFailureProcesses':sum(not c['expectedSuccess'] for c in node),'targetedTestProcesses':2,'publicBuildRunProcesses':2,'nodeBuildProcesses':1,
        'actualProcessInvocations':len(commands),'oldUnchangedLocalScientificCalendarComparisonOr51SpanSuitesRerun':False,'expectedSHA256':EXPECTED_SHA256}
    write(work/'RESULT.json',result);print(json.dumps(result))


if __name__=='__main__':main()
