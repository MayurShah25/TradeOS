from datetime import UTC, datetime
from decimal import Decimal

from tradeos.market import AssetClass, Instrument, MarketStatus, Quote


def test_instrument_and_quote_models() -> None:
    instrument = Instrument(
        instrument_id="US-EQUITY:AAPL",
        symbol="AAPL",
        asset_class=AssetClass.EQUITY,
        exchange="NASDAQ",
        currency="USD",
    )
    quote = Quote(
        instrument_id=instrument.instrument_id,
        bid=Decimal("199.90"),
        ask=Decimal("200.10"),
        timestamp=datetime.now(UTC),
    )

    assert instrument.symbol == "AAPL"
    assert instrument.asset_class is AssetClass.EQUITY
    assert quote.mid == Decimal("200.00")
    assert MarketStatus.OPEN.value == "OPEN"
