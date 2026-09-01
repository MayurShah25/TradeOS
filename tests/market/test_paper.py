from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tradeos.market import AssetClass, Instrument, MarketStatus, PaperMarketDataProvider


def test_single_equity_provider_returns_configured_data() -> None:
    provider = PaperMarketDataProvider.single_equity(
        symbol="AAPL",
        instrument_id="US-EQUITY:AAPL",
        bid=Decimal("199.90"),
        ask=Decimal("200.10"),
        timestamp=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    instrument = provider.get_instrument("AAPL")
    quote = provider.get_quote(instrument)

    assert instrument.instrument_id == "US-EQUITY:AAPL"
    assert quote.mid == Decimal(200)
    assert provider.get_market_status(instrument) is MarketStatus.OPEN


def test_unknown_symbol_is_rejected() -> None:
    provider = PaperMarketDataProvider.single_equity(
        symbol="AAPL",
        instrument_id="US-EQUITY:AAPL",
        bid=Decimal("199.90"),
        ask=Decimal("200.10"),
        timestamp=datetime(2026, 9, 1, 13, 0, tzinfo=UTC),
    )

    with pytest.raises(KeyError, match="Unknown paper instrument"):
        provider.get_instrument("MSFT")


def test_missing_quote_is_rejected() -> None:
    instrument = Instrument(
        instrument_id="US-EQUITY:AAPL",
        symbol="AAPL",
        asset_class=AssetClass.EQUITY,
        exchange="PAPER",
        currency="USD",
    )
    provider = PaperMarketDataProvider((instrument,), ())

    with pytest.raises(KeyError, match="No paper quote configured"):
        provider.get_quote(instrument)
