"""Tests for deterministic walk-forward performance aggregation."""

from dataclasses import replace

import pytest

from tests.backtest.test_walk_forward import FixedSignalStrategy, bars
from tradeos.backtest import BacktestRequest
from tradeos.backtest.walk_forward import WalkForwardRequest, WalkForwardValidator
from tradeos.backtest.walk_forward_analytics import calculate_walk_forward_metrics


def walk_forward_folds():
    """Build the deterministic fold fixture used by aggregation tests."""
    request = BacktestRequest(bars(), initial_capital=100.0)
    validation = WalkForwardRequest(warmup_bars=3, test_bars=2, step_bars=2)
    return WalkForwardValidator().run(request, FixedSignalStrategy(), validation)


def test_walk_forward_metrics_aggregate_oos_folds() -> None:
    metrics = calculate_walk_forward_metrics(walk_forward_folds())

    assert metrics.fold_count == 2
    assert metrics.profitable_fold_count == 1
    assert metrics.losing_fold_count == 0
    assert metrics.total_trade_count == 1
    assert metrics.realized_pnl == 2.0
    assert metrics.total_return == 0.02
    assert metrics.win_rate == 1.0
    assert metrics.profit_factor == float("inf")
    assert metrics.average_trade_pnl == 2.0
    assert metrics.max_drawdown == 0.0
    assert metrics.mean_fold_return == 0.01
    assert metrics.worst_fold_return == 0.0
    assert metrics.fold_returns == (0.02, 0.0)


def test_walk_forward_metrics_reject_empty_folds() -> None:
    with pytest.raises(ValueError, match="at least one"):
        calculate_walk_forward_metrics(())


def test_walk_forward_metrics_reject_mismatched_initial_capital() -> None:
    folds = walk_forward_folds()
    mismatched_result = replace(folds[1].result, initial_capital=200.0)
    mismatched_folds = (folds[0], replace(folds[1], result=mismatched_result))

    with pytest.raises(ValueError, match="same initial capital"):
        calculate_walk_forward_metrics(mismatched_folds)
