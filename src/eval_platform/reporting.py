from collections import defaultdict
from statistics import mean
from typing import Any

from eval_platform.models import CaseResult


def build_summary(results: list[CaseResult]) -> dict[str, Any]:
    if not results:
        return {
            "case_count": 0,
            "mean_overall_score": 0.0,
            "pass_rate": 0.0,
            "criteria": {},
        }

    criterion_scores: dict[str, list[float]] = defaultdict(list)
    for result in results:
        for score in result.scores:
            criterion_scores[score.criterion].append(score.score)

    return {
        "case_count": len(results),
        "mean_overall_score": round(mean(result.overall_score for result in results), 4),
        "pass_rate": round(sum(result.passed for result in results) / len(results), 4),
        "criteria": {
            criterion: {
                "mean_score": round(mean(scores), 4),
                "pass_rate": round(sum(score >= 0.6 for score in scores) / len(scores), 4),
            }
            for criterion, scores in sorted(criterion_scores.items())
        },
    }