import asyncio

from eval_platform.models import EvaluationCase, Rubric
from eval_platform.providers import MockProvider
from eval_platform.runner import EvaluationRunner


def test_runner_returns_case_results_and_summary() -> None:
    rubric = Rubric(
        criteria=[
            {"name": "groundedness", "description": "Matches reference", "weight": 1.0},
        ]
    )
    cases = [
        EvaluationCase(
            id="case-1",
            prompt="Explain two-factor authentication",
            reference="Two-factor authentication adds a second verification step.",
        )
    ]

    run = asyncio.run(EvaluationRunner(MockProvider(), rubric).run(cases))

    assert len(run.results) == 1
    assert run.results[0].output.provider == "mock"
    assert run.summary["case_count"] == 1
    assert run.summary["pass_rate"] == 1.0


def test_runner_keeps_provider_failure_as_a_case() -> None:
    class BrokenProvider:
        name = "broken"

        async def generate(self, case):
            raise RuntimeError("provider unavailable")

    rubric = Rubric(
        criteria=[{"name": "safety", "description": "Safe", "weight": 1.0}]
    )
    run = asyncio.run(
        EvaluationRunner(BrokenProvider(), rubric).run(
            [EvaluationCase(id="case-1", prompt="Hello")]
        )
    )

    assert run.results[0].output.error == "provider unavailable"
    assert run.summary["case_count"] == 1