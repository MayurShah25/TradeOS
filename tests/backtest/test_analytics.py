"""Tests for deterministic Phase 4 backtest analytics."""

from datetime import UTC, datetime, timedelta

import pytest

from tradeos.backtest import BacktestEngine, BacktestRequest, calculate_metrics
from tradeos.strategy import HistoricalBar, Signal


class FixedSignalStrategy:
    """Small deterministic strategy fixture for analytics tests."""

    strategy_id = "fixed-signal"
    version = "1.0.0"

    def signal(self, history: list[HistoricalBar]) -> Signal:
        """Buy on the sixth bar and sell on the seventh bar."""
        if len(history) == 5:
            return Signal.BUY
        if len(history) == 6:
            return Signal.SELL
        return Signal.HOLD


class MultiTradeStrategy:
    """Deterministic fixture with two losing round trips."""

    strategy_id = "multi-trade"
    version = "1.0.0"

    def signal(self, history: list[HistoricalBar]) -> Signal:
        """Emit two deterministic buy/sell pairs."""
        if len(history) in (5, 9):
            return Signal.BUY
        if len(history) in (6, 11):
            return Signal.SELL
        return Signal.HOLD


def bars(
    closes: list[float], opens: list[float] | None = None
) -> tuple[HistoricalBar, ...]:
    """Build timestamped historical bars from close prices and optional opens."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    open_prices = opens or closes
    return tuple(
        HistoricalBar(
            start + timedelta(days=index),
            open_price,
            close,
            open_price,
            open_price,
            100.0,
        )
        for index, (open_price, close) in enumerate(zip(open_prices, closes, strict=True))
    )


def test_backtest_metrics_calculate_pnl_return_and_win_rate() -> None:
    request = BacktestRequest(
        bars([10, 10, 10, 10, 10, 10, 10], opens=[10, 10, 10, 10, 10, 4, 3]),
        initial_capital=100.0,
    )
    result = BacktestEngine().run(request, FixedSignalStrategy())

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 1
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 1
    assert metrics.gross_profit == 0.0
    assert metrics.gross_loss == 1.0
    assert metrics.realized_pnl == -1.0
    assert metrics.total_return == -0.01
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == 0.0
    assert metrics.average_trade_pnl == -1.0
    assert metrics.equity_curve == (100.0, 99.0)
    assert metrics.drawdown_curve == (0.0, 1.0)
    assert metrics.max_drawdown == 1.0


def test_backtest_metrics_aggregate_multiple_trades() -> None:
    request = BacktestRequest(
        bars(
            [10] * 12,
            opens=[10, 10, 10, 10, 10, 4, 3, 10, 10, 5, 10, 2],
        ),
        initial_capital=100.0,
    )
    result = BacktestEngine().run(request, MultiTradeStrategy())

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 2
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 2
    assert metrics.gross_profit == 0.0
    assert metrics.gross_loss == 3.0
    assert metrics.realized_pnl == -3.0
    assert metrics.total_return == -0.03
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == 0.0
    assert metrics.average_trade_pnl == -1.5
    assert metrics.equity_curve == (100.0, 99.0, 96.0)
    assert metrics.drawdown_curve == (0.0, 1.0, 4.0)
    assert metrics.max_drawdown == 4.0


def test_backtest_metrics_return_zeroes_for_no_closed_trades() -> None:
    request = BacktestRequest(bars([10, 11]), initial_capital=100.0)
    result = BacktestEngine().run(request, FixedSignalStrategy())

    metrics = calculate_metrics(result)

    assert metrics.trade_count == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0
    assert metrics.gross_profit == 0.0
    assert metrics.gross_loss == 0.0
    assert metrics.realized_pnl == 0.0
    assert metrics.total_return == 0.0
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == 0.0
    assert metrics.average_trade_pnl == 0.0
    assert metrics.equity_curve == (100.0,)
    assert metrics.drawdown_curve == (0.0,)
    assert metrics.max_drawdown == 0.0


def test_backtest_metrics_calculate_profit_factor_for_mixed_results() -> None:
    request = BacktestRequest(
        bars(
            [10] * 12,
            opens=[10, 10, 10, 10, 10, 4, 3, 10, 10, 5, 10, 2],
        ),
        initial_capital=100.0,
    )
    result = BacktestEngine().run(request, MultiTradeStrategy())
    first_trade, second_trade = result.trades
    mixed_result = result.__class__(
        result.strategy_id,
        result.strategy_version,
        result.initial_capital,
        (
            first_trade._replace(entry_price=1.0, exit_price=6.0),
            second_trade._replace(entry_price=4.0, exit_price=2.0),
        ),
        result.open_entry_timestamp,
        result.open_entry_price,
    )

    metrics = calculate_metrics(mixed_result)

    assert metrics.gross_profit == 5.0
    assert metrics.gross_loss == 2.0
    assert metrics.realized_pnl == 3.0
    assert metrics.win_rate == 0.5
    assert metrics.profit_factor == 2.5
    assert metrics.average_trade_pnl == 1.5
    assert metrics.equity_curve == (100.0, 105.0, 103.0)
    assert metrics.drawdown_curve == (0.0, 0.0, 2.0)


@pytest.mark.parametrize("initial_capital", [0.0, -1.0])
def test_backtest_request_rejects_non_positive_initial_capital(initial_capital: float) -> None:
    with pytest.raises(ValueError, match="initial_capital"):
        BacktestRequest((), initial_capital=initial_capital)
