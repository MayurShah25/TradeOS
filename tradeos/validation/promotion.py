"""Deterministic promotion-stage transition contracts."""

from dataclasses import dataclass
from enum import StrEnum

from tradeos.validation.evidence import PromotionEligibility
from tradeos.validation.review import PromotionReview, PromotionReviewDecision


class PromotionStage(StrEnum):
    """Governed strategy lifecycle stages; none is live execution authority."""

    RESEARCH = "RESEARCH"
    BACKTEST = "BACKTEST"
    VALIDATION = "VALIDATION"
    PAPER = "PAPER"
    CONTROLLED_PROMOTION = "CONTROLLED_PROMOTION"


_ALLOWED_TRANSITIONS: dict[PromotionStage, tuple[PromotionStage, ...]] = {
    PromotionStage.RESEARCH: (PromotionStage.BACKTEST,),
    PromotionStage.BACKTEST: (PromotionStage.VALIDATION,),
    PromotionStage.VALIDATION: (PromotionStage.PAPER,),
    PromotionStage.PAPER: (PromotionStage.CONTROLLED_PROMOTION,),
    PromotionStage.CONTROLLED_PROMOTION: (),
}


@dataclass(frozen=True, slots=True)
class PromotionStageTransition:
    """Immutable result of one explicitly authorized governance stage transition."""

    transition_id: str
    review_id: str
    evidence_id: str
    strategy_id: str
    strategy_version: str
    from_stage: PromotionStage
    to_stage: PromotionStage

    def __post_init__(self) -> None:
        for name, value in (
            ("transition_id", self.transition_id),
            ("review_id", self.review_id),
            ("evidence_id", self.evidence_id),
            ("strategy_id", self.strategy_id),
            ("strategy_version", self.strategy_version),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be blank")
        if self.to_stage not in _ALLOWED_TRANSITIONS[self.from_stage]:
            raise ValueError("promotion stage transition is not allowed")


def transition_from_review(
    *,
    transition_id: str,
    review: PromotionReview,
    from_stage: PromotionStage,
    to_stage: PromotionStage,
) -> PromotionStageTransition:
    """Create one deterministic stage transition from an approved governance review."""
    if review.decision is not PromotionReviewDecision.APPROVED_FOR_NEXT_STAGE:
        raise ValueError("only an approved review can create a promotion transition")
    if review.eligibility is not PromotionEligibility.ELIGIBLE_FOR_REVIEW:
        raise ValueError("ineligible review cannot create a promotion transition")
    if to_stage not in _ALLOWED_TRANSITIONS[from_stage]:
        raise ValueError("promotion stage transition is not allowed")
    return PromotionStageTransition(
        transition_id=transition_id,
        review_id=review.review_id,
        evidence_id=review.evidence_id,
        strategy_id=review.strategy_id,
        strategy_version=review.strategy_version,
        from_stage=from_stage,
        to_stage=to_stage,
    )


def allowed_next_stages(stage: PromotionStage) -> tuple[PromotionStage, ...]:
    """Return the explicitly allowed next stages."""
    return _ALLOWED_TRANSITIONS[stage]
