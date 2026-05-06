from ai_review_agent.engine import ReviewEngine
from ai_review_agent.models import Readiness, ReviewRequest


def test_review_scores_complete_proposal_higher_than_weak_proposal() -> None:
    engine = ReviewEngine()
    complete = engine.review(
        ReviewRequest(
            title="AI 评审通过率优化 Agent",
            description=(
                "核心痛点是 AI 项目材料返工多、评审通过率低。Agent 会读取材料、扫描 token plan、"
                "识别风险，生成问题清单和重写建议。试点 20 人，"
                "目标将准备时间从 2 小时降到 20 分钟，"
                "一次通过率提升到 80%。人工审核后提交，并记录日志。"
            ),
            token_plan="每月约 500 万 tokens，单次约 2.5 万 tokens，通过缓存和摘要压缩控制消耗。",
        )
    )
    weak = engine.review(
        ReviewRequest(
            title="AI tool",
            description="We made a useful AI tool for project documents.",
        )
    )

    assert complete.overall_score > weak.overall_score
    assert complete.readiness in {
        Readiness.READY_WITH_MINOR_EDITS,
        Readiness.READY_TO_SUBMIT,
    }
    assert weak.issues


def test_rewrite_includes_default_token_plan_when_missing() -> None:
    result = ReviewEngine().review(
        ReviewRequest(
            title="AI Review Agent",
            description=(
                "Agent 读取材料并生成建议，解决评审返工问题，"
                "目标提升通过率 80%，人工审核。"
            ),
        )
    )

    assert "500 万 tokens" in result.rewritten_submission
    assert result.rewritten_submission
