from time import perf_counter
from typing import Iterable

from eval_platform.models import EvaluationCase, EvaluationRun, ModelOutput, Rubric
from eval_platform.providers import LLMProvider
from eval_platform.reporting import build_summary
from eval_platform.scoring import score_output


class EvaluationRunner:
    def __init__(self, provider: LLMProvider, rubric: Rubric) -> None:
        self.provider = provider
        self.rubric = rubric

    async def run(self, cases: Iterable[EvaluationCase]) -> EvaluationRun:
        results = []
        for case in cases:
            started = perf_counter()
            try:
                text = await self.provider.generate(case)
                output = ModelOutput(
                    text=text,
                    latency_ms=round((perf_counter() - started) * 1000, 3),
                    provider=self.provider.name,
                )
            except Exception as exc:  # preserve a failed case for the report
                output = ModelOutput(
                    text="",
                    latency_ms=round((perf_counter() - started) * 1000, 3),
                    provider=self.provider.name,
                    error=str(exc),
                )
            results.append(score_output(case, output, self.rubric))

        return EvaluationRun(
            rubric=self.rubric,
            results=results,
            summary=build_summary(results),
        )