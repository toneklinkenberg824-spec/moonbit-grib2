"""Real Node CLI contract checks with literal error/file and independent fixture oracles."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = ["request_key", "station_id", "latitude", "longitude", "value", "algorithm",
          "message", "field", "byte_offset", "product_json", "contributors_json"]
INVALID = {"phase": "selection", "code": "invalid-field-index", "argument": "FIELD_INDEX"}
OUTSIDE = {"phase": "selection", "code": "field-index-out-of-range", "field_count": 4}
SENTINEL = b"\x00existing CSV target\xff\r\nmust stay exact\n"

def check(producer, work, report):
    work.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / "testdata/inventory24"
    rows = []
    count = 0

    def invoke(label, lexeme, *, existing=False, grib=None, stations=None):
        nonlocal count
        count += 1
        output = work / (label + ".csv")
        if existing:
            output.write_bytes(SENTINEL)
        before = output.read_bytes() if output.exists() else None
        args = ["node", str(producer), str(grib or fixture / "forecast.grib2"),
                str(stations or fixture / "stations.json"), str(output), lexeme]
        actual = subprocess.run(args, capture_output=True)
        (work / (label + ".stdout.txt")).write_bytes(actual.stdout)
        (work / (label + ".stderr.txt")).write_bytes(actual.stderr)
        try:
            first = json.loads(actual.stderr.split(b"\n", 1)[0])
        except (ValueError, UnicodeDecodeError):
            first = None
        record = {"case": label, "indexArgument": lexeme, "command": args,
                  "exitCode": actual.returncode, "stdoutBytes": len(actual.stdout),
                  "firstDiagnostic": first, "outputExistedBefore": existing}
        rows.append(record)
        return actual, first, output, before

    def failed(actual, first, output, before, expected):
        assert actual.returncode != 0 and actual.stdout == b""
        assert first == expected, first
        if before is None:
            assert not output.exists()
        else:
            assert output.read_bytes() == before == SENTINEL

    for index, lexeme in enumerate(("not-an-index", "2.0", "", "1e0", "2147483648", "-2147483649")):
        for existing in (False, True):
            label = f"invalid-{index}-" + ("existing" if existing else "absent")
            failed(*invoke(label, lexeme, existing=existing), INVALID)
    for index, lexeme in enumerate(("2", "+2", "02", "0x2", "0b10", "0o2", "0_2", "-0")):
        actual, first, output, _ = invoke(f"valid-{index}", lexeme)
        assert actual.returncode == 0
        summary = json.loads(actual.stdout)
        expected_index = 0 if lexeme == "-0" else 2
        assert (summary["selected_index"], summary["rows"], summary["unavailable"]) == (expected_index, 2, 1)
        reader = csv.DictReader(io.StringIO(output.read_text(encoding="utf-8"), newline=""))
        assert reader.fieldnames == HEADER
        values = [row["value"] for row in reader]
        assert values == (["111", ""] if expected_index == 0 else ["333", ""])
        assert first == {"phase": "sample", "station_id": "catalog-outside",
                         "station_index": 1, "code": "outside-grid"}
        if expected_index == 2:
            assert output.read_bytes() == (fixture / "selected.csv").read_bytes()
        else:
            assert "forecast_time" not in summary["product"]
            assert hashlib.sha256(output.read_bytes()).hexdigest() == "f380708c1da3a43629977da250ce0bdfe6260d2c06e1c2cdc713b4b2d7e054fb"
    for index, lexeme in enumerate(("-1", "4", "2147483647")):
        failed(*invoke(f"range-{index}", lexeme, existing=index == 0), OUTSIDE)
    failed(*invoke("parse-before-io", "bad-index", existing=True,
                   grib=work / "missing.grib2", stations=work / "missing.json"), INVALID)
    actual, first, output, before = invoke("io-stays-io", "2", stations=work / "missing.json")
    assert actual.returncode != 0 and actual.stdout == b"" and not output.exists()
    assert first is None and b"ENOENT" in actual.stderr
    failed(*invoke("decode-stays-decode", "2", grib=fixture / "later-unsupported.grib2"),
           {"phase": "decode", "code": "unsupported-template", "section": 5, "template": 3})
    actual, first, output, before = invoke("valid-no-clobber", "2", existing=True)
    assert actual.returncode != 0 and actual.stdout == b"" and output.read_bytes() == before == SENTINEL
    assert first == {"phase": "sample", "station_id": "catalog-outside",
                     "station_index": 1, "code": "outside-grid"}
    assert count == 27
    result = {"status": "PASS", "cases": count, "producer": str(producer),
              "producerSHA256": hashlib.sha256(producer.read_bytes()).hexdigest(),
              "invalidEventLiteral": INVALID, "validIntegerSpellingsPreserved": 8,
              "nonzeroEmptyStdoutAndExactFileGuards": True,
              "independentFixtureValues": [111, 333], "records": rows}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selectionContract": "PASS", "realProcessCases": count,
                      "validIntegerSpellings": 8, "producerSHA256": result["producerSHA256"]}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    options = parser.parse_args()
    check(options.producer.resolve(), options.work.resolve(),
          options.report.resolve() if options.report else options.work.resolve() / "RESULT.json")
