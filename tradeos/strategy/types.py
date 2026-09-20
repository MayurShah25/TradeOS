"""Shared deterministic strategy types for TradeOS Phase 4."""

from datetime import datetime
from enum import StrEnum
from typing import NamedTuple


class Signal(StrEnum):
    """Action requested by a deterministic strategy."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class HistoricalBar(NamedTuple):
    """Immutable historical OHLCV bar."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
