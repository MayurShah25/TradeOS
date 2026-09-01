"""Deterministic paper-market data adapter.

This adapter is intentionally local: it has no network access and cannot submit
orders. It provides a stable market-data seam for paper execution tests.
"""

from datetime import datetime
from decimal import Decimal

from .models import AssetClass, Instrument, MarketStatus, Quote
from .ports import MarketDataProvider


class PaperMarketDataProvider(MarketDataProvider):
    """In-memory market-data provider backed by explicit test fixtures."""

    def __init__(
        self,
        instruments: tuple[Instrument, ...],
        quotes: tuple[Quote, ...] = (),
        market_status: MarketStatus = MarketStatus.OPEN,
    ) -> None:
        self._instruments = {instrument.symbol: instrument for instrument in instruments}
        self._quotes = {quote.instrument_id: quote for quote in quotes}
        self._market_status = market_status

    def get_instrument(self, symbol: str) -> Instrument:
        """Resolve a known paper symbol or fail deterministically."""
        try:
            return self._instruments[symbol]
        except KeyError as exc:
            raise KeyError(f"Unknown paper instrument: {symbol}") from exc

    def get_quote(self, instrument: Instrument) -> Quote:
        """Return the configured quote for an instrument."""
        try:
            return self._quotes[instrument.instrument_id]
        except KeyError as exc:
            raise KeyError(f"No paper quote configured: {instrument.instrument_id}") from exc

    def get_market_status(self, instrument: Instrument) -> MarketStatus:
        """Return the configured paper-market status."""
        if instrument.asset_class is not AssetClass.EQUITY:
            return MarketStatus.UNKNOWN
        return self._market_status

    @classmethod
    def single_equity(
        cls,
        *,
        symbol: str,
        instrument_id: str,
        exchange: str = "PAPER",
        currency: str = "USD",
        bid: Decimal,
        ask: Decimal,
        timestamp: datetime,
        market_status: MarketStatus = MarketStatus.OPEN,
    ) -> "PaperMarketDataProvider":
        """Build a compact provider fixture for one equity instrument."""
        instrument = Instrument(
            instrument_id=instrument_id,
            symbol=symbol,
            asset_class=AssetClass.EQUITY,
            exchange=exchange,
            currency=currency,
        )
        quote = Quote(
            instrument_id=instrument_id,
            bid=bid,
            ask=ask,
            timestamp=timestamp,
        )
        return cls((instrument,), (quote,), market_status)
