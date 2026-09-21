from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tradeos.infrastructure.sqlite_paper_market_data_repository import (
    SQLitePaperMarketDataRepository,
)
from tradeos.market_data import PaperMarketDataSnapshot
from tradeos.market_data_repository import PaperMarketDataRepository


def _snapshot(
    *,
    instrument_id: str = "NSE:RELIANCE",
    source_id: str = "paper-feed-1",
    minute: int = 0,
    price: str = "2500",
) -> PaperMarketDataSnapshot:
    return PaperMarketDataSnapshot(
        instrument_id=instrument_id,
        source_id=source_id,
        observed_at=datetime(2026, 9, 21, 10, minute, tzinfo=UTC),
        price=Decimal(price),
    )


def test_repository_round_trip(tmp_path) -> None:
    with SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository:
        snapshot = _snapshot()
        repository.save(snapshot)
        assert (
            repository.get(
                instrument_id=snapshot.instrument_id,
                source_id=snapshot.source_id,
                observed_at=snapshot.observed_at,
            )
            == snapshot
        )


def test_repository_is_idempotent_for_exact_resave(tmp_path) -> None:
    with SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository:
        snapshot = _snapshot()
        repository.save(snapshot)
        repository.save(snapshot)
        assert repository.list_for_instrument(
            instrument_id=snapshot.instrument_id,
        ) == (snapshot,)


def test_repository_rejects_mutation(tmp_path) -> None:
    with SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository:
        repository.save(_snapshot(price="2500"))
        with pytest.raises(ValueError, match="immutable"):
            repository.save(_snapshot(price="2501"))


def test_repository_returns_observations_in_order(tmp_path) -> None:
    with SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository:
        later = _snapshot(minute=2)
        earlier = _snapshot(minute=1)
        other_source = _snapshot(minute=1, source_id="paper-feed-2")
        repository.save(later)
        repository.save(other_source)
        repository.save(earlier)
        assert repository.list_for_instrument(
            instrument_id="NSE:RELIANCE",
            source_id="paper-feed-1",
        ) == (earlier, later)
        assert repository.list_for_instrument(
            instrument_id="NSE:RELIANCE",
        ) == (earlier, other_source, later)


def test_repository_rejects_invalid_snapshot(tmp_path) -> None:
    invalid = _snapshot(price="0")
    with (
        SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository,
        pytest.raises(ValueError, match="greater than zero"),
    ):
        repository.save(invalid)


def test_repository_requires_utc_lookup(tmp_path) -> None:
    snapshot = _snapshot()
    with SQLitePaperMarketDataRepository(tmp_path / "market.db") as repository:
        repository.save(snapshot)
        with pytest.raises(ValueError, match="UTC"):
            repository.get(
                instrument_id=snapshot.instrument_id,
                source_id=snapshot.source_id,
                observed_at=snapshot.observed_at.replace(tzinfo=None),
            )


def test_repository_is_a_market_data_port() -> None:
    assert issubclass(SQLitePaperMarketDataRepository, PaperMarketDataRepository)
