"""Tests for deterministic walk-forward validation gates."""

from dataclasses import replace

import pytest

from tradeos.backtest.walk_forward_analytics import calculate_walk_forward_metrics
from tradeos.backtest.walk_forward_validation import (
    WalkForwardValidationConfig,
    evaluate_walk_forward_gate,
)
from tests.backtest.test_walk_forward_analytics import walk_forward_folds


def test_walk_forward_gate_passes_when_all_thresholds_are_met() -> None:
    metrics = calculate_walk_forward_metrics(walk_forward_folds())
    config = WalkForwardValidationConfig(
        min_fold_count=2,
        min_total_return=0.01,
        max_drawdown=0.01,
        min_win_rate=0.5,
        min_profit_factor=1.0,
        min_profitable_fold_ratio=0.5,
    )

    result = evaluate_walk_forward_gate(metrics, config)

    assert result.passed is True
    assert result.failure_reasons == ()


def test_walk_forward_gate_returns_all_failed_thresholds_deterministically() -> None:
    metrics = replace(
        calculate_walk_forward_metrics(walk_forward_folds()),
        max_drawdown=0.5,
        profit_factor=0.5,
    )
    config = WalkForwardValidationConfig(
        min_fold_count=3,
        min_total_return=0.03,
        max_drawdown=0.25,
        min_win_rate=1.0,
        min_profit_factor=1.0,
        min_profitable_fold_ratio=1.0,
    )

    result = evaluate_walk_forward_gate(metrics, config)

    assert result.passed is False
    assert result.failure_reasons == (
        "fold_count 2 is below minimum 3",
        "total_return 0.02 is below minimum 0.03",
        "max_drawdown 0.5 exceeds maximum 0.25",
        "profit_factor 0.5 is below minimum 1.0",
        "profitable_fold_ratio 0.5 is below minimum 1.0",
    )


def test_walk_forward_gate_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError, match="min_fold_count"):
        WalkForwardValidationConfig(min_fold_count=0)
    with pytest.raises(ValueError, match="max_drawdown"):
        WalkForwardValidationConfig(max_drawdown=-0.01)
    with pytest.raises(ValueError, match="min_win_rate"):
        WalkForwardValidationConfig(min_win_rate=1.1)
    with pytest.raises(ValueError, match="min_profit_factor"):
        WalkForwardValidationConfig(min_profit_factor=-1.0)
    with pytest.raises(ValueError, match="min_profitable_fold_ratio"):
        WalkForwardValidationConfig(min_profitable_fold_ratio=1.1)
