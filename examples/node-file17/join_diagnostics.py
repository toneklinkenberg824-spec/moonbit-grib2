"""Join successful file-adapter stderr to original input and logical CSV rows."""
import argparse
import csv
import json
import math
from pathlib import Path


def _same_coordinate(csv_value, original_value):
    actual, expected = float(csv_value), float(original_value)
    return actual == expected or (math.isnan(actual) and math.isnan(expected))


def join(station_path, csv_path, diagnostic_path):
    stations = json.loads(Path(station_path).read_text(encoding="utf-8-sig"))
    # UTF8 file bytes bound any field's characters; restore the caller's limit.
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(max(previous_limit, Path(csv_path).stat().st_size))
        with Path(csv_path).open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source, strict=True))
    finally:
        csv.field_size_limit(previous_limit)
    if len(rows) != len(stations):
        raise ValueError("CSV and station counts differ")
    joined = []
    seen = set()
    # JSONL uses LF boundaries; Unicode line separators can be ID string data.
    for line in Path(diagnostic_path).read_text(encoding="utf-8").split("\n"):
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("phase") != "sample":
            raise ValueError("requires sample diagnostics from a successful run")
        index = event.get("station_index")
        if type(index) is not int:
            raise ValueError("station_index is required; no ID-only guess is made")
        if index < 0 or index >= len(stations) or index in seen:
            raise ValueError("invalid or repeated station_index")
        station, row = stations[index], rows[index]
        if station["id"] != event["station_id"] or row["station_id"] != station["id"]:
            raise ValueError("station identity does not match its CSV record")
        # Compare in the producer's Double domain; retain original JSON integers.
        if not _same_coordinate(row["latitude"], station["latitude"]) or not _same_coordinate(row["longitude"], station["longitude"]):
            raise ValueError("station coordinates do not match its CSV record")
        if row["value"] != "":
            raise ValueError("diagnostic points to an available CSV value")
        seen.add(index)
        joined.append({
            "station_index": index,
            "code": event["code"],
            "station": station,
            "csv_record": row,
        })
    if seen != {i for i, row in enumerate(rows) if row["value"] == ""}:
        raise ValueError("diagnostics do not cover the unavailable CSV records")
    return joined


def _original_station_fragments(station_path):
    text = Path(station_path).read_text(encoding="utf-8-sig")

    def reject_constant(value):
        raise ValueError("non-JSON numeric token in original stations: " + value)

    stations = json.loads(text, parse_constant=reject_constant)
    if not isinstance(stations, list):
        raise ValueError("original station JSON must be an array")
    decoder = json.JSONDecoder(parse_constant=reject_constant)
    position = text.index("[") + 1
    fragments = []
    for _ in stations:
        while text[position] in " \t\r\n":
            position += 1
        start = position
        _, position = decoder.raw_decode(text, position)
        fragments.append(text[start:position])
        while text[position] in " \t\r\n":
            position += 1
        if text[position] == ",":
            position += 1
    return fragments


def _ascii_json_fragment(text):
    return "".join(
        char if ord(char) < 128 else json.dumps(char, ensure_ascii=True)[1:-1]
        for char in text
    )


def _encode_joined_result(result, station_path):
    try:
        return json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False)
    except ValueError:
        # Valid source numbers can exceed binary64. Reuse their original tokens.
        originals = _original_station_fragments(station_path)
        records = []
        for item in result:
            cells = []
            for key, value in item.items():
                if key == "station":
                    encoded = _ascii_json_fragment(originals[item["station_index"]])
                else:
                    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False)
                cells.append(json.dumps(key) + ": " + encoded)
            records.append("  {" + ", ".join(cells) + "}")
        return "[\n" + ",\n".join(records) + "\n]"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stations_json")
    parser.add_argument("output_csv")
    parser.add_argument("stderr_jsonl")
    args = parser.parse_args()
    result = join(args.stations_json, args.output_csv, args.stderr_jsonl)
    # ASCII JSON escapes also survive a Windows redirected stdout using GBK.
    print(_encode_joined_result(result, args.stations_json))


if __name__ == "__main__":
    main()
