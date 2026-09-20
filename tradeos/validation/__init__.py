"""Validation evidence, governance review, and promotion contracts."""

from tradeos.validation.builders import (
    BacktestValidationConfig,
    OutOfSampleValidationConfig,
    RobustnessValidationConfig,
    build_validation_evidence,
    evaluate_backtest_gate,
    evaluate_out_of_sample_gate,
    evaluate_robustness_gate,
)
from tradeos.validation.evidence import (
    PromotionEligibility,
    ValidationEvidence,
    ValidationStage,
    evaluate_promotion_eligibility,
)
from tradeos.validation.in_memory_promotion_repository import InMemoryPromotionTransitionRepository
from tradeos.validation.in_memory_repository import InMemoryValidationEvidenceRepository
from tradeos.validation.in_memory_review_repository import InMemoryPromotionReviewRepository
from tradeos.validation.promotion import (
    PromotionStage,
    PromotionStageTransition,
    allowed_next_stages,
    transition_from_review,
)
from tradeos.validation.promotion_audit import (
    PromotionTransitionAuditEvent,
    PromotionTransitionAuditEventType,
)
from tradeos.validation.promotion_repository import PromotionTransitionRepository
from tradeos.validation.repository import ValidationEvidenceRepository
from tradeos.validation.review import PromotionReview, PromotionReviewDecision
from tradeos.validation.review_audit import (
    PromotionReviewAuditEvent,
    PromotionReviewAuditEventType,
)
from tradeos.validation.review_repository import PromotionReviewRepository

__all__ = [
    "BacktestValidationConfig",
    "InMemoryPromotionReviewRepository",
    "InMemoryPromotionTransitionRepository",
    "InMemoryValidationEvidenceRepository",
    "OutOfSampleValidationConfig",
    "PromotionEligibility",
    "PromotionReview",
    "PromotionReviewAuditEvent",
    "PromotionReviewAuditEventType",
    "PromotionReviewDecision",
    "PromotionReviewRepository",
    "PromotionStage",
    "PromotionStageTransition",
    "PromotionTransitionAuditEvent",
    "PromotionTransitionAuditEventType",
    "PromotionTransitionRepository",
    "RobustnessValidationConfig",
    "ValidationEvidence",
    "ValidationEvidenceRepository",
    "ValidationStage",
    "allowed_next_stages",
    "build_validation_evidence",
    "evaluate_backtest_gate",
    "evaluate_out_of_sample_gate",
    "evaluate_promotion_eligibility",
    "evaluate_robustness_gate",
    "transition_from_review",
]
