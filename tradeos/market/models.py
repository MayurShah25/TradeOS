"""Market-neutral value objects used at provider and broker boundaries."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class AssetClass(StrEnum):
    """Supported asset-class categories at the integration boundary."""

    EQUITY = "EQUITY"


class MarketStatus(StrEnum):
    """Normalized market status."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    HALTED = "HALTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Instrument:
    """Tradable instrument identity independent of a specific provider."""

    instrument_id: str
    symbol: str
    asset_class: AssetClass
    exchange: str
    currency: str


@dataclass(frozen=True, slots=True)
class Quote:
    """Normalized point-in-time quote."""

    instrument_id: str
    bid: Decimal
    ask: Decimal
    timestamp: datetime

    @property
    def mid(self) -> Decimal:
        """Return the midpoint between bid and ask."""
        return (self.bid + self.ask) / Decimal("2")
