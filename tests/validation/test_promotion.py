"""Tests for deterministic promotion-stage transitions."""

from datetime import UTC, datetime

import pytest

from tradeos.validation import (
    PromotionEligibility,
    PromotionReview,
    PromotionReviewDecision,
    PromotionStage,
    PromotionStageTransition,
    allowed_next_stages,
    transition_from_review,
)


def review(
    *,
    decision: PromotionReviewDecision = PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE,
    eligibility: PromotionEligibility = PromotionEligibility.ELIGIBLE_FOR_REVIEW,
) -> PromotionReview:
    return PromotionReview(
        review_id="review-1",
        evidence_id="evidence-1",
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        eligibility=eligibility,
        decision=decision,
        reviewer_id="reviewer-1" if decision is not PromotionReviewDecision.PENDING else None,
        reviewed_at=(
            datetime(2026, 1, 2, tzinfo=UTC)
            if decision is not PromotionReviewDecision.PENDING
            else None
        ),
        rationale="Governance decision.",
    )


def test_allowed_stage_path_is_explicit() -> None:
    assert allowed_next_stages(PromotionStage.RESEARCH) == (PromotionStage.BACKTEST,)
    assert allowed_next_stages(PromotionStage.BACKTEST) == (PromotionStage.VALIDATION,)
    assert allowed_next_stages(PromotionStage.VALIDATION) == (PromotionStage.PAPER,)
    assert allowed_next_stages(PromotionStage.PAPER) == (
        PromotionStage.CONTROLLED_PROMOTION,
    )
    assert allowed_next_stages(PromotionStage.CONTROLLED_PROMOTION) == ()


def test_approved_review_creates_exact_lineage_transition() -> None:
    transition = transition_from_review(
        transition_id="transition-1",
        review=review(),
        from_stage=PromotionStage.PAPER,
        to_stage=PromotionStage.CONTROLLED_PROMOTION,
    )

    assert transition == PromotionStageTransition(
        transition_id="transition-1",
        review_id="review-1",
        evidence_id="evidence-1",
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        from_stage=PromotionStage.PAPER,
        to_stage=PromotionStage.CONTROLLED_PROMOTION,
    )


@pytest.mark.parametrize(
    ("decision", "eligibility", "match"),
    [
        (PromotionReviewDecision.PENDING, PromotionEligibility.ELIGIBLE_FOR_REVIEW, "approved"),
        (PromotionReviewDecision.REJECTED, PromotionEligibility.ELIGIBLE_FOR_REVIEW, "approved"),
        (
            PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE,
            PromotionEligibility.NOT_ELIGIBLE,
            "ineligible",
        ),
    ],
)
def test_transition_requires_approved_eligible_review(
    decision: PromotionReviewDecision,
    eligibility: PromotionEligibility,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        transition_from_review(
            transition_id="transition-1",
            review=review(decision=decision, eligibility=eligibility),
            from_stage=PromotionStage.PAPER,
            to_stage=PromotionStage.CONTROLLED_PROMOTION,
        )


def test_transition_must_follow_single_allowed_step() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        transition_from_review(
            transition_id="transition-1",
            review=review(),
            from_stage=PromotionStage.RESEARCH,
            to_stage=PromotionStage.PAPER,
        )


def test_controlled_promotion_has_no_implicit_live_stage() -> None:
    assert allowed_next_stages(PromotionStage.CONTROLLED_PROMOTION) == ()
