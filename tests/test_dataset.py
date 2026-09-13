import json

import pytest

from eval_platform.dataset import DatasetError, load_jsonl


def test_load_jsonl_validates_cases(tmp_path) -> None:
    path = tmp_path / "cases.jsonl"
    path.write_text(json.dumps({"id": "one", "prompt": "Hello"}) + "\n", encoding="utf-8")

    cases = load_jsonl(path)

    assert len(cases) == 1
    assert cases[0].id == "one"


def test_invalid_jsonl_has_line_context(tmp_path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("{not-json}\n", encoding="utf-8")

    with pytest.raises(DatasetError, match="line 1"):
        load_jsonl(path)