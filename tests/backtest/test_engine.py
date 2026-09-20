"""Tests for the deterministic Phase 4 backtest engine."""

from datetime import UTC, datetime, timedelta

from tradeos.backtest import BacktestEngine, BacktestRequest
from tradeos.strategy import HistoricalBar, Signal


class FixedSignalStrategy:
    """Small deterministic strategy fixture for engine tests."""

    strategy_id = "fixed-signal"
    version = "1.0.0"

    def signal(self, history: list[HistoricalBar]) -> Signal:
        """Emit deterministic signals from history length."""
        if len(history) == 5:
            return Signal.BUY
        if len(history) == 6:
            return Signal.SELL
        return Signal.HOLD


class MultiTradeStrategy:
    """Deterministic fixture with two independent round trips."""

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


def test_backtest_records_buy_then_sell_as_one_trade() -> None:
    request = BacktestRequest(
        bars([10, 10, 10, 10, 10, 10, 10], opens=[10, 10, 10, 10, 10, 4, 3])
    )
    result = BacktestEngine().run(request, FixedSignalStrategy())

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.entry_price == 4
    assert trade.exit_price == 3
    assert result.position_open is False
    assert result.open_entry_timestamp is None
    assert result.open_entry_price is None


def test_backtest_preserves_open_long_position_when_no_sell_occurs() -> None:
    request = BacktestRequest(
        bars([10, 10, 10, 10, 10, 10], opens=[10, 10, 10, 10, 10, 4])
    )
    result = BacktestEngine().run(request, FixedSignalStrategy())

    assert result.trades == ()
    assert result.position_open is True
    assert result.open_entry_price == 4


def test_backtest_ignores_repeated_buy_and_sell_while_flat() -> None:
    request = BacktestRequest(
        bars(
            [10] * 12,
            opens=[10, 10, 10, 10, 10, 4, 3, 10, 10, 5, 10, 2],
        )
    )
    strategy = MultiTradeStrategy()
    first = BacktestEngine().run(request, strategy)
    second = BacktestEngine().run(request, strategy)

    assert first == second
    assert len(first.trades) == 2
    assert first.trades[0].entry_price == 4
    assert first.trades[0].exit_price == 3
    assert first.trades[1].entry_price == 5
    assert first.trades[1].exit_price == 2


def test_backtest_does_not_use_current_bar_for_signal_generation() -> None:
    class CloseTriggeredStrategy:
        strategy_id = "close-triggered"
        version = "1.0.0"

        def signal(self, history: list[HistoricalBar]) -> Signal:
            return Signal.BUY if history and history[-1].close > 100 else Signal.HOLD

    request = BacktestRequest(bars([100, 200, 200], opens=[100, 190, 195]))

    result = BacktestEngine().run(request, CloseTriggeredStrategy())

    assert result.open_entry_timestamp == request.bars[2].timestamp
    assert result.open_entry_price == 195


def test_backtest_returns_empty_result_for_insufficient_history() -> None:
    request = BacktestRequest(bars([10, 11]))
    result = BacktestEngine().run(request, FixedSignalStrategy())

    assert result.trades == ()
    assert result.position_open is False
