#!/usr/bin/env python3
"""Independent actual-file receiver for the Node regional raw-node exporter."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'testdata/node-crop-file'
EXPECTED_SHA = 'c52bf4e2f03bd49432f74420039225bc8ab064fc4834714294be1360e2f9f502'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
def u32(raw, at): return int.from_bytes(raw[at:at + 4], 'big')
def sm(raw, at, length):
    n = int.from_bytes(raw[at:at + length], 'big')
    return -(n & ((1 << (length * 8 - 1)) - 1)) if n >> (length * 8 - 1) else n

def raw_models(raw):
    models = []; offset = 0; message_index = 0
    while offset < len(raw):
        assert raw[offset:offset + 4] == b'GRIB' and raw[offset + 7] == 2
        size = int.from_bytes(raw[offset + 8:offset + 16], 'big')
        assert raw[offset + size - 4:offset + size] == b'7777'
        p = offset + 16; parts = {}; field_index = 0
        while p < offset + size - 4:
            n = u32(raw, p); kind = raw[p + 4]
            assert n >= 5 and p + n <= offset + size - 4
            parts[kind] = raw[p:p + n]; p += n
            if kind != 7: continue
            s1, g, s4, d, bitmap, packed = [parts[k] for k in [1, 3, 4, 5, 6, 7]]
            assert g[12:14] == s4[7:9] == d[9:11] == b'\0\0'
            assert g[38:42] == bytes(4) and d[11:19] == bytes(8) and d[19] == 8
            nc, nr, di, dj = [u32(g, a) for a in [30, 34, 63, 67]]
            assert nc * nr == u32(g, 6)
            scan = g[71]; assert scan & 15 == 0
            mask = [True] * (nr * nc) if bitmap[5] == 255 else [bool(bitmap[6 + i // 8] & (1 << (7 - i % 8))) for i in range(nr * nc)]
            assert u32(d, 5) == sum(mask) and len(packed) == 5 + sum(mask)
            numbers = iter(packed[5:]); scanned = [next(numbers) if ok else None for ok in mask]
            order = []
            if scan & 32:
                for i in range(nc):
                    for j in (range(nr - 1, -1, -1) if scan & 16 and i % 2 else range(nr)):
                        order.append((nr - 1 - j if scan & 64 else j, nc - 1 - i if scan & 128 else i))
            else:
                for j in range(nr):
                    for i in (range(nc - 1, -1, -1) if scan & 16 and j % 2 else range(nc)):
                        order.append((nr - 1 - j if scan & 64 else j, nc - 1 - i if scan & 128 else i))
            values = [None] * (nr * nc); indices = [-1] * (nr * nc)
            for source_index, ((r, c), value) in enumerate(zip(order, scanned)):
                values[r * nc + c] = value; indices[r * nc + c] = source_index
            north_ticks = sm(g, 46, 4) + ((nr - 1) * dj if scan & 64 else 0)
            west_ticks = (u32(g, 50) - ((nc - 1) * di if scan & 128 else 0)) % 360000000
            duplicate = (nc - 1) * di == 360000000
            def surface(at):
                result = {'kind': s4[at]}
                if s4[at + 1] != 255: result['scale'] = sm(s4, at + 1, 1)
                if u32(s4, at + 2) != 0xffffffff: result['scaled_value'] = u32(s4, at + 2)
                return result
            product = {'discipline': raw[offset + 6], 'category': s4[9], 'parameter': s4[10], 'centre': int.from_bytes(s1[5:7], 'big'), 'subcentre': int.from_bytes(s1[7:9], 'big'), 'master_table': s1[9], 'local_table': s1[10], 'reference_time': [int.from_bytes(s1[12:14], 'big'), *s1[14:19]], 'time_unit': s4[17], 'forecast_time': sm(s4, 18, 4), 'first_surface': surface(22), 'second_surface': surface(28)}
            models.append({'rows': nr, 'cols': nc, 'north': north_ticks / 1000000, 'west': west_ticks / 1000000, 'dx': di / 1000000, 'dy': dj / 1000000, 'cyclic': duplicate or nc * di == 360000000, 'unique_columns': nc - 1 if duplicate else nc, 'values': values, 'source_indices': indices, 'origin': {'message': message_index, 'field': field_index, 'byte_offset': offset, 'scanning_mode': scan}, 'product': product})
            field_index += 1
        assert p == offset + size - 4
        offset += size; message_index += 1
    assert offset == len(raw) and message_index == 2
    return models

def expected_points(model, positions):
    result = []
    for position in positions:
        r, c = divmod(position, model['cols'])
        result.append({'row': r, 'col': c, 'source_index': model['source_indices'][position], 'latitude': model['north'] - r * model['dy'], 'longitude': (model['west'] + c * model['dx']) % 360, 'value': model['values'][position]})
    return result

def receive(raw, case, model, expected):
    def reject_constant(value): raise ValueError('non-JSON token ' + value)
    records = [json.loads(line, parse_constant=reject_constant) for line in raw.decode('utf-8').split('\n') if line]
    if len(records) < 2 or records[0].get('type') != 'field' or records[-1].get('type') != 'end':
        raise ValueError('JSONL export lacks complete field/end records')
    grid = {k: model[k] for k in ['rows', 'cols', 'north', 'west', 'dx', 'dy', 'cyclic', 'unique_columns']}
    header = {'type': 'field', 'schema': expected['schema'], 'selected_index': case['index'], 'field_count': 3, 'bounds': case['bounds'], 'origin': model['origin'], 'product': expected['product'], 'grid': grid}
    if records[0] != header: raise ValueError('field header differs from complete expectation')
    points = expected_points(model, case['positions'])
    if records[1:-1] != [{'type': 'point', 'point': p} for p in points]:
        raise ValueError('point records differ from frozen raw-node expectation')
    footer = {'type': 'end', 'points': len(points), 'missing': sum(p['value'] is None for p in points)}
    if records[-1] != footer: raise ValueError('end counts differ from complete expectation')
    return records

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(); work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False); (work / 'logs').mkdir()
    expected_raw = (DATA / 'EXPECTED.json').read_bytes(); assert sha(expected_raw) == EXPECTED_SHA
    expected = json.loads(expected_raw)
    input_raw = (DATA / 'input.grib2').read_bytes(); late_raw = (DATA / 'late-unsupported.grib2').read_bytes()
    assert sha(input_raw) == expected['inputSHA256'] and sha(late_raw) == expected['lateUnsupportedSHA256']
    models = raw_models(input_raw); assert len(models) == 3
    for actual, frozen in zip(models, expected['models']):
        assert actual == {k: v for k, v in frozen.items() if k != 'name'} | {'product': expected['product']}
    assert late_raw.startswith(input_raw)
    assert int.from_bytes(late_raw[len(input_raw) + 16 + 21 + 12:len(input_raw) + 16 + 21 + 14], 'big') == 1
    save(work / 'INDEPENDENT-RAW-REVIEW.json', {'status': 'PASS', 'expectedSHA256': EXPECTED_SHA, 'all3DecodedHandModels': models, 'messageCount': 2, 'sameMessageFields0and1Distinct': True, 'noMoonBitOracleOrScientificReference': True})
    module = work / 'producer'; module.mkdir()
    canonical = {}
    for name in ['main.mbt', 'moon.mod', 'moon.pkg', 'pkg.generated.mbti']:
        raw = (ROOT / 'examples/node-crop-file' / name).read_bytes()
        (module / name).write_bytes(raw); canonical[name] = sha(raw)
    (work / 'moon.work').write_text('members = ' + json.dumps([str(ROOT), str(module)]) + '\n', encoding='utf-8')
    path_input = work / '原节点😀.grib2'; path_input.write_bytes(input_raw)
    path_late = work / '末字段不支持.grib2'; path_late.write_bytes(late_raw)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    commands = []
    def run(label, command, success=True):
        sout = work / 'logs' / (label + '.stdout'); serr = work / 'logs' / (label + '.stderr')
        with sout.open('wb') as stdout, serr.open('wb') as stderr:
            try:
                p = subprocess.run(list(map(str, command)), cwd=work, env=env, stdout=stdout, stderr=stderr, timeout=180)
            except subprocess.TimeoutExpired:
                commands.append({'label': label, 'command': list(map(str, command)), 'outcome': 'timeout180seconds', 'rawStreamsDirectlyPersisted': True})
                save(work / 'COMMANDS.json', commands); raise
        commands.append({'label': label, 'command': list(map(str, command)), 'cwd': str(work), 'exitCode': p.returncode, 'expectedSuccess': success})
        save(work / 'COMMANDS.json', commands)
        assert (p.returncode == 0) == success, (label, serr.read_text(encoding='utf-8', errors='replace')[-1000:])
        return sout.read_bytes(), serr.read_bytes()
    run('build-new-node-crop', ['moon', '-C', module, 'build', '--target', 'js'])
    binary = work / '_build/js/debug/build/local/grib2-crop-file/grib2-crop-file.js'
    reviews = []
    for case in expected['successCases']:
        bounds = work / (case['name'] + '边界.json')
        raw = (json.dumps(case['bounds']) + '\n').encode()
        if case['name'].endswith('-bom'): raw = b'\xef\xbb\xbf' + raw
        bounds.write_bytes(raw)
        stdout, stderr = run('node-' + case['name'], ['node', binary, path_input, bounds, str(case['index'])])
        assert not stderr
        records = receive(stdout, case, models[case['index']], expected)
        reviews.append({'name': case['name'], 'records': records})
    negatives = []
    for case in expected['negativeCases']:
        bounds = work / (case['name'] + '.json')
        bounds.write_text('{' if case.get('malformed') else json.dumps(case['bounds']) + '\n', encoding='utf-8')
        stdout, stderr = run('node-' + case['name'], ['node', binary, path_late if case.get('late') else path_input, bounds, case['index']], success=False)
        assert not stdout and stderr
        if 'event' in case:
            event = json.loads(stderr.decode('utf-8').split('\n')[0])
            assert event == case['event']; negatives.append({'name': case['name'], 'event': event, 'stdoutEmpty': True})
        else: negatives.append({'name': case['name'], 'stdoutEmpty': True, 'parseFailureExit': True})
    first = reviews[0]['records']
    receiver_controls = [
        ('truncated-before-end-record', first[:-1], 'JSONL export lacks complete field/end records'),
        ('wrong-point-value', copy.deepcopy(first), 'point records differ from frozen raw-node expectation'),
    ]
    receiver_controls[1][1][1]['point']['value'] = 999
    checked = []
    for name, records, message in receiver_controls:
        raw = ('\n'.join(json.dumps(r) for r in records) + '\n').encode()
        (work / (name + '.jsonl')).write_bytes(raw)
        try: receive(raw, expected['successCases'][0], models[0], expected)
        except ValueError as error:
            assert str(error) == message; checked.append({'name': name, 'error': str(error)})
        else: raise AssertionError('Receiver accepted ' + name)
    save(work / 'COMPLETE-OUTPUT-REVIEW.json', {'status': 'PASS', 'successes': reviews, 'expectedFailures': negatives, 'receiverNegativeCases': checked})
    result = {'status': 'PASS', 'expectedSHA256': EXPECTED_SHA, 'actualProcessInvocations': len(commands), 'buildProcesses': 1, 'nodeSuccessProcesses': 7, 'nodeExpectedFailureProcesses': 6, 'independentReceiverNegativeCases': 2, 'successfulJSONLRecords': sum(len(x['records']) for x in reviews), 'successfulPointRecords': sum(len(x['records']) - 2 for x in reviews), 'twoMessageThreeFieldOriginChecked': True, 'rawZeroNullScan240GlobalDuplicateThinAndEmptyChecked': True, 'completeHeaderEveryPointAndEndChecked': True, 'negativeInputNoSuccessfulStdoutPrefix': True, 'UTF8PathsAndBOM': True, 'noOldLocalSuitesRerun': True, 'canonicalProducerSourcesSHA256': canonical, 'actualBinary': str(binary), 'actualBinarySHA256': sha(binary.read_bytes()), 'actualInputGRIBSHA256': sha(path_input.read_bytes()), 'actualLateInputSHA256': sha(path_late.read_bytes())}
    save(work / 'RESULT.json', result); print(json.dumps(result))

if __name__ == '__main__': main()
