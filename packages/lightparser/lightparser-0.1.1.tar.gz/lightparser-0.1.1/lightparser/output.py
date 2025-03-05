import csv
import json
import sys

_output_file = None
_writer = None
_format = None

def setup_output(output_path):
    global _output_file, _writer, _format
    if not output_path:
        return

    _format = "json" if output_path.endswith(".json") else "csv"
    _output_file = open(output_path, "w", newline="", encoding="utf-8")

    if _format == "csv":
        _writer = csv.writer(_output_file)
        _writer.writerow(["fieldnames_placeholder"])

    elif _format == "json":
        _output_file.write("[")

def yield_item(item):
    global _output_file, _writer, _format

    if not _output_file:
        return

    if _format == "csv":
        if _writer and _writer.writerow:
            if _writer.writerow == ["fieldnames_placeholder"]:
                _writer.writerow(item.keys())
            _writer.writerow(item.values())

    elif _format == "json":
        _output_file.write(json.dumps(item, ensure_ascii=False) + ",")

def close_output():
    global _output_file, _format
    if _output_file:
        if _format == "json":
            _output_file.seek(_output_file.tell() - 1, os.SEEK_SET)
            _output_file.write("]")
        _output_file.close()
