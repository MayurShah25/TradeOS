"""Immutable validation evidence and promotion eligibility contracts."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ValidationStage(StrEnum):
    """Validation stages that may contribute promotion evidence."""

    BACKTEST = "BACKTEST"
    ROBUSTNESS = "ROBUSTNESS"
    OUT_OF_SAMPLE = "OUT_OF_SAMPLE"
    WALK_FORWARD = "WALK_FORWARD"
    PAPER = "PAPER"


class PromotionEligibility(StrEnum):
    """Deterministic eligibility result, not execution authority."""

    ELIGIBLE_FOR_REVIEW = "ELIGIBLE_FOR_REVIEW"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


@dataclass(frozen=True, slots=True)
class ValidationEvidence:
    """Immutable evidence snapshot for one exact strategy version."""

    evidence_id: str
    strategy_id: str
    strategy_version: str
    dataset_version: str
    configuration_version: str
    code_version: str
    generated_at: datetime
    gate_results: tuple[tuple[ValidationStage, bool], ...]
    known_limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be blank")
        if not self.strategy_id.strip():
            raise ValueError("strategy_id must not be blank")
        if not self.strategy_version.strip():
            raise ValueError("strategy_version must not be blank")
        if not self.dataset_version.strip():
            raise ValueError("dataset_version must not be blank")
        if not self.configuration_version.strip():
            raise ValueError("configuration_version must not be blank")
        if not self.code_version.strip():
            raise ValueError("code_version must not be blank")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")

        stages = tuple(stage for stage, _ in self.gate_results)
        if len(stages) != len(set(stages)):
            raise ValueError("gate_results must contain unique validation stages")

    def result_for(self, stage: ValidationStage) -> bool | None:
        """Return a stage result, or None when the stage is missing."""
        for recorded_stage, passed in self.gate_results:
            if recorded_stage is stage:
                return passed
        return None


def evaluate_promotion_eligibility(
    evidence: ValidationEvidence,
    required_stages: tuple[ValidationStage, ...],
) -> PromotionEligibility:
    """Evaluate deterministic eligibility without granting approval or execution."""
    if not required_stages:
        raise ValueError("at least one required validation stage is necessary")

    if len(required_stages) != len(set(required_stages)):
        raise ValueError("required validation stages must be unique")

    if any(evidence.result_for(stage) is not True for stage in required_stages):
        return PromotionEligibility.NOT_ELIGIBLE

    return PromotionEligibility.ELIGIBLE_FOR_REVIEW
