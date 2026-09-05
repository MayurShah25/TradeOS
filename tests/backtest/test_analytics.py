"""Tests for deterministic Phase 4 backtest analytics."""

from datetime import UTC, datetime, timedelta

import pytest

from tradeos.backtest import BacktestEngine, BacktestRequest, calculate_metrics
from tradeos.strategy import HistoricalBar, MovingAverageCrossStrategy


def bars(closes: list[float]) -> tuple[HistoricalBar, ...]:
    """Build timestamped historical bars from close prices."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return tuple(
        HistoricalBar(start + timedelta(days=index), close, close, close, close, 100.0)
        for index, close in enumerate(closes)
    )


def test_backtest_metrics_calculate_pnl_return_and_win_rate() -> None:
    request = BacktestRequest(bars([3, 3, 2, 4, 4, 3, 5]), initial_capital=100.0)
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 1
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 1
    assert metrics.realized_pnl == -1.0
    assert metrics.total_return == -0.01
    assert metrics.win_rate == 0.0
    assert metrics.max_drawdown == 1.0


def test_backtest_metrics_aggregate_multiple_trades() -> None:
    request = BacktestRequest(bars([3, 3, 2, 4, 4, 3, 5, 5, 2, 2, 6]), initial_capital=100.0)
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 2
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 2
    assert metrics.realized_pnl == -4.0
    assert metrics.total_return == -0.04
    assert metrics.win_rate == 0.0
    assert metrics.max_drawdown == 4.0


def test_backtest_metrics_return_zeroes_for_no_closed_trades() -> None:
    request = BacktestRequest(bars([10, 11]), initial_capital=100.0)
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0
    assert metrics.realized_pnl == 0.0
    assert metrics.total_return == 0.0
    assert metrics.win_rate == 0.0
    assert metrics.max_drawdown == 0.0


@pytest.mark.parametrize("initial_capital", [0.0, -1.0])
def test_backtest_request_rejects_non_positive_initial_capital(initial_capital: float) -> None:
    with pytest.raises(ValueError, match="initial_capital"):
        BacktestRequest((), initial_capital=initial_capital)
