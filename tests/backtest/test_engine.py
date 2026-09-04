"""Tests for the deterministic Phase 4 backtest engine."""

from datetime import UTC, datetime, timedelta

from tradeos.backtest import BacktestEngine, BacktestRequest
from tradeos.strategy import HistoricalBar, MovingAverageCrossStrategy


def bars(closes: list[float]) -> tuple[HistoricalBar, ...]:
    """Build timestamped historical bars from close prices."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return tuple(
        HistoricalBar(start + timedelta(days=index), close, close, close, close, 100.0)
        for index, close in enumerate(closes)
    )


def test_backtest_records_buy_then_sell_as_one_trade() -> None:
    request = BacktestRequest(bars([3, 3, 2, 4, 4, 3, 5]))
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.entry_price == 4
    assert trade.exit_price == 3
    assert result.position_open is False
    assert result.open_entry_timestamp is None
    assert result.open_entry_price is None


def test_backtest_preserves_open_long_position_when_no_sell_occurs() -> None:
    request = BacktestRequest(bars([3, 3, 2, 4]))
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    assert result.trades == ()
    assert result.position_open is True
    assert result.open_entry_price == 4


def test_backtest_ignores_repeated_buy_and_sell_while_flat() -> None:
    request = BacktestRequest(bars([3, 3, 2, 4, 4, 3, 5, 5]))
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)
    first = BacktestEngine().run(request, strategy)
    second = BacktestEngine().run(request, strategy)

    assert first == second
    assert len(first.trades) == 1
    assert first.trades[0].entry_price == 4
    assert first.trades[0].exit_price == 3


def test_backtest_returns_empty_result_for_insufficient_history() -> None:
    request = BacktestRequest(bars([10, 11]))
    result = BacktestEngine().run(
        request, MovingAverageCrossStrategy(short_window=2, long_window=3)
    )

    assert result.trades == ()
    assert result.position_open is False
