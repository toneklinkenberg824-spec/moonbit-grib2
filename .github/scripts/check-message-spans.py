#!/usr/bin/env python3
"""Literal original-byte/message-span contract and unchanged decoder receiver."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'testdata'/'message-spans'
EXPECTED_SHA256='974400b5d489790f7f3aaf630859520b04ceca9c4c415f437f7037632b85dafd'


def load():
    raw=(DATA/'EXPECTED.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256, 'Frozen independent expectations changed'
    expected=json.loads(raw)
    for case in expected['cases']:
        data=bytes.fromhex(case['hex'])
        assert hashlib.sha256(data).hexdigest()==case['sha256']
        if 'spans' in case:
            for span in case['spans']:
                piece=data[span['byte_offset']:span['byte_offset']+span['length']]
                assert len(piece)==span['length'] and piece[:4]==b'GRIB' and piece[-4:]==b'7777'
                assert int.from_bytes(piece[8:16],'big')==span['length']
            assert sum(s['length'] for s in case['spans'])==len(data)
    for name in ('supported','unsupported','mixed-su','mixed-us','multi-field','payload-magic'):
        case=next(c for c in expected['cases'] if c['name']==name)
        assert (DATA/(name+'.grib2')).read_bytes()==bytes.fromhex(case['hex'])
    return expected


def expected_fields(expected, multi=False, local=False):
    first=copy.deepcopy(expected['supported'])
    first['local']=list(bytes.fromhex(expected['payloadLocalHex'])) if local else None
    fields=[first]
    if multi:
        second=copy.deepcopy(first)
        second['values']=expected['secondField']['values']
        second['product']['forecast_time']=12
        second['origin']['field']=1
        fields.append(second)
    return fields


def receiver_expected(expected, raw):
    by_name={c['name']:bytes.fromhex(c['hex']) for c in expected['cases'][:6]}
    if raw==by_name['unsupported']:
        result={'error':expected['unsupportedError']}
        return result,result
    if raw==by_name['supported']:
        fields=expected_fields(expected)
    elif raw==by_name['multi-field']:
        fields=expected_fields(expected,multi=True)
    elif raw==by_name['payload-magic']:
        fields=expected_fields(expected,local=True)
    else:
        return None,None
    return {'fields':fields},({'field':fields[0]} if len(fields)==1 else {'error':expected['multiReadMessageError']})


def validate_before(records,expected):
    cases=expected['cases'][:6]
    assert [r['case'] for r in records]==[c['name'] for c in cases]
    section_counts={'supported':[6],'unsupported':[6],'mixed-su':[6,6],'mixed-us':[6,6],'multi-field':[10],'payload-magic':[7]}
    for record,case in zip(records,cases):
        data=bytes.fromhex(case['hex'])
        assert len(record['technicalMessages'])==len(case['spans'])
        for row,span,sections in zip(record['technicalMessages'],case['spans'],section_counts[case['name']]):
            original=data[span['byte_offset']:span['byte_offset']+span['length']]
            assert row['byte_offset']==span['byte_offset'] and row['length']==span['length']
            assert row['rawExact'] is True and bytes(row['raw'])==original
            assert row['sections']==sections and row['submessages']==(2 if case['name']=='multi-field' else 1)
            assert row['edition']==2 and row['discipline']==0
            decoded,one=receiver_expected(expected,original)
            assert row['decoded']==decoded,(case['name'],row['decoded'],decoded)
            assert row['one']==one
        if case['name'].startswith('mixed') or case['name']=='unsupported':
            assert record['whole']=={'error':expected['unsupportedError']}
        else:
            assert record['whole']==receiver_expected(expected,data)[0]


def validate_after(records,expected):
    assert [r['case'] for r in records]==[c['name'] for c in expected['cases']]
    for record,case in zip(records,expected['cases']):
        if 'error' in case:
            assert record=={'case':case['name'],'error':case['error']},(case['name'],record,case['error'])
            continue
        assert record['spans']==case['spans']
        assert len(record['receivers'])==len(case['spans'])
        data=bytes.fromhex(case['hex'])
        for receiver,span in zip(record['receivers'],case['spans']):
            assert set(span)=={'index','byte_offset','length','edition','discipline'}
            original=data[span['byte_offset']:span['byte_offset']+span['length']]
            assert receiver['span']==span and bytes(receiver['raw'])==original
            decoded,one=receiver_expected(expected,original)
            if decoded is None:
                assert receiver['decoded']['error']['kind']=='corrupted-bitstream'
                assert receiver['one']['error']['kind']=='corrupted-bitstream'
            else:
                assert receiver['decoded']==decoded,(case['name'],receiver['decoded'],decoded)
                assert receiver['one']==one
                # Selected slice Origins are always local, independent of original span offset/index.
                if 'fields' in decoded:
                    for field in receiver['decoded']['fields']:
                        assert field['origin']['message']==field['origin']['byte_offset']==0
        if case['name'] in ('mixed-su','mixed-us','unsupported'):
            assert record['whole']=={'error':expected['unsupportedError']}
        elif receiver_expected(expected,data)[0] is not None:
            assert record['whole']==receiver_expected(expected,data)[0]
        else:
            assert record['whole']['error']['kind']=='corrupted-bitstream'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--moon',default='moon')
    parser.add_argument('--before',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    expected=load()
    args.output.mkdir(parents=True,exist_ok=True)
    if args.before:
        records=[json.loads(s) for s in args.before.read_text(encoding='utf-8').splitlines()]
        validate_before(records,expected)
        result={'status':'PASS','mode':'existing_routes_before','cases':6,'mixedWholeReadErrorPreserved':True,'technicalPublicInternalContextsAndExactRaw':True,'handDecoderValuesMasksProductsOrigins':True}
    else:
        source=(ROOT/'cmd'/'message-spans'/'main.mbt').read_text(encoding='utf-8')
        literals=re.findall(r'inspect\(\s*"([^"]+)"\s*,\s*b"((?:\\x[0-9a-f]{2})*)"\s*,?\s*\)',source)
        assert len(literals)==len(expected['cases'])
        for (name,literal),case in zip(literals,expected['cases']):
            assert name==case['name'] and literal.replace('\\x','')==case['hex']
        outputs=[]
        commands=[]
        for target in ('js','wasm-gc'):
            command=[args.moon,'run','cmd/message-spans','--target',target]
            p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
            (args.output/(target+'.stdout.jsonl')).write_text(p.stdout,encoding='utf-8')
            (args.output/(target+'.stderr.txt')).write_text(p.stderr,encoding='utf-8')
            commands.append({'command':command,'exitCode':p.returncode})
            assert p.returncode==0,target+' public receiver failed'
            records=[json.loads(s) for s in p.stdout.splitlines()]
            validate_after(records,expected)
            outputs.append(records)
        assert outputs[0]==outputs[1]
        result={'status':'PASS','targets':['js','wasm-gc'],'casesPerTarget':len(expected['cases']),'actualConsumerInvocations':2,'frozenExpectedSHA256':EXPECTED_SHA256,'exactOriginalByteSlices':True,'unsignedLengthAndSectionBounds':True,'handDecoderValuesMasksProductsOrigins':True,'oldFullReadUnsupportedAndOneFieldErrors':True,'localOriginWithOriginalSpanContext':True,'semanticInvalidFramingAcceptedButOldDecoderRejects':True,'noPartialSuccess':True,'commands':commands}
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':
    main()
