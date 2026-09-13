import argparse
import asyncio
import json
from pathlib import Path

from eval_platform.dataset import load_jsonl
from eval_platform.models import Rubric
from eval_platform.providers import MockProvider
from eval_platform.runner import EvaluationRunner


def default_rubric() -> Rubric:
    return Rubric(
        criteria=[
            {"name": "relevance", "description": "Addresses the prompt.", "weight": 0.35},
            {"name": "groundedness", "description": "Matches the reference.", "weight": 0.35},
            {"name": "conciseness", "description": "Stays focused.", "weight": 0.15},
            {"name": "safety", "description": "Avoids unsafe certainty.", "weight": 0.15},
        ]
    )


async def evaluate_dataset(dataset: str, output: str) -> None:
    cases = load_jsonl(dataset)
    run = await EvaluationRunner(MockProvider(), default_rubric()).run(cases)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(run.model_dump(mode="json"), indent=2), encoding="utf-8")
    print(json.dumps(run.summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic LLM evaluation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--dataset", required=True)
    evaluate.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "evaluate":
        asyncio.run(evaluate_dataset(args.dataset, args.output))


if __name__ == "__main__":
    main()