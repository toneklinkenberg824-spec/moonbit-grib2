"""External query recipes, order-stable real files and pre-write selection."""
import argparse
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'testdata/request-file'
EXPECTED_SHA256='a701120af92c875b467c14482642acab4419cde46d575f62a2a4876be60085b4'
HEADER=['request_key','station_id','latitude','longitude','value','algorithm','message','field','byte_offset','product_json','contributors_json']


def sha(data):return hashlib.sha256(data).hexdigest()


def write(path,value,bom=False):
    path.write_text(('\ufeff' if bom else '')+json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


class Acceptance:
    def __init__(self,args):
        self.args=args;self.work=args.work.resolve();assert not self.work.exists(),'Use a fresh work directory; failures are retained'
        self.work.mkdir(parents=True);(self.work/'logs').mkdir();self.commands=[]
        raw=(DATA/'EXPECTED.json').read_bytes();assert sha(raw)==EXPECTED_SHA256;self.expected=json.loads(raw)
        pieces=[]
        for item in self.expected['weather']:
            data=(ROOT/item['path']).read_bytes();assert len(data)==item['bytes'] and sha(data)==item['sha256'];pieces.append(data)
        self.weather={}
        for item in self.expected['weatherOrders']:
            path=self.work/(item['name']+' 原报😀.grib2');path.write_bytes(b''.join(pieces[i] for i in item['parts']));self.weather[item['name']]=path
        self.catalogue=ROOT/self.expected['cataloguePath'];assert sha(self.catalogue.read_bytes())==self.expected['catalogueSHA256']

    def run(self,name,command,success=True):
        p=subprocess.run(list(map(str,command)),cwd=self.work,capture_output=True)
        label=f'{len(self.commands):02d}-'+name;(self.work/'logs'/(label+'.stdout')).write_bytes(p.stdout);(self.work/'logs'/(label+'.stderr')).write_bytes(p.stderr)
        self.commands.append({'label':name,'command':list(map(str,command)),'exitCode':p.returncode,'expectedSuccess':success})
        write(self.work/'COMMANDS.json',self.commands)
        assert (p.returncode==0)==success,(name,p.stderr.decode('utf-8',errors='replace')[:2200])
        return p

    def build(self):
        modules=[]
        for folder,example in [('receiver','node-request-file'),('legacy','node-file17')]:
            module=self.work/folder;module.mkdir()
            for name in ('main.mbt','moon.mod','moon.pkg','pkg.generated.mbti'):
                source=ROOT/'examples'/example/name
                if source.exists():shutil.copyfile(source,module/name)
            modules.append(module)
        (self.work/'moon.work').write_text('members = '+json.dumps([str(ROOT),*[str(m) for m in modules]])+'\n',encoding='utf-8')
        for module in modules:self.run('build-'+module.name,[self.args.moon,'-C',module,'build','--target','js'])
        self.binaries=[]
        for module in modules:
            name=re.search(r'^name\s*=\s*"([^"]+)"',(module/'moon.mod').read_text(encoding='utf-8'),re.M)[1]
            path=self.work/'_build/js/debug/build'/name/(name.split('/')[-1]+'.js');assert path.is_file();self.binaries.append(path)
        self.receiver,self.legacy=self.binaries

    def csv(self,path):
        rows=list(csv.reader(io.StringIO(path.read_bytes().decode('utf-8'),newline='')));assert rows[0]==HEADER and all(len(r)==11 for r in rows)
        return rows[1:]

    def call(self,name,requests,stations,source=None,error=None,raw_requests=None,existing=False,bom=False):
        recipe=self.work/(name+' requests.json');station_file=self.work/(name+' stations.json');output=self.work/(name+' 输出.csv')
        if raw_requests is None:write(recipe,requests,bom)
        else:recipe.write_text(raw_requests,encoding='utf-8')
        write(station_file,stations,bom)
        if existing:output.write_bytes(b'EXISTING-CSV-DO-NOT-CHANGE')
        before=output.read_bytes() if output.exists() else None
        p=self.run(name,['node',self.receiver,source or self.weather['weather-a'],recipe,station_file,output],error is None)
        if error is not None:
            assert not p.stdout
            assert json.loads(p.stderr.decode('utf-8').splitlines()[0])==error,(name,p.stderr)
            assert (output.read_bytes() if output.exists() else None)==before
            return None,None,None
        assert p.stderr==b''
        summary=json.loads(p.stdout);rows=self.csv(output)
        assert summary['output']==str(output) and summary['request_count']==len(requests) and summary['station_count']==len(stations)
        assert summary['row_count']==len(rows)==len(requests)*len(stations)
        assert summary['unavailable']==sum(r[4]=='' for r in rows)
        assert [g['key'] for g in summary['groups']]==[r['key'] for r in requests]
        assert [r[0] for r in rows]==[r['key'] for r in requests for _ in stations]
        assert [r[1] for r in rows]==[s['id'] for _ in requests for s in stations]
        for index,row in enumerate(rows):
            group=summary['groups'][index//len(stations)];assert row[6:9]==[str(group['origin'][k]) for k in ('message','field','byte_offset')]
            assert json.loads(row[9])==group['product'];assert isinstance(json.loads(row[10]),list)
        return summary,rows,output

    def before(self):
        stations=self.work/'legacy-stations.json';write(stations,self.expected['weatherStations']);observed=[]
        for order in self.expected['weatherOrders']:
            target=self.work/(order['name']+' legacy.csv')
            self.run('old-index0-'+order['name'],['node',self.legacy,self.weather[order['name']],stations,target,'0'])
            rows=self.csv(target);values=[None if r[4]=='' else float(r[4]) for r in rows]
            expected=[253.6234765625,None] if order['parts'][0]==0 else [None,239.85598754882812]
            assert values==expected and {json.loads(r[9])['centre'] for r in rows}=={7 if order['parts'][0]==0 else 98}
            observed.append({'order':order['name'],'numericIndex':0,'values':values})
        write(self.work/'BEFORE.json',{'status':'PASS','productionBugClaimed':False,'existingAPICompositionAcknowledged':True,'oldNumericIndexIntentionalOrderDependence':observed,'noExistingExternalNamedRecipeReceiverFound':True})

    def after(self):
        req=self.expected['weatherRequests'];stations=self.expected['weatherStations']
        for order in self.expected['weatherOrders']:
            summary,rows,_=self.call(order['name'],req,stations,source=self.weather[order['name']],bom=True)
            assert [None if r[4]=='' else float(r[4]) for r in rows]==self.expected['weatherValues']
            assert [g['origin'] for g in summary['groups']]==order['origins']
            assert [json.loads(r[9])['centre'] for r in rows]==[7,7,98,98]
        cat_req=self.expected['catalogueRequests'];cat_st=[self.expected['catalogueStation']]
        summary,rows,_=self.call('all-raw-filters',cat_req,cat_st,source=self.catalogue)
        assert [float(r[4]) for r in rows]==[101,202,303,404,606]
        assert [g['origin'] for g in summary['groups']]==self.expected['catalogueOrigins']
        assert json.loads(rows[2][9])['first_surface']=={'kind':100,'scale':0,'scaled_value':85000}
        assert json.loads(rows[3][9])['first_surface']=={'kind':100,'scale':1,'scaled_value':850000}
        assert 'forecast_time' not in json.loads(rows[0][9]) and json.loads(rows[1][9])['forecast_time']==0
        assert json.loads(rows[4][9])['time_unit']==0 and json.loads(rows[4][9])['forecast_time']==360
        negative=[{'key':'negative','query':{'discipline':0,'category':0,'parameter':0,'forecast_time':-6}}]
        _,negative_rows,_=self.call('negative-lead',negative,cat_st,source=ROOT/'testdata/inventory24/forecast.grib2')
        assert float(negative_rows[0][4])==444 and json.loads(negative_rows[0][9])['forecast_time']==-6
        _,empty_rows,_=self.call('no-requests',[],stations);assert empty_rows==[]
        summary,empty_rows,_=self.call('no-stations',req,[]);assert empty_rows==[] and len(summary['groups'])==2
        _,rows,_=self.call('nonfinite-station',req,[{'id':'NaN-station','latitude':'NaN','longitude':31.5}]);assert [r[4] for r in rows]==['',''] and [r[2] for r in rows]==['NaN','NaN']
        request_error={'phase':'requests','code':'invalid-request-file'}
        invalid=[('top-object',{}),('item-null',[None]),('missing-key',[{'query':req[0]['query']}]),('missing-query',[{'key':'x'}]),('query-null',[{'key':'x','query':None}]),
                 ('missing-id',[{'key':'x','query':{'discipline':0,'category':0}}]),('fractional-id',[{'key':'x','query':{'discipline':0.5,'category':0,'parameter':0}}]),
                 ('overflow-id',[{'key':'x','query':{'discipline':2147483648,'category':0,'parameter':0}}]),('unknown-request',[{**req[0],'extra':0}]),
                 ('unknown-query',[{'key':'x','query':{**req[0]['query'],'centree':7}}]),('unknown-surface',[{'key':'x','query':{**req[0]['query'],'first_surface':{'kind':103,'extra':1}}}]),
                 ('surface-no-kind',[{'key':'x','query':{**req[0]['query'],'first_surface':{'scale':0}}}]),('negative-uint',[{'key':'x','query':{**req[0]['query'],'first_surface':{'kind':103,'scaled_value':-1}}}]),
                 ('fractional-scale',[{'key':'x','query':{**req[0]['query'],'first_surface':{'kind':103,'scale':0.5}}}]),
                 ('fractional-uint',[{'key':'x','query':{**req[0]['query'],'first_surface':{'kind':103,'scaled_value':2.5}}}]),
                 ('fractional-time',[{'key':'x','query':{**req[0]['query'],'forecast_time':0.5}}]),
                 ('fractional-reference',[{'key':'x','query':{**req[0]['query'],'reference_time':[2007,3,23,12,0,0.5]}}]),
                 ('boolean-time',[{'key':'x','query':{**req[0]['query'],'forecast_time':False}}]),('reference-type',[{'key':'x','query':{**req[0]['query'],'reference_time':'2007'}}])]
        for name,value in invalid:self.call(name,value,stations,source=self.work/'nonexistent-data.grib2',error=request_error)
        self.call('syntax-invalid',None,stations,raw_requests='[',error=request_error)
        selection=lambda message:{'phase':'selection','code':'invalid-field-request','message':message}
        self.call('empty-key',[{'key':'','query':req[0]['query']}],stations,error=selection('request key must be nonempty'))
        self.call('duplicate-key',[req[0],req[0]],stations,error=selection('duplicate request key: '+req[0]['key']))
        self.call('late-missing',[req[0],{'key':'late','query':{**req[0]['query'],'centre':99}}],stations,error=selection('late: no field matches query'),existing=True)
        self.call('omitted-time-ambiguous',[{'key':'any','query':{'discipline':0,'category':0,'parameter':0}}],cat_st,source=self.catalogue,error=selection('any: query matches multiple fields'))
        self.call('late-ambiguous',[cat_req[0],{'key':'any','query':{'discipline':0,'category':0,'parameter':0}}],cat_st,source=self.catalogue,error=selection('any: query matches multiple fields'))
        self.call('invalid-reference',[{'key':'bad-ref','query':{**req[0]['query'],'reference_time':[2007,3,23]}}],stations,error=selection('bad-ref: reference_time must contain six components'))
        self.call('invalid-reference-no-stations',[{'key':'bad-ref','query':{**req[0]['query'],'reference_time':[2007]}}],[],error=selection('bad-ref: reference_time must contain six components'))
        self.call('uint32-accepted-no-match',[{'key':'full-u32','query':{'discipline':0,'category':0,'parameter':0,'first_surface':{'kind':100,'scale':0,'scaled_value':4294967295}}}],cat_st,source=self.catalogue,error=selection('full-u32: no field matches query'))
        self.call('no-time-conversion',[{'key':'minutes','query':{'discipline':0,'category':0,'parameter':1,'time_unit':1,'forecast_time':6}}],cat_st,source=self.catalogue,error=selection('minutes: no field matches query'))
        self.call('wrong-unit-same-lead',[{'key':'unit','query':{'discipline':0,'category':0,'parameter':1,'time_unit':1,'forecast_time':360}}],cat_st,source=self.catalogue,error=selection('unit: no field matches query'))
        for key,value in [('subcentre',1),('master_table',99),('local_table',1),('time_unit',9),('second_surface',{'kind':1})]:
            query=copy.deepcopy(cat_req[3]['query']);query[key]=value
            self.call('wrong-'+key,[{'key':'wrong','query':query}],cat_st,source=self.catalogue,error=selection('wrong: no field matches query'))
        query=copy.deepcopy(cat_req[2]['query']);query['first_surface']['scale']=None
        self.call('surface-missing-scale',[{'key':'raw-none','query':query}],cat_st,source=self.catalogue,error=selection('raw-none: no field matches query'))
        unsupported=ROOT/'testdata/message-spans/unsupported.grib2'
        self.call('old-decode-error',req,stations,source=unsupported,error={'phase':'decode','code':'unsupported-template','section':3,'template':1})
        recipe=self.work/'valid-requests.json';station_file=self.work/'valid-stations.json';write(recipe,req);write(station_file,stations)
        target=self.work/'protected.csv';target.write_bytes(b'EXISTING')
        p=self.run('existing-output',['node',self.receiver,self.weather['weather-a'],recipe,station_file,target],False);assert not p.stdout and target.read_bytes()==b'EXISTING'
        p=self.run('missing-input',['node',self.receiver,self.work/'missing.grib2',recipe,station_file,self.work/'missing.csv'],False);assert not p.stdout and not (self.work/'missing.csv').exists()
        p=self.run('usage',['node',self.receiver],False);assert not p.stdout


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--moon',default='moon');parser.add_argument('--work',type=Path,required=True);args=parser.parse_args()
    tests=Acceptance(args);tests.build();tests.before();tests.after()
    commands=tests.commands
    result={'status':'PASS','runtimeTarget':'Node/JS','newReceiverProcesses':sum('grib2-request-file.js' in ' '.join(c['command']) for c in commands),'oldNumericReceiverProcesses':2,'buildProcesses':2,
            'orderStableNamedQueries':True,'elevenColumnExternalCSVReadback':True,'omissionNullZeroDistinguished':True,'allRawFiltersAndSurfaceEncodings':True,'atomicSelectionAndOutputGuards':True,
            'sameStationNonfinitePolicy':True,'frozenExpectedSHA256':EXPECTED_SHA256,'oldUnchangedLocalSuitesOrReferencesRerun':False}
    write(tests.work/'RESULT.json',result);print(json.dumps(result))


if __name__=='__main__':main()
