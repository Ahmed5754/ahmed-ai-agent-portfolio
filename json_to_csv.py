#!/usr/bin/env python3
"""Convert an array of flat JSON objects to RFC 4180-style CSV, with blank missing values."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def convert(input_path: Path, output_path: Path) -> int:
    """Convert and return number of records written.

    Columns are the first-seen union of all object keys, stable across runs.
    Nested arrays and objects are rejected because the contract specifies flat objects.
    """
    source = input_path.expanduser().resolve()
    target = output_path.expanduser().resolve()
    if source == target:
        raise ValueError("Input and output must be different paths")

    with source.open("r", encoding="utf-8-sig") as stream:
        rows = json.load(stream)

    if not isinstance(rows, list):
        raise ValueError("Input must be a JSON array of flat objects")

    columns: list[str] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Row {row_number} is not a JSON object")
        for key, value in row.items():
            if isinstance(value, (list, dict)):
                raise ValueError(f"Row {row_number}, field {key!r} is nested; only flat objects are supported")
            if key not in seen:
                columns.append(key)
                seen.add(key)

    # Validation is complete before opening the output to avoid partial CSV files.
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        if columns:
            writer.writerow(columns)
        for row in rows:
            writer.writerow([_cell(row.get(column)) for column in columns])
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert a JSON array of flat objects into CSV. Missing/null values become empty cells."
    )
    parser.add_argument("input", type=Path, help="Path to input JSON file")
    parser.add_argument("output", type=Path, help="Path to output CSV file")
    args = parser.parse_args(argv)
    try:
        count = convert(args.input, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Converted {count} record(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
