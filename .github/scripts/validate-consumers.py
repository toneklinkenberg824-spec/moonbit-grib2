"""Exercise real consumers against committed independent expectations."""
import argparse
import csv
import io
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = ["request_key", "station_id", "latitude", "longitude", "value", "algorithm",
          "message", "field", "byte_offset", "product_json", "contributors_json"]

def strict_json(raw):
    def invalid(token):
        raise ValueError("Non-JSON numeric token: " + token)
    return json.loads(raw, parse_constant=invalid)

def command(args, cwd, success=True):
    print("+ " + " ".join(map(str, args)), flush=True)
    result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True)
    if (result.returncode == 0) != success:
        sys.stdout.buffer.write(result.stdout)
        sys.stderr.buffer.write(result.stderr)
        raise AssertionError("Unexpected exit status: " + str(result.returncode))
    return result

def workspace(work, examples, dependency=None):
    work.mkdir(parents=True, exist_ok=False)
    modules = []
    for name, example in examples.items():
        dest = work / name
        dest.mkdir()
        for filename in ("main.mbt", "moon.mod", "moon.pkg", "pkg.generated.mbti"):
            source = ROOT / "examples" / example / filename
            if source.exists():
                shutil.copyfile(source, dest / filename)
        modules.append(dest)
    command(["moon", "work", "init"], work)
    command(["moon", "work", "use", ROOT, *modules, *([dependency] if dependency else [])], work)
    return modules

def build(module, target):
    command(["moon", "-C", module, "check", "--target", target], module)
    command(["moon", "-C", module, "build", "--target", target], module)

def binary(work, module):
    name = re.search(r'^name\s*=\s*"([^"]+)"', (module / "moon.mod").read_text(), re.M)[1]
    result = work / "_build/js/debug/build" / name / (name.split("/")[-1] + ".js")
    assert result.is_file(), result
    return result

def diagnostics(raw):
    return [strict_json(line) for line in raw.decode("utf-8").split("\n") if line.strip()]

def join(stations, output, diagnostic_path, work, success=True):
    return command([sys.executable, ROOT / "examples/node-file17/join_diagnostics.py",
                    stations, output, diagnostic_path], work, success)

def hosts(work):
    sampler, inventory = workspace(work, {"sampler": "node-file17", "inventory": "node-inventory24"})
    for module in (sampler, inventory):
        build(module, "js")
    producer, listing = binary(work, sampler), binary(work, inventory)
    command([sys.executable, ROOT / ".github/scripts/check-selection-errors.py",
             "--producer", producer, "--work", work / "selection-contract"], work)
    source = ROOT / "testdata/inventory24"
    fields = strict_json(command(["node", listing, source / "forecast.grib2"], work).stdout)
    assert fields["field_count"] == 4
    assert [f["index"] for f in fields["fields"]] == list(range(4))
    assert [f["product"].get("forecast_time") for f in fields["fields"]] == [None, 0, 6, -6]
    assert "forecast_time" not in fields["fields"][0]["product"]
    assert all((f["rows"], f["cols"], f["is_global"]) == (2, 3, False) for f in fields["fields"])
    selected = next(f["index"] for f in fields["fields"] if f["product"].get("forecast_time") == 6)
    output = work / "selected.csv"
    result = command(["node", producer, source / "forecast.grib2", source / "stations.json", output, selected], work)
    summary = strict_json(result.stdout)
    assert (summary["rows"], summary["unavailable"], summary["selected_index"]) == (2, 1, 2)
    assert output.read_bytes() == (source / "selected.csv").read_bytes()
    reader = csv.DictReader(io.StringIO(output.read_text(encoding="utf-8"), newline=""))
    assert reader.fieldnames == HEADER
    assert [r["value"] for r in reader] == ["333", ""]
    assert [d["code"] for d in diagnostics(result.stderr)] == ["outside-grid"]
    diag = work / "selected.stderr.jsonl"
    diag.write_bytes(result.stderr)
    joined = strict_json(join(source / "stations.json", output, diag, work).stdout)
    assert [r["station_index"] for r in joined] == [1]
    before = output.read_bytes()
    command(["node", producer, source / "forecast.grib2", source / "stations.json", output, selected], work, False)
    assert output.read_bytes() == before
    for invalid in ("later-unsupported.grib2", "later-truncated.grib2"):
        failure = command(["node", listing, source / invalid], work, False)
        assert not failure.stdout
        assert strict_json(failure.stderr.split(b"\n", 1)[0])["phase"] == "decode"
    nan = ROOT / "testdata/nan26"
    nan_csv, nan_diag = work / "nan.csv", work / "nan.stderr.jsonl"
    result = command(["node", producer, nan / "regional.grib2", nan / "stations.json", nan_csv, 0], work)
    assert nan_csv.read_bytes() == (nan / "result.csv").read_bytes()
    nan_diag.write_bytes(result.stderr)
    joined = join(nan / "stations.json", nan_csv, nan_diag, work)
    assert strict_json(joined.stdout) == strict_json((nan / "joined.expected.json").read_bytes())
    joined_path = work / "joined.json"
    joined_path.write_bytes(joined.stdout)
    command(["node", "-e", "JSON.parse(require('node:fs').readFileSync(process.argv[1],'utf8'))", joined_path], work)
    rejected = join(nan / "stations.json", nan / "wrong-kind.csv", nan / "diagnostics.jsonl", work, False)
    assert not rejected.stdout
    numeric = ROOT / "testdata/strictjson25"
    encoded = join(numeric / "stations.json", numeric / "result.csv", numeric / "diagnostics.jsonl", work)
    # Python stdout uses the host newline convention; numeric tokens/escaping stay exact.
    assert encoded.stdout.replace(b"\r\n", b"\n") == (numeric / "joined.expected.json").read_bytes().replace(b"\r\n", b"\n")
    numeric_output = work / "strict-numeric.json"
    numeric_output.write_bytes(encoded.stdout)
    command(["node", "-e", "JSON.parse(require('node:fs').readFileSync(process.argv[1],'utf8'))", numeric_output], work)
    print(json.dumps({"consumer": "hosts", "inventoryStates": [None, 0, 6, -6],
                      "selectedValues": ["333", ""], "NaNIdentityAndWrongKind": "PASS",
                      "laterFieldErrorsAndNoClobber": "PASS", "standardNumericLexemes": "PASS"}), flush=True)

def nyacsv(work, dependency):
    assert dependency and (dependency / "LICENSE").is_file()
    head = command(["git", "-C", dependency, "rev-parse", "HEAD"], work.parent).stdout.decode().strip()
    assert head == "fe4448e1e45a25f6fca151320c766519e80162c9"
    module, = workspace(work, {"consumer": "nyacsv13"}, dependency)
    expected = strict_json((ROOT / "testdata/consumer13/REFERENCE.json").read_bytes())
    for target in ("js", "wasm-gc"):
        build(module, target)
        result = command(["moon", "-C", module, "run", "--target", target, "."], module)
        records = [strict_json(line) for line in result.stdout.decode("utf-8").split("\n") if line.strip()]
        rows = {case: [r for r in records if r["kind"] == "row" and r["case"] == case]
                for case in expected["summaries"]}
        summaries = {r["case"]: r["consumed_rows"] for r in records if r["kind"] == "summary"}
        assert summaries == expected["summaries"]
        assert {case: len(items) for case, items in rows.items()} == summaries
        for case in ("real", "numeric"):
            ref, actual = expected[case], rows[case]
            for index, (row, value) in enumerate(zip(actual, ref["values"], strict=True)):
                assert len(row["cells"]) == 11 and all(isinstance(v, str) for v in row["cells"])
                assert row["cells"][0] == ref["keys"][index // 2]
                assert row["cells"][1] == ref["station_ids"][index % 2]
                assert row["product"] == strict_json(row["cells"][9])
                assert row["contributors"] == strict_json(row["cells"][10])
                if value is None:
                    assert row["value"] is None and row["cells"][4] == ""
                else:
                    assert math.isclose(row["value"], value, rel_tol=0, abs_tol=1e-9)
            if case == "real":
                assert [r["product"]["centre"] for r in actual] == ref["centres"]
                assert [int(r["cells"][6]) for r in actual] == ref["messages"]
                assert [int(r["cells"][8]) for r in actual] == ref["byte_offsets"]
            else:
                assert [r["product"].get("forecast_time") for r in actual] == ref["forecast_times"]
                assert all("forecast_time" not in r["product"] for r in actual[:2])
        assert rows["preview"][0]["cells"] == rows["real"][0]["cells"]
        assert not rows["empty"]
        print(json.dumps({"consumer": "NyaCSV", "target": target, "rows": 9,
                          "numericZeroMissingAndUnicode": "PASS", "dependency": head}), flush=True)

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["hosts", "nyacsv"])
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--dependency", type=Path)
args = parser.parse_args()
if args.mode == "hosts":
    hosts(args.work.resolve())
else:
    nyacsv(args.work.resolve(), args.dependency.resolve() if args.dependency else None)
