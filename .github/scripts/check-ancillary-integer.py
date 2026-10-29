#!/usr/bin/env python3
"""Consume real Node station files containing large ancillary JSON integers."""
import argparse
import csv
from decimal import Decimal
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'testdata/ancillary-integer'
HELPER = ROOT / 'examples/node-file17/join_diagnostics.py'
EXPECTED_SHA = 'aa73a1f2647f76d9e36d4e120a5a1161ed5975ef407d3e477b52a7d5d0760558'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def moonbit_sources():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
    return {n: sha((ROOT / n).read_bytes()) for n in names if n.endswith(('.mbt', '.mbti')) or Path(n).name in {'moon.mod', 'moon.pkg'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--consume-from', type=Path)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    logs = work / 'logs'
    logs.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    commands = []
    initial_limit = sys.get_int_max_str_digits()

    def run(label, command, success=True):
        p = subprocess.run(list(map(str, command)), cwd=work, env=env, capture_output=True)
        (logs / (label + '.stdout')).write_bytes(p.stdout)
        (logs / (label + '.stderr')).write_bytes(p.stderr)
        commands.append({'label': label, 'command': list(map(str, command)), 'cwd': str(work), 'exitCode': p.returncode, 'expectedSuccess': success})
        save(work / 'COMMANDS.json', commands)
        assert (p.returncode == 0) == success, (label, p.stderr.decode('utf-8', errors='replace')[-1000:])
        return p

    raw_expected = (DATA / 'EXPECTED.json').read_bytes()
    assert sha(raw_expected) == EXPECTED_SHA
    expected = json.loads(raw_expected)
    raw_stations = (DATA / 'stations.json').read_bytes()
    grib = ROOT / expected['inputGRIB']
    assert sha(raw_stations) == expected['stationsSHA256'] and sha(grib.read_bytes()) == expected['inputGRIBSHA256']
    canonical = {n: sha((ROOT / 'examples/node-file17' / n).read_bytes()) for n in ['main.mbt', 'moon.mod', 'moon.pkg', 'pkg.generated.mbti']}
    sources = moonbit_sources()
    actual_names = ['stations.json', 'output.csv', 'node-ancillary-integer.stdout', 'node-ancillary-integer.stderr']
    if args.consume_from:
        previous = args.consume_from.resolve()
        producer = json.loads((previous / 'PRODUCER.json').read_text(encoding='utf-8'))
        assert producer['status'] == 'PASS' and producer['canonicalNodeSources'] == canonical and producer['allMoonBitSources'] == sources
        assert sha(Path(producer['binary']).read_bytes()) == producer['binarySHA256']
        for name in actual_names:
            raw = (previous / name).read_bytes()
            assert sha(raw) == producer['actualFiles'][name]['rawSHA256']
            (work / name).write_bytes(raw)
        producer = {**producer, 'reusedActualProducerDirectory': str(previous), 'noNodeRebuildOrRerun': True}
    else:
        module = work / 'receiver'
        module.mkdir()
        for name in canonical:
            shutil.copyfile(ROOT / 'examples/node-file17' / name, module / name)
        (work / 'moon.work').write_text('members = ' + json.dumps([str(ROOT), str(module)]) + '\n', encoding='utf-8')
        (work / 'stations.json').write_bytes(raw_stations)
        run('build-unchanged-node', ['moon', '-C', module, 'build', '--target', 'js'])
        binary = work / '_build/js/debug/build/local/grib2-file17/grib2-file17.js'
        p = run('node-ancillary-integer', ['node', binary, grib, work / 'stations.json', work / 'output.csv', '0'])
        (work / 'node-ancillary-integer.stdout').write_bytes(p.stdout)
        (work / 'node-ancillary-integer.stderr').write_bytes(p.stderr)
        producer = {'status': 'PASS', 'canonicalNodeSources': canonical, 'allMoonBitSources': sources, 'binary': str(binary), 'binarySHA256': sha(binary.read_bytes()), 'inputGRIBSHA256': sha(grib.read_bytes()), 'actualFiles': {n: {'rawSHA256': sha((work / n).read_bytes()), 'bytes': (work / n).stat().st_size} for n in actual_names}}
    save(work / 'PRODUCER.json', producer)
    assert (work / 'stations.json').read_bytes() == raw_stations
    summary = json.loads((work / 'node-ancillary-integer.stdout').read_text(encoding='utf-8'))
    assert summary['rows'] == 4 and summary['unavailable'] == 3 and summary['selected_index'] == 0
    assert summary['origin'] == expected['origin'] and summary['product'] == expected['product']
    with (work / 'output.csv').open(encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source, strict=True)
        rows = list(reader)
        assert reader.fieldnames == expected['csvHeader']
    stations_decimal = json.loads(raw_stations, parse_int=Decimal, parse_float=Decimal)
    events = [json.loads(line) for line in (work / 'node-ancillary-integer.stderr').read_text(encoding='utf-8').split('\n') if line.strip()]
    assert len(rows) == 4 and len(events) == 3
    for i, row in enumerate(rows):
        assert set(row) == set(expected['csvHeader']) and row['request_key'] == 'selected-field'
        assert row['station_id'] == stations_decimal[i]['id']
        assert [float(row[k]) for k in ['latitude', 'longitude']] == expected['coordinates'][i]
        assert row['value'] == expected['values'][i] and row['algorithm'] == expected['algorithms'][i]
        assert [row[k] for k in ['message', 'field', 'byte_offset']] == ['0', '0', '0']
        assert json.loads(row['product_json']) == expected['product']
        assert json.loads(row['contributors_json']) == (expected['availableContributors'] if i == 0 else [])
        if i:
            assert events[i - 1] == {'phase': 'sample', 'station_id': stations_decimal[i]['id'], 'station_index': i, 'code': expected['diagnosticCodes'][i - 1]}
    save(work / 'INDEPENDENT-CSV-REVIEW.json', {'status': 'PASS', 'all11ColumnRows': rows, 'allDiagnostics': events, 'summary': summary, 'expectedSHA256': EXPECTED_SHA})

    p = run('join-large-integer', [sys.executable, '-B', HELPER, work / 'stations.json', work / 'output.csv', work / 'node-ancillary-integer.stderr'])
    assert p.stdout.isascii()
    def reject_constant(value):
        raise AssertionError('Non-JSON numeric token ' + value)
    joined = json.loads(p.stdout, parse_int=Decimal, parse_float=Decimal, parse_constant=reject_constant)
    assert len(joined) == 3
    for item, index, code in zip(joined, expected['diagnosticIndices'], expected['diagnosticCodes']):
        assert item['station_index'] == index and item['code'] == code
        assert item['station'] == stations_decimal[index] and item['csv_record'] == rows[index]
    positive = Decimal(expected['largeIntegerToken'])
    assert joined[0]['station']['extra'] == positive
    assert joined[1]['station']['extra']['nested'][0] == Decimal('-' + expected['largeIntegerToken'])
    assert joined[2]['station']['extra'] == Decimal('1e400')
    spec = importlib.util.spec_from_file_location('ancillary_integer_receiver', HELPER)
    receiver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(receiver)
    imported = receiver.join(work / 'stations.json', work / 'output.csv', work / 'node-ancillary-integer.stderr')
    integer = 10 ** 5001 + 1
    assert type(imported[0]['station']['extra']) is int and imported[0]['station']['extra'] == integer
    assert imported[1]['station']['extra']['nested'] == [-integer, 7]
    assert initial_limit == sys.get_int_max_str_digits()

    altered = [dict(row) for row in rows]
    altered[1]['latitude'] = '3.5'
    text = io.StringIO(newline='')
    writer = csv.DictWriter(text, fieldnames=expected['csvHeader'], lineterminator='\r\n')
    writer.writeheader(); writer.writerows(altered)
    (work / 'wrong-coordinate.csv').write_bytes(text.getvalue().encode('utf-8'))
    try:
        receiver.join(work / 'stations.json', work / 'wrong-coordinate.csv', work / 'node-ancillary-integer.stderr')
    except ValueError as error:
        assert str(error) == 'station coordinates do not match its CSV record'
    else:
        raise AssertionError('Changed coordinate accepted')
    bad = raw_stations.replace(expected['largeIntegerToken'].encode(), b'NaN', 1)
    assert bad != raw_stations
    (work / 'non-json-token.json').write_bytes(bad)
    p = run('reject-non-json-token', [sys.executable, '-B', HELPER, work / 'non-json-token.json', work / 'output.csv', work / 'node-ancillary-integer.stderr'], success=False)
    assert not p.stdout and b'non-JSON numeric token in original stations: NaN' in p.stderr
    assert sys.get_int_max_str_digits() == initial_limit
    result = {'status': 'PASS', 'expectedSHA256': EXPECTED_SHA, 'producerReusedWithoutLocalRerun': bool(args.consume_from), 'actualProcessInvocationsThisPhase': len(commands), 'freshProducerProcesses': 0 if args.consume_from else 2, 'receiverSuccessCLIProcesses': 1, 'receiverExpectedFailureCLIProcesses': 1, 'directReceiverCalls': 2, 'CSVRowsFullyRead': 4, 'joinedRecordsFullyRead': 3, 'positiveNegativeNestedIntegerDigits': 5002, 'exactOriginalIntegersAndExponentTokenPreserved': True, 'strictCoordinateMismatchAndNonJSONTokenRejection': True, 'globalIntegerDigitLimitBefore': initial_limit, 'globalIntegerDigitLimitAfter': sys.get_int_max_str_digits(), 'unchangedMoonBitSourceConfigAPIFiles': len(sources), 'oldAcceptedSuitesRerun': False}
    save(work / 'RESULT.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
