"""Tests for the validation promotion review boundary."""

from datetime import UTC, datetime

import pytest

from tradeos.validation import (
    PromotionEligibility,
    PromotionReview,
    PromotionReviewDecision,
    ValidationEvidence,
    ValidationStage,
)


def evidence(passed: bool = True) -> ValidationEvidence:
    return ValidationEvidence(
        evidence_id="evidence-1",
        strategy_id="strategy-1",
        strategy_version="1.0.0",
        dataset_version="dataset-1",
        configuration_version="config-1",
        code_version="commit-1",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        gate_results=((ValidationStage.BACKTEST, passed),),
    )


def test_pending_review_is_derived_from_evidence() -> None:
    review = PromotionReview.pending("review-1", evidence())

    assert review.eligibility is PromotionEligibility.ELIGIBLE_FOR_REVIEW
    assert review.decision is PromotionReviewDecision.PENDING
    assert review.reviewer_id is None


def test_ineligible_evidence_cannot_be_approved() -> None:
    with pytest.raises(ValueError, match="ineligible"):
        PromotionReview(
            review_id="review-1",
            evidence_id="evidence-1",
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            eligibility=PromotionEligibility.NOT_ELIGIBLE,
            decision=PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE,
            reviewer_id="reviewer-1",
            reviewed_at=datetime(2026, 1, 2, tzinfo=UTC),
            rationale="Approval.",
        )


def test_completed_review_requires_reviewer_and_utc_timestamp() -> None:
    with pytest.raises(ValueError, match="reviewer_id"):
        PromotionReview(
            review_id="review-1",
            evidence_id="evidence-1",
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            eligibility=PromotionEligibility.ELIGIBLE_FOR_REVIEW,
            decision=PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE,
            reviewer_id=None,
            reviewed_at=datetime(2026, 1, 2, tzinfo=UTC),
            rationale="Approval.",
        )


def test_pending_review_cannot_be_self_completed() -> None:
    with pytest.raises(ValueError, match="pending"):
        PromotionReview(
            review_id="review-1",
            evidence_id="evidence-1",
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            eligibility=PromotionEligibility.ELIGIBLE_FOR_REVIEW,
            decision=PromotionReviewDecision.PENDING,
            reviewer_id="strategy-agent",
            reviewed_at=None,
            rationale="Approval.",
        )
