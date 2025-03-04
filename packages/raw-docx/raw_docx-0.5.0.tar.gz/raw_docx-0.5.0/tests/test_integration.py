import json
from src.raw_docx.raw_docx import RawDocx

WRITE_FILE = True


def _run_test(name, save=False):
    filename = f"{name}.docx"
    raw_docx = RawDocx(_full_path(filename))
    result = raw_docx.target_document.to_dict()
    pretty_result = json.dumps(result, indent=2)
    result_filename = filename = f"{name}_result.json"
    if save:
        _write_json(_full_path(result_filename), pretty_result)
    expected = _read_json(_full_path(result_filename))
    assert pretty_result == expected


def _full_path(filename):
    return f"tests/test_files/{filename}"


def _write_json(full_path, content):
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(
            json.dumps(json.loads(content), indent=2)
        )  # Content expected to be string, no formatting


def _read_json(full_path):
    with open(full_path, "r") as f:
        return json.dumps(json.load(f), indent=2)  # Return pretty printed version


def test_example_1():
    _run_test("example_1", WRITE_FILE)
