import csv
import json
from pathlib import Path

import pytest

from json_to_csv import convert, main


def _convert(tmp_path: Path, rows):
    src = tmp_path / "input.json"
    dest = tmp_path / "output.csv"
    src.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    count = convert(src, dest)
    with dest.open(newline="", encoding="utf-8") as file:
        table = list(csv.reader(file))
    return count, table


def test_basic_conversion(tmp_path):
    assert _convert(tmp_path, [{"name": "Ali", "age": 20}]) == (
        1, [["name", "age"], ["Ali", "20"]]
    )


def test_union_of_keys_missing_as_blank(tmp_path):
    assert _convert(tmp_path, [{"a": 1}, {"b": 2}, {"a": 3}]) == (
        3, [["a", "b"], ["1", ""], ["", "2"], ["3", ""]]
    )


def test_first_seen_header_order(tmp_path):
    assert _convert(tmp_path, [{"z": 4, "a": 2}, {"k": 3}])[1][0] == ["z", "a", "k"]


def test_null_and_booleans(tmp_path):
    assert _convert(tmp_path, [{"missing": None, "active": True, "deleted": False}])[1][1] == ["", "true", "false"]


def test_csv_quoting_and_newline(tmp_path):
    records = [{"text": 'a,"b"\nsecond line'}]
    assert _convert(tmp_path, records)[1][1] == ['a,"b"\nsecond line']


def test_unicode(tmp_path):
    assert _convert(tmp_path, [{"name": "مرحبا 🌍"}])[1][1] == ["مرحبا 🌍"]


def test_empty_array(tmp_path):
    assert _convert(tmp_path, []) == (0, [])


@pytest.mark.parametrize("bad", [{}, "abc", [1], [None], [{"x": []}], [{"x": {"a": 1}}]])
def test_reject_non_flat_input(tmp_path, bad):
    src = tmp_path / "input.json"
    dest = tmp_path / "output.csv"
    src.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        convert(src, dest)
    assert not dest.exists()


def test_invalid_json_return_code_and_no_output(tmp_path, capsys):
    src = tmp_path / "bad.json"
    target = tmp_path / "output.csv"
    src.write_text("{oops", encoding="utf-8")
    assert main([str(src), str(target)]) == 2
    assert "Error:" in capsys.readouterr().err
    assert not target.exists()


def test_no_overwriting_source(tmp_path):
    p = tmp_path / "in.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        convert(p, p)
    assert p.read_text(encoding="utf-8") == "[]"


def test_utf8_bom_accepted(tmp_path):
    p = tmp_path / "bom.json"
    p.write_bytes(b"\xef\xbb\xbf" + b'[{"name":"Ada"}]')
    out = tmp_path / "out.csv"
    assert convert(p, out) == 1
    assert out.read_text(encoding="utf-8") == "name\nAda\n"
