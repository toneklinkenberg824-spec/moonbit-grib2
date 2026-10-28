#!/usr/bin/env python3
"""Independent raw-byte/hand-node acceptance for the public crop iterator."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'testdata' / 'crop-iter'


def u32(data, at):
    return int.from_bytes(data[at:at+4], 'big')


def signed(value, sign):
    return -(value & (sign - 1)) if value & sign else value


def raw_fields(data):
    fields = []
    offset = 0
    while offset < len(data):
        assert data[offset:offset+4] == b'GRIB'
        length = int.from_bytes(data[offset+8:offset+16], 'big')
        end = offset + length
        assert data[end-4:end] == b'7777'
        at = offset + 16
        sections = {}
        while at < end - 4:
            n = u32(data, at)
            section = data[at:at+n]
            assert n >= 5 and at+n <= end-4
            assert section[4] not in sections, 'Fixture must have one field per message'
            sections[section[4]] = section
            at += n
        assert at == end-4 and {1, 3, 4, 5, 6, 7} <= sections.keys()
        grid, packing = sections[3], sections[5]
        bitmap = None if sections[6][5] == 255 else sections[6][6:]
        assert sections[6][5] in (0, 255)
        count = u32(grid, 6)
        valid_count = count if bitmap is None else sum(bool(bitmap[i // 8] & (128 >> (i % 8))) for i in range(count))
        assert valid_count == u32(packing, 5)
        fields.append({
            'origin': {'message': len(fields), 'field': 0, 'byte_offset': offset, 'scanning_mode': grid[71]},
            'shape': [u32(grid, 34), u32(grid, 30)], 'count': count,
            'coordinates': [signed(u32(grid, p), 1 << 31) / 1000000 for p in (46, 50, 55, 59)] + [u32(grid, p) / 1000000 for p in (63, 67)],
            'bitmap': bitmap, 'bits': packing[19], 'payload': sections[7][5:],
            'reference': Fraction(struct.unpack('>f', packing[11:15])[0]),
            'binaryScale': signed(int.from_bytes(packing[15:17], 'big'), 1 << 15),
            'decimalScale': signed(int.from_bytes(packing[17:19], 'big'), 1 << 15),
        })
        offset = end
    assert offset == len(data)
    return fields


def raw_value(field, index):
    bitmap = field['bitmap']
    if bitmap is not None:
        if not bitmap[index // 8] & (128 >> (index % 8)):
            return None
        packed_index = sum(bool(bitmap[i // 8] & (128 >> (i % 8))) for i in range(index))
    else:
        packed_index = index
    width = field['bits']
    bit_start = packed_index * width
    coded = 0
    for bit in range(bit_start, bit_start + width):
        coded = (coded << 1) | bool(field['payload'][bit // 8] & (128 >> (bit % 8)))
    return float((field['reference'] + coded * Fraction(2) ** field['binaryScale']) * Fraction(10) ** -field['decimalScale'])


def raw_acceptance(expected):
    for name, pin in expected['fixtures'].items():
        data = (DATA / name).read_bytes()
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256'], name
    raw = raw_fields((DATA / 'regions.grib2').read_bytes())
    assert len(raw) == 3
    coordinates = [[1, 359, 0, 1, 1, 1], [90, 0, -90, 360, 90, 90], [-90, 270, 90, 0, 90, 90]]
    for index, (field, manual) in enumerate(zip(raw, expected['fields'])):
        assert field['origin'] == manual['origin'] and field['shape'] == manual['shape']
        assert field['coordinates'] == coordinates[index]
        for row in manual['points']:
            assert raw_value(field, row[2]) == row[5], (index, row)
    # Hand-set repeated endpoints match; the accepted crop tables omit column4.
    for index in (0, 5, 10):
        assert raw_value(raw[1], index) == raw_value(raw[1], index+4)
    large = raw_fields((DATA / 'large-prefix.grib2').read_bytes())
    assert len(large) == 1 and large[0]['shape'] == expected['large']['shape']
    assert large[0]['count'] == expected['large']['count'] == 1048576
    assert large[0]['coordinates'] == [51.15, 0, 0, 51.15, 0.05, 0.05]
    assert large[0]['bits'] == 0 and large[0]['bitmap'] is None
    assert raw_value(large[0], 0) == raw_value(large[0], 1048575) == 7


def points_equal(points, manual, columns):
    assert len(points) == len(manual)
    for point, row in zip(points, manual):
        assert set(point) == set(columns), point
        actual = [point[k] for k in columns]
        for a, b in zip(actual, row):
            if isinstance(a, float) and isinstance(b, (int, float)):
                assert abs(a-b) <= max(abs(b), 1) * 1e-14, (actual, row)
            else:
                assert a == b, (actual, row)


def validate(records, expected, before=False):
    names = [case[0] for case in expected['cases']] + [case[0] for case in expected['invalid']]
    if not before:
        names += ['regional-pull-resume', 'global-independent-iterators', 'empty-exhaustion', 'large-prefix']
    assert [r['case'] for r in records] == names
    by_name = {r['case']: r for r in records}
    columns = expected['pointColumns']
    for name, index, _, indices in expected['cases']:
        record = by_name[name]
        field = expected['fields'][index]
        assert record['origin'] == field['origin']
        manual = [field['points'][i] for i in indices]
        points_equal(record['points'], manual, columns)
        if not before:
            points_equal(record['legacy'], manual, columns)
            assert record['afterEnd'] == [None, None]
    for name, _ in expected['invalid']:
        assert by_name[name]['error'] == 'invalid bbox'
        if not before:
            assert by_name[name]['legacyError'] == 'invalid bbox'
    if before:
        return
    region = expected['fields'][0]
    global_field = expected['fields'][1]
    record = by_name['regional-pull-resume']
    assert record['origin'] == region['origin']
    assert [record[k] for k in ['afterConstruction', 'afterFirst', 'afterSecond', 'afterResume']] == [0, 1, 2, 6]
    points_equal(record['prefix'], region['points'][:2], columns)
    points_equal(record['remaining'], region['points'][2:], columns)
    assert record['afterEnd'] is None
    record = by_name['global-independent-iterators']
    points_equal(record['first'], global_field['points'][:2], columns)
    points_equal(record['second'], global_field['points'][:1], columns)
    assert by_name['empty-exhaustion']['afterEnd'] == [None, None, None]
    record = by_name['large-prefix']
    assert record['shape'] == [1024, 1024] and record['seen'] == 2
    assert record['origin'] == region['origin']
    points_equal(record['points'], expected['large']['points'], columns)


def embedded_acceptance(expected):
    source = (ROOT / 'cmd' / 'crop-iter' / 'main.mbt').read_text(encoding='utf-8')
    literals = re.findall(r'b"((?:\\x[0-9a-f]{2})+)"', source)
    assert len(literals) == 2
    for function, name in [('main', 'regions.grib2'), ('large_prefix', 'large-prefix.grib2')]:
        literal = re.search(r'fn ' + function + r'\b[\s\S]*?b"((?:\\x[0-9a-f]{2})+)"', source)
        assert literal, function
        assert bytes.fromhex(literal[1].replace('\\x', '')) == (DATA / name).read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--moon', default='moon')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--before', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    expected = json.loads((DATA / 'EXPECTED.json').read_text(encoding='utf-8'))
    raw_acceptance(expected)
    if args.before:
        records = [json.loads(line) for line in args.before.read_text(encoding='utf-8').splitlines()]
        validate(records, expected, before=True)
        result = {'status': 'PASS', 'mode': 'existing_api_before', 'cases': len(records), 'rawBytesAndManualNodes': True}
    else:
        embedded_acceptance(expected)
        outputs = []
        commands = []
        for target in ('js', 'wasm-gc'):
            command = [args.moon, 'run', 'cmd/crop-iter', '--target', target]
            proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            (args.output / (target + '.stdout.jsonl')).write_text(proc.stdout, encoding='utf-8')
            (args.output / (target + '.stderr.txt')).write_text(proc.stderr, encoding='utf-8')
            commands.append({'command': command, 'exitCode': proc.returncode})
            assert proc.returncode == 0, target + ': executable consumer failed'
            records = [json.loads(line) for line in proc.stdout.splitlines()]
            validate(records, expected)
            outputs.append(records)
        assert outputs[0] == outputs[1], 'Backend semantic mismatch'
        result = {'status': 'PASS', 'targets': ['js', 'wasm-gc'], 'casesPerTarget': len(outputs[0]),
                  'actualConsumerInvocations': 2, 'rawBytesAndManualNodes': True,
                  'legacyCropAgreement': True, 'invalidBBoxSynchronousErrors': True,
                  'prefixResumeAndIndependentCursors': True, 'millionPointFieldPrefix': 2,
                  'lazinessClaimScope': 'Actual prefix consumer plus source audit of cursor/next construction; no timing or total-memory benchmark.',
                  'commands': commands, 'fixtures': expected['fixtures']}
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
