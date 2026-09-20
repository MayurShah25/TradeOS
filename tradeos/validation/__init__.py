"""Validation evidence and governance review contracts."""

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
from tradeos.validation.in_memory_repository import InMemoryValidationEvidenceRepository
from tradeos.validation.in_memory_review_repository import InMemoryPromotionReviewRepository
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
    "InMemoryValidationEvidenceRepository",
    "OutOfSampleValidationConfig",
    "PromotionEligibility",
    "PromotionReview",
    "PromotionReviewAuditEvent",
    "PromotionReviewAuditEventType",
    "PromotionReviewDecision",
    "PromotionReviewRepository",
    "RobustnessValidationConfig",
    "ValidationEvidence",
    "ValidationEvidenceRepository",
    "ValidationStage",
    "build_validation_evidence",
    "evaluate_backtest_gate",
    "evaluate_out_of_sample_gate",
    "evaluate_promotion_eligibility",
    "evaluate_robustness_gate",
]
