import json
from pathlib import Path
from typing import Iterable

from eval_platform.models import EvaluationCase


class DatasetError(ValueError):
    """Raised when a dataset cannot be loaded or validated."""


def load_jsonl(path: str | Path) -> list[EvaluationCase]:
    source = Path(path)
    if not source.exists():
        raise DatasetError(f"Dataset does not exist: {source}")

    cases: list[EvaluationCase] = []
    for line_number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
            cases.append(EvaluationCase.model_validate(payload))
        except (json.JSONDecodeError, ValueError) as exc:
            raise DatasetError(f"Invalid dataset row at line {line_number}") from exc

    if not cases:
        raise DatasetError("Dataset contains no evaluation cases")
    return cases


def dump_jsonl(cases: Iterable[EvaluationCase], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case.model_dump(), default=str) + "\n")