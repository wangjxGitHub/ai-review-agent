from __future__ import annotations

import re
from dataclasses import dataclass

from ai_review_agent.models import (
    DimensionScore,
    Issue,
    Readiness,
    ReviewRequest,
    ReviewResult,
    Suggestion,
)


@dataclass(frozen=True)
class ReviewDimension:
    name: str
    weight: float
    positive_keywords: tuple[str, ...]
    required_patterns: tuple[str, ...]
    success_summary: str
    missing_summary: str


DIMENSIONS = (
    ReviewDimension(
        name="core_pain_point",
        weight=0.22,
        positive_keywords=("痛点", "问题", "瓶颈", "返工", "效率", "成本", "通过率", "评审"),
        required_patterns=(r"(痛点|问题|瓶颈|返工|成本|效率)",),
        success_summary="The core pain point is clear and connected to review efficiency.",
        missing_summary="The proposal needs a sharper business pain point.",
    ),
    ReviewDimension(
        name="agent_workflow",
        weight=0.24,
        positive_keywords=("agent", "扫描", "识别", "生成", "建议", "重写", "闭环", "工作流"),
        required_patterns=(r"(读取|扫描|分析|识别)", r"(生成|输出|重写|建议)"),
        success_summary="The agent workflow explains input, reasoning, and output.",
        missing_summary="The agent workflow should describe how the system works end to end.",
    ),
    ReviewDimension(
        name="measurable_outcome",
        weight=0.22,
        positive_keywords=("提升", "降低", "缩短", "覆盖", "准确", "分钟", "小时", "%"),
        required_patterns=(r"\d+(\.\d+)?\s*(%|分钟|小时|天|人|次|万|M|K)?",),
        success_summary="The expected outcome includes measurable indicators.",
        missing_summary="The result should include concrete metrics before review submission.",
    ),
    ReviewDimension(
        name="token_budget",
        weight=0.18,
        positive_keywords=("token", "tokens", "预算", "额度", "调用", "模型", "消耗", "月"),
        required_patterns=(r"token|tokens", r"\d+(\.\d+)?\s*(万|千|m|k|元|cny|rmb)?"),
        success_summary="The token plan contains estimated usage and budget logic.",
        missing_summary="The token plan should explain expected usage volume and allocation.",
    ),
    ReviewDimension(
        name="risk_control",
        weight=0.14,
        positive_keywords=(
            "验证",
            "测试",
            "人工",
            "审核",
            "确认",
            "日志",
            "权限",
            "脱敏",
            "风险",
            "回滚",
            "复盘",
        ),
        required_patterns=(r"(验证|测试|人工|审核|确认|日志|权限|脱敏|风险|回滚|复盘)",),
        success_summary="The proposal mentions validation or risk controls.",
        missing_summary=(
            "The proposal should include verification, privacy, or human review controls."
        ),
    ),
)


class ReviewEngine:
    """Rule-based review engine for project application drafts."""

    def review(self, request: ReviewRequest) -> ReviewResult:
        text = self._combine_text(request)
        dimension_scores = [self._score_dimension(text, dimension) for dimension in DIMENSIONS]
        issues = self._build_issues(dimension_scores)
        suggestions = self._build_suggestions(dimension_scores, request)
        overall_score = round(
            sum(item.score * self._dimension_by_name(item.name).weight for item in dimension_scores)
        )
        readiness = self._readiness(overall_score, issues)
        rewritten_submission = self._rewrite(request, dimension_scores, overall_score)

        return ReviewResult(
            overall_score=overall_score,
            readiness=readiness,
            dimension_scores=dimension_scores,
            issues=issues,
            suggestions=suggestions,
            rewritten_submission=rewritten_submission,
        )

    def _combine_text(self, request: ReviewRequest) -> str:
        return "\n".join(
            [
                request.title,
                request.description,
                request.token_plan,
                request.grant_plan,
                request.target_users,
            ]
        ).lower()

    def _score_dimension(self, text: str, dimension: ReviewDimension) -> DimensionScore:
        keyword_hits = sum(1 for keyword in dimension.positive_keywords if keyword.lower() in text)
        keyword_score = min(55, keyword_hits * 8)

        pattern_hits = sum(
            1 for pattern in dimension.required_patterns if re.search(pattern, text, re.IGNORECASE)
        )
        pattern_score = int((pattern_hits / len(dimension.required_patterns)) * 35)

        length_score = min(10, len(text) // 180)
        score = min(100, keyword_score + pattern_score + length_score)
        summary = dimension.success_summary if score >= 70 else dimension.missing_summary

        return DimensionScore(
            name=dimension.name,
            score=score,
            weight=dimension.weight,
            summary=summary,
        )

    def _build_issues(self, scores: list[DimensionScore]) -> list[Issue]:
        issues: list[Issue] = []
        for score in scores:
            if score.score >= 70:
                continue
            severity = "high" if score.score < 45 else "medium"
            issues.append(
                Issue(
                    dimension=score.name,
                    severity=severity,
                    message=score.summary,
                )
            )
        return issues

    def _build_suggestions(
        self, scores: list[DimensionScore], request: ReviewRequest
    ) -> list[Suggestion]:
        suggestions: list[Suggestion] = []
        low_dimensions = {score.name for score in scores if score.score < 70}

        if "core_pain_point" in low_dimensions:
            suggestions.append(
                Suggestion(
                    dimension="core_pain_point",
                    action=(
                        "Add one sentence that states the current review bottleneck, "
                        "affected users, and cost of repeated revisions."
                    ),
                )
            )
        if "agent_workflow" in low_dimensions:
            suggestions.append(
                Suggestion(
                    dimension="agent_workflow",
                    action=(
                        "Describe the chain: draft intake, rule or LLM analysis, "
                        "issue detection, rewrite generation, and reviewer confirmation."
                    ),
                )
            )
        if "measurable_outcome" in low_dimensions:
            suggestions.append(
                Suggestion(
                    dimension="measurable_outcome",
                    action=(
                        "Add baseline and target metrics, such as preparation time, "
                        "review pass rate, or number of returned submissions."
                    ),
                )
            )
        if "token_budget" in low_dimensions:
            suggestions.append(
                Suggestion(
                    dimension="token_budget",
                    action=(
                        "Estimate monthly usage by users, submissions per user, "
                        "average tokens per review, and expected optimization strategy."
                    ),
                )
            )
        if "risk_control" in low_dimensions:
            suggestions.append(
                Suggestion(
                    dimension="risk_control",
                    action=(
                        "Mention manual confirmation, logging, privacy filtering, "
                        "and rollback for generated text."
                    ),
                )
            )
        return suggestions

    def _rewrite(
        self, request: ReviewRequest, scores: list[DimensionScore], overall_score: int
    ) -> str:
        title = request.title.strip() or "AI Review Agent"
        token_plan = request.token_plan.strip() or (
            "预计每月服务 20 名内部用户，每人提交 10 次材料预审，单次消耗约 2.5 万 tokens，"
            "月度总量约 500 万 tokens。通过规则预筛、摘要压缩和结果缓存控制消耗。"
        )
        grant_plan = (
            request.grant_plan.strip() or "申请小额试点额度用于覆盖首月评审、重写和日志分析调用。"
        )
        target_users = request.target_users.strip() or "AI 项目负责人、产品经理和内部评审支持团队"
        weak_dimensions = ", ".join(score.name for score in scores if score.score < 70) or "none"

        return (
            f"我构建了一个名为「{title}」的 AI 项目预评审 Agent，用于提升内部 AI/Agent "
            f"项目材料的评估通过率。项目解决的核心痛点是：项目负责人在填写申报材料、token plan "
            f"和效果说明时，经常缺少明确痛点、完整逻辑链和可验证指标，导致评审返工、沟通成本增加。"
            f"\n\n该 Agent 会读取项目描述、预算计划和目标用户信息，按「痛点清晰度、Agent 工作流、"
            f"量化结果、token 预算、风险控制」五个维度进行评分。核心流程包括：材料解析、规则检查、"
            f"长链推理式问题定位、改写建议生成、提交稿重写和人工确认。对于低分维度，系统会输出具体修改动作，"
            f"例如补充基线指标、拆解 token 计算方式、增加隐私与人工审核说明。"
            f"\n\n当前目标用户为：{target_users}。{token_plan}{grant_plan}"
            f" 试点阶段以评审通过率、单份材料修改耗时、返工次数和 tokens 单次成本作为评估指标，"
            f"目标是将材料准备时间从约 2 小时降低到 20 分钟以内，"
            f"并将预审后的一次通过率提升到 80% 以上。"
            f"\n\n本次自动预审评分为 {overall_score}/100，仍需重点优化的维度为：{weak_dimensions}。"
        )

    def _readiness(self, overall_score: int, issues: list[Issue]) -> Readiness:
        has_high_issue = any(issue.severity == "high" for issue in issues)
        if overall_score >= 85 and not has_high_issue:
            return Readiness.READY_TO_SUBMIT
        if overall_score >= 65:
            return Readiness.READY_WITH_MINOR_EDITS
        return Readiness.NEEDS_MAJOR_REVISION

    def _dimension_by_name(self, name: str) -> ReviewDimension:
        for dimension in DIMENSIONS:
            if dimension.name == name:
                return dimension
        raise ValueError(f"Unknown dimension: {name}")
