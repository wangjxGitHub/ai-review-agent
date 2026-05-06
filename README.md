# AI Review Agent

AI Review Agent is a small, practical agent for pre-reviewing AI project applications before formal submission. It checks whether a proposal clearly explains the pain point, workflow, evaluation metrics, token plan, risks, and expected business value.

The project is designed for demo, internal tooling, and GitHub portfolio use. It runs without any API key by default, using a transparent rule-based review engine. You can later connect an LLM provider by implementing the `LLMProvider` interface.

## Features

- Scores AI project proposals across five dimensions
- Detects missing elements in project descriptions and token plans
- Generates concrete improvement suggestions
- Produces a polished rewrite suitable for submission forms
- Provides both CLI and FastAPI interfaces
- Includes sample data and tests

## Project Scenario

Many teams submit AI or Agent projects with vague descriptions, weak metrics, or incomplete token budget explanations. This leads to repeated review feedback and a lower pass rate.

AI Review Agent acts as a pre-review assistant:

1. Reads the draft project description.
2. Checks clarity, workflow, measurable outcomes, budget logic, and risk controls.
3. Produces a score, issue list, improvement actions, and a rewritten version.
4. Helps teams improve evaluation pass rate and reduce material preparation time.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run the CLI with the included sample:

```bash
ai-review-agent review examples/sample_proposal.md
```

Or read from standard input:

```bash
type examples\sample_proposal.md | ai-review-agent review -
```

Start the API server:

```bash
uvicorn ai_review_agent.api:app --reload
```

Then send a request:

```bash
curl -X POST http://127.0.0.1:8000/review ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"AI evaluation assistant\",\"description\":\"We built an agent to review AI project applications and improve pass rate.\",\"token_plan\":\"About 2M tokens per month.\"}"
```

## CLI Output

The CLI returns:

- Overall score
- Pass-readiness level
- Dimension scores
- Detected issues
- Suggested actions
- A rewritten submission draft

## API

### `POST /review`

Request:

```json
{
  "title": "AI Review Agent",
  "description": "We built an agent that reviews AI project applications...",
  "token_plan": "Estimated 5M tokens per month for 20 users.",
  "grant_plan": "Request 500 CNY trial grant for pilot usage."
}
```

Response:

```json
{
  "overall_score": 82,
  "readiness": "ready_with_minor_edits",
  "dimension_scores": [],
  "issues": [],
  "suggestions": [],
  "rewritten_submission": "..."
}
```

## Development

Run tests:

```bash
pytest
```

Format and lint:

```bash
ruff check .
ruff format .
```

## Repository Structure

```text
ai-review-agent/
  ai_review_agent/
    api.py
    cli.py
    engine.py
    llm.py
    models.py
  examples/
    sample_proposal.md
  tests/
    test_engine.py
  pyproject.toml
  README.md
```

## Suggested GitHub Description

An AI project pre-review agent that scores proposals, validates token plans, and rewrites submissions to improve evaluation pass rate.

