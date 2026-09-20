"""Governance review records for validation evidence."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from tradeos.validation.evidence import PromotionEligibility, ValidationEvidence


class PromotionReviewDecision(StrEnum):
    """Governance decision recorded against validation evidence."""

    PENDING = "PENDING"
    APPROVED_FOR_NEXT_STAGE = "APPROVED_FOR_NEXT_STAGE"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class PromotionReview:
    """Immutable governance handoff record; never an execution authorization."""

    review_id: str
    evidence_id: str
    strategy_id: str
    strategy_version: str
    eligibility: PromotionEligibility
    decision: PromotionReviewDecision
    reviewer_id: str | None
    reviewed_at: datetime | None
    rationale: str

    def __post_init__(self) -> None:
        if not self.review_id.strip():
            raise ValueError("review_id must not be blank")
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be blank")
        if not self.strategy_id.strip():
            raise ValueError("strategy_id must not be blank")
        if not self.strategy_version.strip():
            raise ValueError("strategy_version must not be blank")
        if self.decision is PromotionReviewDecision.PENDING:
            if self.reviewer_id is not None or self.reviewed_at is not None:
                raise ValueError("pending review cannot have reviewer metadata")
        else:
            if not self.reviewer_id or not self.reviewer_id.strip():
                raise ValueError("completed review requires reviewer_id")
            if self.reviewed_at is None or self.reviewed_at.tzinfo is None:
                raise ValueError("completed review requires timezone-aware reviewed_at")
            if self.reviewed_at.tzinfo is not UTC:
                raise ValueError("reviewed_at must use UTC")
        if self.eligibility is PromotionEligibility.NOT_ELIGIBLE and (
            self.decision is PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE
        ):
            raise ValueError("ineligible evidence cannot be approved for next stage")
        if not self.rationale.strip():
            raise ValueError("rationale must not be blank")

    @classmethod
    def pending(cls, review_id: str, evidence: ValidationEvidence) -> "PromotionReview":
        """Create a review handoff without granting approval."""
        from tradeos.validation.evidence import evaluate_promotion_eligibility

        eligibility = evaluate_promotion_eligibility(
            evidence,
            tuple(stage for stage, _ in evidence.gate_results),
        )
        return cls(
            review_id=review_id,
            evidence_id=evidence.evidence_id,
            strategy_id=evidence.strategy_id,
            strategy_version=evidence.strategy_version,
            eligibility=eligibility,
            decision=PromotionReviewDecision.PENDING,
            reviewer_id=None,
            reviewed_at=None,
            rationale="Awaiting governance review.",
        )
