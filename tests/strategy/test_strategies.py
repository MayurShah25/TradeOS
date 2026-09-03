"""Tests for deterministic Phase 4 strategies."""

from datetime import UTC, datetime

import pytest

from tradeos.strategy import HistoricalBar, MovingAverageCrossStrategy, Signal


def bar(close: float) -> HistoricalBar:
    """Build a minimal historical bar for strategy tests."""
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    return HistoricalBar(timestamp, close, close, close, close, 100.0)


def test_moving_average_cross_returns_hold_until_long_window_is_available() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)

    assert strategy.signal([bar(10), bar(11)]) is Signal.HOLD


def test_moving_average_cross_returns_buy_on_bullish_crossover() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)

    assert strategy.signal([bar(10), bar(10), bar(10), bar(12)]) is Signal.BUY


def test_moving_average_cross_returns_sell_on_bearish_crossover() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)

    assert strategy.signal([bar(10), bar(10), bar(10), bar(8)]) is Signal.SELL


def test_moving_average_cross_returns_hold_when_averages_are_equal() -> None:
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)

    assert strategy.signal([bar(9), bar(9), bar(9), bar(9)]) is Signal.HOLD


@pytest.mark.parametrize(
    ("short_window", "long_window"),
    [(0, 2), (2, 2), (3, 2)],
)
def test_moving_average_cross_rejects_invalid_windows(short_window: int, long_window: int) -> None:
    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(short_window=short_window, long_window=long_window)
