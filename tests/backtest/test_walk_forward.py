"""Tests for deterministic Phase 4 walk-forward validation."""

from datetime import UTC, datetime, timedelta

import pytest

from tradeos.backtest import BacktestRequest, ExecutionCostModel
from tradeos.backtest.walk_forward import WalkForwardRequest, WalkForwardValidator
from tradeos.strategy import HistoricalBar, Signal


class FixedSignalStrategy:
    """Small deterministic strategy fixture for walk-forward tests."""

    strategy_id = "fixed-signal"
    version = "1.0.0"

    def signal(self, history: tuple[HistoricalBar, ...] | list[HistoricalBar]) -> Signal:
        """Buy on the fourth bar and sell on the fifth bar."""
        if len(history) == 4:
            return Signal.BUY
        if len(history) == 5:
            return Signal.SELL
        return Signal.HOLD


def bars() -> tuple[HistoricalBar, ...]:
    """Build a deterministic series with two out-of-sample windows."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    prices = (10.0, 10.0, 10.0, 10.0, 12.0, 12.0, 12.0)
    return tuple(
        HistoricalBar(start + timedelta(days=index), price, price, price, price, 100.0)
        for index, price in enumerate(prices)
    )


def test_walk_forward_runs_sequential_out_of_sample_folds() -> None:
    request = BacktestRequest(bars(), initial_capital=100.0)
    validation = WalkForwardRequest(warmup_bars=3, test_bars=2, step_bars=2)

    folds = WalkForwardValidator().run(request, FixedSignalStrategy(), validation)

    assert len(folds) == 2
    assert (folds[0].train_end_index, folds[0].test_start_index, folds[0].test_end_index) == (
        2,
        3,
        5,
    )
    assert (folds[1].train_end_index, folds[1].test_start_index, folds[1].test_end_index) == (
        4,
        5,
        7,
    )
    assert folds[0].result.trades[0].entry_price == 10.0
    assert folds[0].result.trades[0].exit_price == 12.0
    assert folds[1].result.trades == ()


def test_walk_forward_preserves_cost_model_and_capital() -> None:
    request = BacktestRequest(
        bars(),
        initial_capital=250.0,
        cost_model=ExecutionCostModel(commission_per_order=0.5),
    )
    validation = WalkForwardRequest(warmup_bars=3, test_bars=2, step_bars=2)

    folds = WalkForwardValidator().run(request, FixedSignalStrategy(), validation)

    assert folds[0].result.initial_capital == 250.0
    assert folds[0].result.trades[0].commission == 1.0
    assert folds[0].result.trades[0].net_pnl == 1.0


@pytest.mark.parametrize(
    ("warmup_bars", "test_bars", "step_bars"),
    [(0, 2, 1), (2, 0, 1), (2, 1, 0)],
)
def test_walk_forward_rejects_invalid_window_configuration(
    warmup_bars: int, test_bars: int, step_bars: int
) -> None:
    with pytest.raises(ValueError):
        WalkForwardRequest(warmup_bars, test_bars, step_bars)


def test_walk_forward_rejects_insufficient_warmup_data() -> None:
    request = BacktestRequest(bars()[:3])
    validation = WalkForwardRequest(warmup_bars=3, test_bars=1, step_bars=1)

    with pytest.raises(ValueError, match="warmup"):
        WalkForwardValidator().run(request, FixedSignalStrategy(), validation)
