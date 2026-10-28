"""Independent raw-fixture/identity acceptance for the public query catalogue."""
import argparse
from fractions import Fraction
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "testdata/query-inspection"

def raw_fixture(data):
    """Read only this fixture's original3.0/4.0/5.0 headers, never library output."""
    rows, lengths = [], []
    offset, message = 0, 0
    while offset < len(data):
        assert data[offset:offset+4] == b"GRIB" and data[offset+7] == 2
        length = int.from_bytes(data[offset+8:offset+16], "big")
        assert data[offset+length-4:offset+length] == b"7777"
        lengths.append(length)
        point, field = offset+16, 0
        product, constant, identification, scanning = None, None, None, None
        while point < offset+length-4:
            count = int.from_bytes(data[point:point+4], "big")
            section = data[point:point+count]
            assert count >= 5 and point+count <= offset+length-4
            number = section[4]
            if number == 1:
                identification = {"centre": int.from_bytes(section[5:7], "big"),
                    "subcentre": int.from_bytes(section[7:9], "big"),
                    "master_table": section[9], "local_table": section[10],
                    "reference_time": [int.from_bytes(section[12:14], "big"), *section[14:19]]}
            elif number == 3:
                assert section[12:14] == b"\0\0"
                scanning = section[71]
            elif number == 4:
                assert section[7:9] == b"\0\0"
                def surface(start):
                    kind, scale = section[start:start+2]
                    result = {"kind": kind}
                    if scale != 255:
                        result["scale"] = -(scale & 127) if scale & 128 else scale
                    value = int.from_bytes(section[start+2:start+6], "big")
                    if value != 0xffffffff:
                        result["scaled_value"] = value
                    return result
                product = {"discipline": data[offset+6], "category": section[9], "parameter": section[10],
                           **identification, "time_unit": section[17],
                           "first_surface": surface(22), "second_surface": surface(28)}
                time = int.from_bytes(section[18:22], "big")
                if time != 0xffffffff:
                    product["forecast_time"] = time
            elif number == 5:
                assert section[9:11] == b"\0\0" and section[15:19] == b"\0"*4 and section[19] == 0
                assert int.from_bytes(section[5:9], "big") == 5
                constant = struct.unpack(">f", section[11:15])[0]
            elif number == 6:
                assert section[5:] == b"\0\x7c"  # six nodes; first absent, five present
            elif number == 7:
                assert len(section) == 5
                rows.append({"index": len(rows), "origin": {"message": message, "field": field,
                    "byte_offset": offset, "scanning_mode": scanning},
                    "product": product, "constantValue": constant})
                field += 1
            else:
                raise AssertionError(number)
            point += count
        assert point == offset+length-4
        offset += length
        message += 1
    assert offset == len(data)
    return rows, lengths

def expected_legacy(entries, indexes, batch=False):
    if len(indexes) == 1:
        row = entries[indexes[0]]
        return {"kind": "unique", "origin": row["origin"], "product": row["product"],
                "value": row["constantValue"]}
    text = "no field matches query" if not indexes else "query matches multiple fields"
    return {"kind": "invalid-request", "message": ("probe: " if batch else "") + text}

def verify_case(row, expected_entries, matched):
    report = row["inspection"]
    assert report["kind"] == "report"
    report = report["report"]
    assert set(report) == {"field_count", "match_count", "entries"}
    assert type(report["field_count"]) is int and type(report["match_count"]) is int
    assert report["field_count"] == len(expected_entries) == len(report["entries"])
    assert report["match_count"] == len(matched)
    for index, (actual, expected) in enumerate(zip(report["entries"], expected_entries, strict=True)):
        assert set(actual) == {"index", "matches", "origin", "product"}
        assert type(actual["index"]) is int and type(actual["matches"]) is bool
        assert actual == {"index": index, "matches": index in matched,
                          "origin": expected["origin"], "product": expected["product"]}
    assert row["unique"] == expected_legacy(expected_entries, matched)
    assert row["batch"] == expected_legacy(expected_entries, matched, True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--moon", default="moon")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    fixture = (DATA / "catalogue.grib2").read_bytes()
    expected = json.loads((DATA / "EXPECTED.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(fixture).hexdigest() == expected["fixtureSHA256"]
    entries, lengths = raw_fixture(fixture)
    assert entries == expected["entries"] and lengths == expected["messageLengths"]
    assert len(entries) == 6 and len(lengths) == 5
    assert Fraction(85000, 10**0) == Fraction(850000, 10**1) == 85000
    # The portable public consumer embeds exactly these same bytes.
    source = (ROOT / "cmd/query-catalog/main.mbt").read_text(encoding="utf-8")
    literal = re.search(r'b"((?:\\x[0-9a-f]{2})+)"', source)[1]
    assert bytes.fromhex(literal.replace("\\x", "")) == fixture
    outputs, commands = {}, []
    for target in ("js", "wasm-gc"):
        command = [args.moon, "run", "cmd/query-catalog", "--target", target]
        result = subprocess.run(command, cwd=ROOT, capture_output=True)
        (args.output / (target + ".stdout.jsonl")).write_bytes(result.stdout)
        (args.output / (target + ".stderr.txt")).write_bytes(result.stderr)
        commands.append({"command": command, "exitCode": result.returncode})
        if result.returncode:
            raise AssertionError(result.stderr.decode("utf-8", "replace")[-2000:])
        rows = [json.loads(line) for line in result.stdout.decode("utf-8").split("\n") if line.strip()]
        assert len(rows) == 17 and len({r["case"] for r in rows}) == 17
        by_name = {r["case"]: r for r in rows}
        assert set(by_name) == set(expected["queries"]) | {"slice", "empty", "invalid-reference", "invalid-empty", "snapshot"}
        for name, matched in expected["queries"].items():
            verify_case(by_name[name], entries, matched)
        verify_case(by_name["slice"], [entries[i] for i in (1, 2, 3)], [1, 2])
        verify_case(by_name["empty"], [], [])
        invalid = {"kind": "invalid-request", "message": expected["invalidReferenceMessage"]}
        for name in ("invalid-reference", "invalid-empty"):
            row = by_name[name]
            assert row["inspection"] == row["unique"] == invalid
            assert row["batch"] == {"kind": "invalid-request", "message": "probe: " + expected["invalidReferenceMessage"]}
        snapshot = by_name["snapshot"]
        assert snapshot["changed_snapshot_year"] == 1900
        assert snapshot["original_year"] == snapshot["fresh_year"] == 2007
        assert snapshot["unique"] == expected_legacy(entries, [2])
        assert snapshot["batch"] == expected_legacy(entries, [2], True)
        outputs[target] = rows
        print(json.dumps({"queryCatalogue": "PASS", "target": target, "cases": 17,
                          "fields": 6, "messages": 5, "independentRawMetadata": True}))
    assert outputs["js"] == outputs["wasm-gc"]
    record = {"status": "PASS", "casesPerTarget": 17, "targets": ["js", "wasm-gc"],
              "actualConsumerInvocations": 2, "independentRawMetadataAndHandIdentities": True,
              "samePhysicalDifferentEncodedSurface": True, "completeUntruncatedCatalogue": True,
              "invalidAndEmptyInput": True, "legacyUniqueBatchAgreement": True,
              "snapshotIsolation": True, "dualBackendSemanticEquality": True,
              "commands": commands, "fixtureSHA256": expected["fixtureSHA256"]}
    (args.output / "RESULT.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
