from fastapi import FastAPI

from ai_review_agent.engine import ReviewEngine
from ai_review_agent.models import ReviewRequest, ReviewResult

app = FastAPI(
    title="AI Review Agent",
    summary="Pre-review AI project applications and token plans.",
    version="0.1.0",
)

engine = ReviewEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_model=ReviewResult)
def review(request: ReviewRequest) -> ReviewResult:
    return engine.review(request)

