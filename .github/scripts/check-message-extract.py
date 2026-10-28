"""Real filesystem delivery -> existing inventory/CSV receiver acceptance."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'testdata/message-extract'
EXPECTED_SHA256='cef22924e90b323d5bd8483215d32a1fc8a385d5de94f65897d31c97c9faeb91'


def digest(data):return hashlib.sha256(data).hexdigest()


def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


class Checks:
    def __init__(self,args):
        self.args=args;self.work=args.work;self.commands=[]
        assert not self.work.exists(), 'Use a fresh acceptance directory; old failures are retained'
        self.work.mkdir(parents=True);(self.work/'logs').mkdir()
        raw=(DATA/'EXPECTED.json').read_bytes();assert digest(raw)==EXPECTED_SHA256
        self.expected=json.loads(raw);self.parts=[]
        for part in self.expected['parts']:
            content=(ROOT/part['path']).read_bytes();assert len(content)==part['length'] and digest(content)==part['sha256'];self.parts.append(content)
        self.mixed=b''.join(self.parts);assert len(self.mixed)==961 and digest(self.mixed)==self.expected['mixedSHA256']
        self.source=self.work/'混合 原文件😀.grib2';self.source.write_bytes(self.mixed)
        self.stations=self.work/'stations.json';write(self.stations,self.expected['stations'])

    def run(self,label,command,success=True,extra_env=None):
        environment=dict(os.environ)
        if extra_env:environment.update(extra_env)
        result=subprocess.run(list(map(str,command)),cwd=self.work,env=environment,capture_output=True)
        prefix=str(len(self.commands)).zfill(2)+'-'+label
        (self.work/'logs'/(prefix+'.stdout')).write_bytes(result.stdout)
        (self.work/'logs'/(prefix+'.stderr')).write_bytes(result.stderr)
        self.commands.append({'label':label,'command':list(map(str,command)),'exitCode':result.returncode,'expectedSuccess':success})
        write(self.work/'COMMANDS.json',self.commands)
        assert (result.returncode==0)==success,(label,result.stderr.decode('utf-8',errors='replace')[:2000])
        assert self.source.read_bytes()==self.mixed,'Input was changed'
        return result

    def build(self,example,name):
        module=self.work/name;module.mkdir()
        for filename in ('main.mbt','moon.mod','moon.pkg','pkg.generated.mbti'):
            source=ROOT/'examples'/example/filename
            if source.exists():shutil.copyfile(source,module/filename)
        return module

    def binary(self,module):
        name=re.search(r'^name\s*=\s*"([^"]+)"',(module/'moon.mod').read_text(encoding='utf-8'),re.M)[1]
        result=self.work/'_build/js/debug/build'/name/(name.split('/')[-1]+'.js')
        assert result.is_file();return result

    def hosts(self):
        modules=[]
        if self.args.reuse_hosts:
            prior=self.args.reuse_hosts
            identity=json.loads((prior/'HOSTS.json').read_text(encoding='utf-8'))
            for name,sha in identity['dependencySourceSHA256'].items():assert digest((ROOT/name).read_bytes())==sha,name
            for kind,example in [('inventory','node-inventory24'),('sampler','node-file17')]:
                for filename in ('main.mbt','moon.mod','moon.pkg'):
                    assert (prior/kind/filename).read_bytes()==(ROOT/'examples'/example/filename).read_bytes()
            self.inventory=Path(identity['inventory']);self.sampler=Path(identity['sampler'])
            for kind in ('inventory','sampler'):assert digest(Path(identity[kind]).read_bytes())==identity[kind+'SHA256']
        else:
            self.inventory_module=self.build('node-inventory24','inventory');self.sampler_module=self.build('node-file17','sampler')
            modules += [self.inventory_module,self.sampler_module]
        if not self.args.before_only:
            self.extractor_module=self.build('node-message-extract','extractor');modules.append(self.extractor_module)
        (self.work/'moon.work').write_text('members = '+json.dumps([str(ROOT),*[str(m) for m in modules]])+'\n',encoding='utf-8')
        for module in modules:self.run('build-'+module.name,[self.args.moon,'-C',module,'build','--target','js'])
        if not self.args.reuse_hosts:
            self.inventory=self.binary(self.inventory_module);self.sampler=self.binary(self.sampler_module)
            dependency={}
            for path in ROOT.rglob('*'):
                if '_build' in path.parts or 'target' in path.parts or not path.is_file():continue
                if path.suffix in ('.mbt','.mbti') or path.name in ('moon.mod','moon.pkg'):
                    dependency[str(path.relative_to(ROOT))]=digest(path.read_bytes())
            write(self.work/'HOSTS.json',{'inventory':str(self.inventory),'sampler':str(self.sampler),'inventorySHA256':digest(self.inventory.read_bytes()),'samplerSHA256':digest(self.sampler.read_bytes()),'dependencySourceSHA256':dependency})
        if not self.args.before_only:self.extractor=self.binary(self.extractor_module)

    def before(self):
        expected={'phase':'decode','code':'unsupported-template','section':3,'template':1}
        a=self.run('old-inventory-mixed',['node',self.inventory,self.source],False)
        assert not a.stdout and json.loads(a.stderr.decode().splitlines()[0])==expected
        target=self.work/'old-cannot-produce.csv'
        b=self.run('old-sampler-mixed',['node',self.sampler,self.source,self.stations,target,'1'],False)
        assert not b.stdout and json.loads(b.stderr.decode().splitlines()[0])==expected and not target.exists()
        write(self.work/'BEFORE.json',{'status':'PASS','newMixedInputBytes':961,'existingFullDecoderBoundary':expected,'rawFileExtractorFoundBefore':False,'oldConsumerErrorPreserved':True,'newOutputNotCreated':True})

    def extract(self,name,index,part=None,source=None,output=None,success=True,event=None,node_options=None,extra_env=None):
        source=source or self.source;output=output or (self.work/(name+' 输出😀.grib2'))
        existed=output.exists()
        before=output.read_bytes() if output.is_file() else None
        result=self.run(name,['node',*(node_options or []),self.extractor,source,output,index],success,extra_env)
        if success:
            expected=self.expected['parts'][part];data=self.parts[part];summary=json.loads(result.stdout)
            assert result.stderr==b''
            assert summary=={'input':str(source),'output':str(output),'span':expected['span'],'bytes_written':len(data),'input_sha256':digest(source.read_bytes()),'output_sha256':digest(data)}
            assert output.read_bytes()==data
        else:
            assert not result.stdout
            if event:assert json.loads(result.stderr.decode().splitlines()[0])==event
            if before is not None:assert output.read_bytes()==before
            elif existed:assert output.is_dir() and not list(output.iterdir())
            elif not extra_env:assert not output.exists()
        return output

    def receiver(self,name,output,part):
        listing=self.run(name+'-inventory',['node',self.inventory,output])
        data=json.loads(listing.stdout)
        assert data['field_count']==(2 if part==3 else 1)
        for field in data['fields']:assert field['origin']['message']==field['origin']['byte_offset']==0
        return data

    def after(self):
        outputs={i:self.extract('part-'+str(i),str(i),part=i) for i in range(4)}
        for token in ('+1','01','0x1','0b1','0o1','0_1'):self.extract('grammar-'+token,token,part=1)
        a=self.run('unsupported-receiver',['node',self.inventory,outputs[0]],False)
        assert not a.stdout and json.loads(a.stderr.decode().splitlines()[0])=={'phase':'decode','code':'unsupported-template','section':3,'template':1}
        for i in (1,2,3):self.receiver('part-'+str(i),outputs[i],i)
        for sample in self.expected['samples']:
            stations=self.work/('sample-'+str(sample['part'])+'.json');write(stations,[self.expected['stations'][sample['station']]])
            csv_path=self.work/('sample-'+str(sample['part'])+'.csv')
            self.run('real-file-to-csv-'+str(sample['part']),['node',self.sampler,outputs[sample['part']],stations,csv_path,'0'])
            rows=list(csv.reader(io.StringIO(csv_path.read_text(encoding='utf-8'))));assert len(rows)==2 and all(len(row)==11 for row in rows)
            row=rows[1];assert abs(float(row[4])-sample['value'])<1e-10 and row[6:9]==['0','0','0']
            assert json.loads(row[9])['centre']==sample['centre']
        stations=self.work/'multi-station.json';write(stations,[self.expected['multiStation']]);csv_path=self.work/'multi.csv'
        self.run('multi-field-to-csv',['node',self.sampler,outputs[3],stations,csv_path,'1'])
        rows=list(csv.reader(io.StringIO(csv_path.read_text(encoding='utf-8'))));assert len(rows)==2 and len(rows[1])==11
        assert float(rows[1][4])==6 and rows[1][6:9]==['0','1','0'] and json.loads(rows[1][9])['forecast_time']==12
        for i,token in enumerate(('bad','1.5','','2147483648')):
            self.extract('invalid-index-'+str(i),token,source=self.work/'nonexistent-input',success=False,event={'phase':'selection','code':'invalid-message-index','argument':'MESSAGE_INDEX'})
        for token in ('-1','4','2147483647'):
            self.extract('range-'+token,token,success=False,event={'phase':'selection','code':'message-index-out-of-range','message_count':4})
        for name,payload,code,offset in [('empty',b'','empty-input',0),('garbage',b'x','invalid-magic',0),('late',self.mixed+b'?','invalid-magic',961)]:
            source=self.work/(name+'.input');source.write_bytes(payload)
            self.extract(name,'1',source=source,success=False,event={'phase':'framing','code':code,'byte_offset':offset})
        sentinel=self.work/'existing.grib2';sentinel.write_bytes(b'EXISTING-DO-NOT-CHANGE')
        self.extract('existing-output','1',output=sentinel,success=False)
        self.extract('same-input-output','1',output=self.source,success=False)
        self.extract('missing-input','1',source=self.work/'missing.input',success=False)
        self.extract('missing-parent','1',output=self.work/'absent-parent'/'out.grib2',success=False)
        directory=self.work/'directory-output';directory.mkdir()
        self.extract('directory-output','1',output=directory,success=False)
        for args in ([],[str(self.source)],[str(self.source),'unused','1','extra']):
            result=self.run('usage-'+str(len(args)),['node',self.extractor,*args],False);assert not result.stdout
        bad=self.work/'late.input'
        self.extract('late-preserves-existing','1',source=bad,output=sentinel,success=False,event={'phase':'framing','code':'invalid-magic','byte_offset':961})
        preload=self.work/'readback-fault.cjs'
        preload.write_text("const fs=require('node:fs');const read=fs.readFileSync;fs.readFileSync=function(path,...args){const value=read.call(this,path,...args);if(String(path)===process.env.GRIB2_TEST_READBACK){const copy=Buffer.from(value);copy[0]^=1;return copy;}return value;};\n",encoding='utf-8')
        target=self.work/'readback-fault.grib2'
        self.extract('readback-mismatch','1',output=target,success=False,event={'phase':'verification','code':'output-readback-mismatch'},node_options=['--require',str(preload)],extra_env={'GRIB2_TEST_READBACK':str(target)})
        assert target.read_bytes()==self.parts[1]
        assert self.source.read_bytes()==self.mixed and sentinel.read_bytes()==b'EXISTING-DO-NOT-CHANGE'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--moon',default='moon');parser.add_argument('--work',type=Path,required=True);parser.add_argument('--before-only',action='store_true');parser.add_argument('--reuse-hosts',type=Path)
    args=parser.parse_args();args.work=args.work.resolve()
    if args.reuse_hosts:args.reuse_hosts=args.reuse_hosts.resolve()
    checks=Checks(args);checks.hosts()
    if args.before_only:checks.before();result={'status':'PASS','mode':'before','processInvocations':len(checks.commands),'before':'BEFORE.json'}
    else:
        if not args.reuse_hosts:checks.before()
        checks.after();result={'status':'PASS','mode':'file_delivery','runtimeTarget':'js','newExtractorProcesses':sum('grib2-message-extract.js' in ' '.join(c['command']) for c in checks.commands),'totalProcessInvocations':len(checks.commands),'exactFileBytesAndSHA256':True,'readbackRequiredBeforeSuccess':True,'originalSpanAndSliceLocalOrigin':True,'realNOAAIFSAndMultiFieldReceivers':True,'existingTargetsAndInputPreserved':True,'frozenExpectedSHA256':EXPECTED_SHA256}
    write(args.work/'RESULT.json',result)
    print(json.dumps(result))


if __name__=='__main__':main()
