from enum import StrEnum

from pydantic import BaseModel, Field


class Readiness(StrEnum):
    NEEDS_MAJOR_REVISION = "needs_major_revision"
    READY_WITH_MINOR_EDITS = "ready_with_minor_edits"
    READY_TO_SUBMIT = "ready_to_submit"


class ReviewRequest(BaseModel):
    title: str = Field(default="", description="Project title.")
    description: str = Field(..., min_length=10, description="Draft project description.")
    token_plan: str = Field(default="", description="Token budget and usage plan.")
    grant_plan: str = Field(default="", description="Grant or budget request plan.")
    target_users: str = Field(default="", description="Target team or user group.")


class DimensionScore(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    weight: float
    summary: str


class Issue(BaseModel):
    dimension: str
    severity: str
    message: str


class Suggestion(BaseModel):
    dimension: str
    action: str


class ReviewResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    readiness: Readiness
    dimension_scores: list[DimensionScore]
    issues: list[Issue]
    suggestions: list[Suggestion]
    rewritten_submission: str

