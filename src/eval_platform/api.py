from fastapi import FastAPI
from pydantic import BaseModel, Field

from eval_platform.models import EvaluationCase, FeedbackLabel, HumanFeedback, Rubric
from eval_platform.providers import MockProvider
from eval_platform.runner import EvaluationRunner

app = FastAPI(
    title="LLM Evaluation Platform",
    version="0.1.0",
    description="Dataset, rubric, scoring, and human feedback API for LLM evaluation.",
)
feedback_store: list[HumanFeedback] = []

DEFAULT_RUBRIC = Rubric(
    criteria=[
        {"name": "relevance", "description": "Addresses the user request.", "weight": 0.35},
        {"name": "groundedness", "description": "Stays close to the reference.", "weight": 0.35},
        {"name": "conciseness", "description": "Is focused and readable.", "weight": 0.15},
        {"name": "safety", "description": "Avoids unsafe certainty.", "weight": 0.15},
    ]
)


class EvaluationRequest(BaseModel):
    cases: list[EvaluationCase] = Field(min_length=1, max_length=1000)
    rubric: Rubric | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": "mock"}


@app.post("/evaluate")
async def evaluate(request: EvaluationRequest) -> dict:
    run = await EvaluationRunner(MockProvider(), request.rubric or DEFAULT_RUBRIC).run(request.cases)
    return run.model_dump(mode="json")


@app.post("/feedback")
def add_feedback(feedback: HumanFeedback) -> dict:
    feedback_store.append(feedback)
    return feedback.model_dump(mode="json")


@app.get("/feedback")
def list_feedback(run_id: str | None = None) -> list[dict]:
    records = feedback_store if run_id is None else [item for item in feedback_store if item.run_id == run_id]
    return [item.model_dump(mode="json") for item in records]