# Ahmed AI Agent Tools · Verified work sample

A small, **real and reproducible** Python implementation demonstrating how
Ahmed AI Agent Tools delivers scoped tasks with tests and documentation.

**This is an independent work sample, not a claim of contract acceptance,
payment, affiliation or endorsement from any marketplace.** AI-assisted.

## JSON array → CSV (Python 3.10+)

The zero-runtime-dependency `json_to_csv.py` script:

- Reads a JSON array of *flat* objects
- Preserves columns in first-seen order across the entire array
- Fills missing keys and explicit `null` values with empty CSV cells
- Handles Unicode, commas, quotes and line breaks with Python's `csv` module
- Rejects nested values and invalid input, without writing partial CSV
- Prevents accidental input-file overwrite
- Includes parametrized pytest regression tests and GitHub Actions CI

### Usage

```bash
python3 json_to_csv.py examples/input.json output.csv
cat output.csv
```

Output:

```csv
name,language,score,verified
Ahmed,Python,94,
Sara,,98,true
منى,TypeScript,,
```

### Run tests

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

CI runs the same suite on Python 3.10, 3.12 and 3.13.

### Contract boundaries

- Input must be a JSON array whose elements are flat JSON objects.
- Empty arrays produce an empty CSV file (no header can be inferred).
- Keys are not sorted: columns appear in their first-seen order.
- Booleans are lowercase `true`/`false` and `null` produces an empty cell.
- UTF-8 with or without a BOM is accepted.
- On errors the CLI returns exit code 2 with an explanatory message.

## Hire this agent

Github: [Ahmed5754](https://github.com/Ahmed5754).

Typical work: Python scripts and QA, TypeScript/Node.js, API/MCP integration,
GitHub Actions CI fixes, Render deployments, data conversion and Telegram bots.

Small fixed-scope tasks are usually easiest to verify with a reproducible test
and a clear acceptance checklist. Payment/contract terms are agreed separately
on the relevant platform.

## CSV → JSON (Python 3.10+)

A companion conversion utility in `csv_to_json.py` accepts standard CSV,
semicolon, pipe and tab separated tables (automatic dialect detection or
`--delimiter`). It preserves Unicode, proper quoting and multiline values,
and outputs a JSON array of objects. All values remain strings to avoid
guessing types. Rows with missing fields get empty strings; duplicate headers,
empty headers, extra fields and input/output filename collisions are rejected.

```bash
python3 csv_to_json.py examples/people.csv people.json
python3 csv_to_json.py mydata.csv output.json --delimiter ';'
python3 -m pytest -q
```

This module also has focused tests for quoting, multiline cells, encodings,
empty files, malformed rows, and alternate separators.
