import json

import pytest

from csv_to_json import convert, main


def _run(tmp_path, source, **kwargs):
    csv_path = tmp_path / "input.csv"
    json_path = tmp_path / "output.json"
    csv_path.write_text(source, encoding="utf-8")
    count = convert(csv_path, json_path, **kwargs)
    return count, json.loads(json_path.read_text(encoding="utf-8"))


def test_comma_standard(tmp_path):
    assert _run(tmp_path, "name,age\nAda,20\n")[1] == [{"name": "Ada", "age": "20"}]


def test_semicolon_format(tmp_path):
    assert _run(tmp_path, "name;age\nAda;20\n")[1] == [{"name": "Ada", "age": "20"}]


def test_tabs(tmp_path):
    assert _run(tmp_path, "name\tage\nAda\t20\n")[1] == [{"name": "Ada", "age": "20"}]


def test_pipes(tmp_path):
    assert _run(tmp_path, "name|age\nAda|20\n", delimiter="|")[1] == [{"name": "Ada", "age": "20"}]


def test_unicode(tmp_path):
    assert _run(tmp_path, "name,city\nأحمد,غزة\n")[1] == [{"name": "أحمد", "city": "غزة"}]


def test_quotes_and_commas(tmp_path):
    assert _run(tmp_path, 'name,note\n"Ada, Jr.","He said ""hello"""\n')[1] == [{"name": "Ada, Jr.", "note": 'He said "hello"'}]


def test_multiline_cell(tmp_path):
    assert _run(tmp_path, 'name,note\nAda,"line 1\nline 2"\n')[1] == [{"name": "Ada", "note": "line 1\nline 2"}]


def test_missing_fields_empty(tmp_path):
    assert _run(tmp_path, "a,b\n1\n")[1] == [{"a": "1", "b": ""}]


def test_empty_csv(tmp_path):
    assert _run(tmp_path, "") == (0, [])


def test_header_without_rows(tmp_path):
    assert _run(tmp_path, "a,b\n") == (0, [])


def test_bom(tmp_path):
    csv_file = tmp_path / "bom.csv"
    output = tmp_path / "out.json"
    csv_file.write_bytes(b"\xef\xbb\xbf" + b"a,b\n1,2\n")
    assert convert(csv_file, output) == 1
    assert json.loads(output.read_text()) == [{"a": "1", "b": "2"}]


@pytest.mark.parametrize("source", ["a,a\n1,2\n", ",a\n1,2\n", "a,b\n1,2,3\n"])
def test_bad_rows_rejected_before_output(tmp_path, source):
    csv_file = tmp_path / "input.csv"
    output = tmp_path / "out.json"
    csv_file.write_text(source)
    with pytest.raises(ValueError):
        convert(csv_file, output, delimiter=",")
    assert not output.exists()


def test_same_path_refused(tmp_path):
    csv_file = tmp_path / "x.csv"
    csv_file.write_text("a\n1\n")
    with pytest.raises(ValueError):
        convert(csv_file, csv_file)


def test_invalid_delimiter(tmp_path):
    csv_file = tmp_path / "x.csv"
    csv_file.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        convert(csv_file, tmp_path / "out.json", delimiter="||")


def test_cli_bad_file(tmp_path, capsys):
    assert main([str(tmp_path / "missing.csv"), str(tmp_path / "out.json")]) == 2
    assert "Error:" in capsys.readouterr().err
