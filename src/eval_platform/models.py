from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvaluationCase(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1, max_length=10000)
    reference: str | None = Field(default=None, max_length=20000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RubricCriterion(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    weight: float = Field(gt=0, le=1)


class Rubric(BaseModel):
    name: str = "default"
    criteria: list[RubricCriterion] = Field(min_length=1)
    pass_threshold: float = Field(default=0.60, ge=0, le=1)

    def normalized_weights(self) -> dict[str, float]:
        total = sum(criterion.weight for criterion in self.criteria)
        return {criterion.name: criterion.weight / total for criterion in self.criteria}


class ModelOutput(BaseModel):
    text: str
    latency_ms: float = Field(ge=0)
    provider: str
    error: str | None = None


class CriterionScore(BaseModel):
    criterion: str
    score: float = Field(ge=0, le=1)
    rationale: str


class CaseResult(BaseModel):
    case_id: str
    output: ModelOutput
    scores: list[CriterionScore]
    overall_score: float = Field(ge=0, le=1)
    passed: bool


class EvaluationRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=utc_now)
    rubric: Rubric
    results: list[CaseResult]
    summary: dict[str, Any] = Field(default_factory=dict)


class FeedbackLabel(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_REVIEW = "needs_review"


class HumanFeedback(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    case_id: str
    label: FeedbackLabel
    rating: int = Field(ge=1, le=5)
    notes: str = Field(default="", max_length=5000)
    reviewer: str = Field(default="anonymous", max_length=200)
    created_at: datetime = Field(default_factory=utc_now)