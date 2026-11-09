#!/usr/bin/env python3
"""Parse CSV into a JSON array of objects with configurable delimiter and encoding."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def convert(
    input_path: Path,
    output_path: Path,
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    indent: int = 2,
) -> int:
    source, target = input_path.expanduser().resolve(), output_path.expanduser().resolve()
    if source == target:
        raise ValueError("Input and output must be different paths")
    if delimiter is not None and len(delimiter) != 1:
        raise ValueError("Delimiter must be exactly one character")

    with source.open(encoding=encoding, newline="") as handle:
        if delimiter is None:
            sample = handle.read(16384)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|") if sample.strip() else csv.excel
            except csv.Error:
                dialect = csv.excel
            reader = csv.DictReader(handle, dialect=dialect)
        else:
            reader = csv.DictReader(handle, delimiter=delimiter)
        headers = reader.fieldnames
        if headers is None:
            records = []
        else:
            if not headers[0]:
                raise ValueError("CSV has an empty first header")
            if len(headers) != len(set(headers)):
                raise ValueError("Duplicate CSV column names are ambiguous")
            if any(not h for h in headers):
                raise ValueError("CSV contains empty column name")
            records = []
            for index, row in enumerate(reader, 2):
                if None in row:
                    raise ValueError(f"CSV row {index} has extra fields")
                records.append({column: (value if value is not None else "") for column, value in row.items()})

    with target.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(records, handle, indent=indent, ensure_ascii=False)
        handle.write("\n")
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert CSV (comma, semicolon, tab, pipe) to JSON objects")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--delimiter", help="Explicit CSV delimiter (otherwise auto-detected)")
    parser.add_argument("--encoding", default="utf-8-sig", help="Input encoding (default utf-8-sig)")
    args = parser.parse_args(argv)
    try:
        n = convert(args.input, args.output, delimiter=args.delimiter, encoding=args.encoding)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Converted {n} row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
