"""Tests for immutable validation evidence and promotion eligibility."""

from datetime import UTC, datetime

import pytest

from tradeos.validation import (
    PromotionEligibility,
    ValidationEvidence,
    ValidationStage,
    evaluate_promotion_eligibility,
)


def evidence(
    gates: tuple[tuple[ValidationStage, bool], ...],
) -> ValidationEvidence:
    """Build deterministic validation evidence."""
    return ValidationEvidence(
        evidence_id="evidence-1",
        strategy_id="moving-average-cross",
        strategy_version="1.0.0",
        dataset_version="dataset-1",
        configuration_version="config-1",
        code_version="commit-1",
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        gate_results=gates,
    )


def test_all_required_gates_must_pass_for_review_eligibility() -> None:
    result = evaluate_promotion_eligibility(
        evidence(
            (
                (ValidationStage.BACKTEST, True),
                (ValidationStage.ROBUSTNESS, True),
                (ValidationStage.OUT_OF_SAMPLE, True),
                (ValidationStage.WALK_FORWARD, True),
            )
        ),
        (
            ValidationStage.BACKTEST,
            ValidationStage.ROBUSTNESS,
            ValidationStage.OUT_OF_SAMPLE,
            ValidationStage.WALK_FORWARD,
        ),
    )

    assert result is PromotionEligibility.ELIGIBLE_FOR_REVIEW


def test_missing_gate_is_not_a_pass() -> None:
    result = evaluate_promotion_eligibility(
        evidence(((ValidationStage.BACKTEST, True),)),
        (ValidationStage.BACKTEST, ValidationStage.WALK_FORWARD),
    )

    assert result is PromotionEligibility.NOT_ELIGIBLE


def test_failed_gate_is_not_eligible() -> None:
    result = evaluate_promotion_eligibility(
        evidence(
            (
                (ValidationStage.BACKTEST, True),
                (ValidationStage.WALK_FORWARD, False),
            )
        ),
        (ValidationStage.BACKTEST, ValidationStage.WALK_FORWARD),
    )

    assert result is PromotionEligibility.NOT_ELIGIBLE


def test_duplicate_gate_stage_is_rejected() -> None:
    with pytest.raises(ValueError, match="unique validation stages"):
        evidence(
            (
                (ValidationStage.BACKTEST, True),
                (ValidationStage.BACKTEST, True),
            )
        )


def test_duplicate_required_stage_is_rejected() -> None:
    with pytest.raises(ValueError, match="required validation stages"):
        evaluate_promotion_eligibility(
            evidence(((ValidationStage.BACKTEST, True),)),
            (ValidationStage.BACKTEST, ValidationStage.BACKTEST),
        )


def test_evidence_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ValidationEvidence(
            evidence_id="evidence-1",
            strategy_id="strategy-1",
            strategy_version="1.0.0",
            dataset_version="dataset-1",
            configuration_version="config-1",
            code_version="commit-1",
            generated_at=datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None),
            gate_results=((ValidationStage.BACKTEST, True),),
        )
