"""Validation evidence and promotion eligibility contracts."""

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

__all__ = [
    "BacktestValidationConfig",
    "OutOfSampleValidationConfig",
    "PromotionEligibility",
    "RobustnessValidationConfig",
    "ValidationEvidence",
    "ValidationStage",
    "build_validation_evidence",
    "evaluate_backtest_gate",
    "evaluate_out_of_sample_gate",
    "evaluate_promotion_eligibility",
    "evaluate_robustness_gate",
]
