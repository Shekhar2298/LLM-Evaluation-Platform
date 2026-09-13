# LLM Evaluation Platform

A practical Python platform for evaluating LLM outputs against datasets, weighted rubrics, automated scores, and human feedback.

The project is intentionally small enough to understand in one sitting, but structured around the same boundaries a larger evaluation system needs: datasets are versionable, providers are replaceable, scoring is explicit, and aggregate reports are machine-readable.

> This is an evaluation and experimentation toolkit. It is not a guarantee of model safety, factuality, or suitability for a production decision.

## Why this project exists

LLM applications are easy to demo and difficult to measure consistently. A single good response does not tell a team whether a model is reliable across a dataset, whether one prompt is better than another, or whether a regression has been introduced.

This repository provides a repeatable loop:

```text
Dataset → Provider → Model outputs → Rubric scorer → Case results → Aggregate report
                                          ↑
                                  Human feedback
```

## Features

- JSONL dataset loading with schema validation.
- Typed evaluation cases, rubric criteria, outputs, scores, and feedback.
- Weighted rubric scoring with a deterministic baseline scorer.
- Pluggable provider interface.
- Mock provider for offline development and CI.
- OpenAI-compatible provider adapter for real model runs.
- Aggregate metrics by criterion, including mean score and pass rate.
- In-memory human feedback API for review workflows.
- FastAPI endpoints for health checks, evaluation runs, and feedback.
- CLI entry point for running a dataset evaluation and writing a JSON report.
- Unit and API tests covering the end-to-end evaluation path.

## Architecture

```text
                         ┌──────────────────────┐
                         │ JSONL / API dataset  │
                         └──────────┬───────────┘
                                    │
                                    v
┌──────────────┐      ┌────────────────────────┐      ┌─────────────────┐
│ CLI or API   │ ───> │ EvaluationRunner       │ ───> │ LLMProvider      │
└──────────────┘      │ - execute each case    │      │ - mock           │
                      │ - record latency       │      │ - compatible API │
                      └──────────┬─────────────┘      └─────────────────┘
                                 │
                                 v
                      ┌────────────────────────┐
                      │ RubricScorer           │
                      │ - criterion scores     │
                      │ - weighted overall      │
                      └──────────┬─────────────┘
                                 │
                                 v
                      ┌────────────────────────┐
                      │ ReportBuilder          │
                      │ - means and pass rates │
                      │ - JSON export          │
                      └──────────┬─────────────┘
                                 │
                                 v
                      ┌────────────────────────┐
                      │ Human feedback store   │
                      │ - approve / reject     │
                      │ - reviewer notes       │
                      └────────────────────────┘
```

### Design decisions

1. **Provider abstraction:** model access is isolated behind `LLMProvider`, so evaluation logic does not depend on one vendor.
2. **Explicit rubrics:** scoring criteria are data, not hidden prompt behavior. Teams can version and review their rubric.
3. **Deterministic baseline:** the included scorer is transparent and reproducible. It is a baseline for development, not a replacement for expert review or a calibrated judge model.
4. **Case-level results:** each result keeps the input, output, scores, latency, and errors needed to debug a regression.
5. **Human feedback as a first-class record:** reviewer decisions and notes can be attached to a case instead of living in a spreadsheet disconnected from the run.

## Quick start

Requires Python 3.11 or newer.

```bash
cd llm-evaluation-platform
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Run the sample dataset:

```bash
python -m eval_platform.cli evaluate \
  --dataset datasets/sample.jsonl \
  --output artifacts/sample-report.json
```

Start the API:

```bash
uvicorn eval_platform.api:app --reload
```

The service runs at `http://127.0.0.1:8000`.

## API examples

Evaluate cases directly:

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "cases": [
      {
        "id": "support-001",
        "prompt": "Explain why a password reset link might expire.",
        "reference": "Reset links commonly expire to reduce account takeover risk.",
        "metadata": {"domain": "support"}
      }
    ]
  }'
```

Submit human feedback:

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run-id-from-evaluation",
    "case_id": "support-001",
    "label": "accept",
    "rating": 4,
    "notes": "Accurate and concise."
  }'
```

## Dataset format

Each line in a JSONL dataset is one case:

```json
{
  "id": "case-001",
  "prompt": "What is a concise answer to this question?",
  "reference": "A reviewed reference answer.",
  "metadata": {
    "category": "helpfulness",
    "split": "dev"
  }
}
```

The reference answer is optional. Criteria that require grounding should be used only when a reviewed reference is available.

## Rubric model

The default rubric contains:

| Criterion | Weight | Intent |
| --- | ---: | --- |
| relevance | 0.35 | Does the output address the input? |
| groundedness | 0.35 | Does it overlap with the reviewed reference when provided? |
| conciseness | 0.15 | Is the output focused rather than empty or excessively long? |
| safety | 0.15 | Does it avoid unsupported certainty and unsafe instructions? |

Scores are normalized to a 0–1 scale. The default pass threshold is 0.60. In a real project, replace the baseline scorer with calibrated judge models, task-specific validators, or expert review.

## Environment variables

```dotenv
LLM_PROVIDER=mock
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=30
```

The mock provider is the default and does not require credentials. Never commit `.env` or API keys.

## Production roadmap

- Persist runs, case results, and feedback in PostgreSQL.
- Add dataset versioning and immutable run manifests.
- Add a judge-model adapter with structured output validation.
- Add pairwise comparison between prompts or model versions.
- Add slice metrics by metadata such as language, domain, and difficulty.
- Add an annotation queue with reviewer assignment and agreement metrics.
- Add trace IDs, cost tracking, rate limits, and secret management.
- Add regression gates for CI and pull requests.

## Project structure

```text
llm-evaluation-platform/
├── datasets/
│   └── sample.jsonl
├── src/eval_platform/
│   ├── api.py
│   ├── cli.py
│   ├── dataset.py
│   ├── models.py
│   ├── providers.py
│   ├── reporting.py
│   ├── runner.py
│   └── scoring.py
├── tests/
├── Dockerfile
├── pyproject.toml
└── README.md
```

## License

MIT. See `LICENSE`.