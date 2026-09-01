"""Provider and broker interfaces for the first-market boundary."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol

from .models import Instrument, MarketStatus, Quote


class MarketDataProvider(ABC):
    """Provider boundary; implementations own external API semantics."""

    @abstractmethod
    def get_instrument(self, symbol: str) -> Instrument:
        """Resolve a provider symbol into a normalized instrument."""
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, instrument: Instrument) -> Quote:
        """Return the latest normalized quote for an instrument."""
        raise NotImplementedError

    @abstractmethod
    def get_market_status(self, instrument: Instrument) -> MarketStatus:
        """Return normalized market status."""
        raise NotImplementedError


class BrokerGateway(Protocol):
    """Minimal broker boundary reserved for paper-safe execution adapters."""

    def get_account_id(self) -> str:
        """Return the broker account identifier."""
        ...

    def get_positions(self) -> Sequence[object]:
        """Return broker positions for reconciliation."""
        ...
