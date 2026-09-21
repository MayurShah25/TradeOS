from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tradeos.market_data import PaperMarketDataSnapshot
from tradeos.market_data_stream import PaperMarketDataStream


def _snapshot(\n    *,\n    instrument_id: str = "NSE:RELIANCE",\n    source_id: str = "paper-feed-1",\n    minute: int = 0,\n    price: str = "2500",\n) -> PaperMarketDataSnapshot:
    return PaperMarketDataSnapshot(
        instrument_id=instrument_id,
        price=Decimal(price),
        observed_at=datetime(2026, 9, 21, 10, minute, tzinfo=UTC),
        source_id=source_id,
    )


def test_stream_accepts_first_snapshot_and_exposes_state() -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    snapshot = _snapshot()
    stream.accept(snapshot)
    assert stream.latest() == snapshot
    assert stream.state is not None
    assert stream.state.last_observed_at == snapshot.observed_at


def test_stream_accepts_strictly_newer_snapshot() -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    first = _snapshot(minute=0)
    second = _snapshot(minute=1, price="2501")
    stream.accept(first)
    stream.accept(second)
    assert stream.latest() == second


@pytest.mark.parametrize("minute", [1, 0])
def test_stream_rejects_duplicate_or_out_of_order(minute: int) -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    first = _snapshot(minute=1)
    candidate = _snapshot(minute=minute)
    stream.accept(first)
    with pytest.raises(ValueError, match="duplicate or out of order"):
        stream.accept(candidate)
    assert stream.latest() == first


def test_stream_rejects_instrument_mismatch() -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    with pytest.raises(ValueError, match="instrument"):
        stream.accept(_snapshot(instrument_id="NSE:TCS"))


def test_stream_rejects_source_mismatch() -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    with pytest.raises(ValueError, match="source"):
        stream.accept(_snapshot(source_id="paper-feed-2"))


def test_stream_rejects_invalid_snapshot_without_mutating_state() -> None:
    stream = PaperMarketDataStream(instrument_id="NSE:RELIANCE", source_id="paper-feed-1")
    first = _snapshot()
    invalid = _snapshot(minute=1, price="0")
    stream.accept(first)
    with pytest.raises(ValueError, match="greater than zero"):
        stream.accept(invalid)
    assert stream.latest() == first


@pytest.mark.parametrize(\n    ("instrument_id", "source_id"), [("", "paper-feed-1"), ("NSE:RELIANCE", "")]\n)
def test_stream_requires_identity(instrument_id: str, source_id: str) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        PaperMarketDataStream(instrument_id=instrument_id, source_id=source_id)