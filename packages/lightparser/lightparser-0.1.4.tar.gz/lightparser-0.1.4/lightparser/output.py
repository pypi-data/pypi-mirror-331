import csv
import json
import sys
import os
import atexit

_output_file = None
_output_format = None
_items_buffer = []
_headers_written = False
_mode = None  # "overwrite" or "append"

def setup_output():
    """Parse command line arguments and initialize output settings."""
    global _output_file, _output_format, _mode, _headers_written, _items_buffer
    args = sys.argv
    
    # Determine mode (-O or -o)
    if "-O" in args and "-o" in args:
        raise ValueError("Cannot use both -O and -o flags")
    elif "-O" in args:
        _mode = "overwrite"
        index = args.index("-O") + 1
    elif "-o" in args:
        _mode = "append"
        index = args.index("-o") + 1
    else:
        return  # No output specified

    if index < len(args):
        _output_file = args[index]
        _output_format = "json" if _output_file.endswith(".json") else "csv"

        # Handle overwrite mode: delete existing file
        if _mode == "overwrite" and os.path.exists(_output_file):
            os.remove(_output_file)

        # Handle JSON append: load existing data
        if _mode == "append" and _output_format == "json" and os.path.exists(_output_file):
            try:
                with open(_output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    _items_buffer.extend(existing_data if isinstance(existing_data, list) else [existing_data])
            except (json.JSONDecodeError, FileNotFoundError):
                pass  # Start with empty buffer if file is invalid

    # Register JSON finalizer
    if _output_format == "json":
        atexit.register(finalize_json)

def yield_item(item):
    """Store item and write to CSV immediately or buffer JSON for later."""
    _items_buffer.append(item)

    # Write CSV immediately, buffer JSON for final write
    if _output_file and _output_format == "csv":
        write_csv()

def write_csv():
    """Write items to CSV with correct overwrite/append semantics."""
    global _items_buffer, _headers_written
    if not _items_buffer:
        return

    # Determine write mode
    if _mode == "overwrite":
        # Use "w" only for the first write (headers), then "a"
        file_mode = "w" if not _headers_written else "a"
    else:  # append
        file_mode = "a"

    # Check if file exists to decide header writing
    file_exists = os.path.exists(_output_file)
    write_header = (not file_exists) or (_mode == "overwrite" and not _headers_written)

    with open(_output_file, file_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_items_buffer[0].keys())
        
        if write_header:
            writer.writeheader()
            _headers_written = True
        
        writer.writerows(_items_buffer)
    
    _items_buffer = []  # Clear buffer after writing

def finalize_json():
    """Final JSON write handling both overwrite and append modes."""
    if not _items_buffer:
        return

    with open(_output_file, "w", encoding="utf-8") as f:
        json.dump(_items_buffer, f, indent=4)
    _items_buffer.clear()

setup_output()  # Initialize output settings at script start