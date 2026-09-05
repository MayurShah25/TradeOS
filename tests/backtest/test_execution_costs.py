"""Tests for deterministic Phase 4 backtest execution costs."""

from datetime import UTC, datetime, timedelta

import pytest

from tradeos.backtest import (
    BacktestEngine,
    BacktestRequest,
    BacktestResult,
    ExecutionCostModel,
    calculate_metrics,
)
from tradeos.strategy import HistoricalBar, MovingAverageCrossStrategy


def bars(closes: list[float]) -> tuple[HistoricalBar, ...]:
    """Build timestamped historical bars from close prices."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return tuple(
        HistoricalBar(start + timedelta(days=index), close, close, close, close, 100.0)
        for index, close in enumerate(closes)
    )


def run_trade(cost_model: ExecutionCostModel) -> BacktestResult:
    """Run the deterministic fixture with the supplied execution costs."""
    request = BacktestRequest(
        bars([3, 3, 2, 4, 4, 3, 5]),
        initial_capital=100.0,
        cost_model=cost_model,
    )
    return BacktestEngine().run(request, MovingAverageCrossStrategy(short_window=2, long_window=3))


def test_zero_cost_preserves_raw_and_effective_prices() -> None:
    result = run_trade(ExecutionCostModel())
    trade = result.trades[0]

    assert trade.entry_price == 4
    assert trade.exit_price == 3
    assert trade.effective_entry_price == 4
    assert trade.effective_exit_price == 3
    assert trade.commission == 0
    assert trade.net_pnl == -1


def test_commission_only_costs_reduce_realized_pnl() -> None:
    result = run_trade(ExecutionCostModel(commission_per_order=0.5))

    assert result.trades[0].commission == 1.0
    assert result.trades[0].effective_entry_price == 4
    assert result.trades[0].effective_exit_price == 3
    assert calculate_metrics(result).realized_pnl == -2.0


def test_slippage_only_costs_reduce_realized_pnl() -> None:
    result = run_trade(ExecutionCostModel(slippage_bps=100))
    trade = result.trades[0]

    assert trade.effective_entry_price == 4.04
    assert trade.effective_exit_price == 2.97
    assert trade.commission == 0
    assert trade.net_pnl == pytest.approx(-1.07)
    assert calculate_metrics(result).realized_pnl == pytest.approx(-1.07)


def test_combined_commission_and_slippage_are_applied() -> None:
    result = run_trade(ExecutionCostModel(commission_per_order=0.5, slippage_bps=100))
    trade = result.trades[0]

    assert trade.effective_entry_price == 4.04
    assert trade.effective_exit_price == 2.97
    assert trade.commission == 1.0
    assert trade.net_pnl == pytest.approx(-2.07)
    assert calculate_metrics(result).realized_pnl == pytest.approx(-2.07)


def test_execution_cost_model_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="commission_per_order"):
        ExecutionCostModel(commission_per_order=-0.01)
    with pytest.raises(ValueError, match="slippage_bps"):
        ExecutionCostModel(slippage_bps=10_001)


def test_execution_costs_are_deterministic_across_repeated_runs() -> None:
    cost_model = ExecutionCostModel(commission_per_order=0.5, slippage_bps=100)

    first = run_trade(cost_model)
    second = run_trade(cost_model)

    assert first == second
    assert calculate_metrics(first) == calculate_metrics(second)
