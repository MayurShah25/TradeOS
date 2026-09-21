from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from tradeos.market_data import (
    PaperMarketDataFreshnessPolicy,
    PaperMarketDataSnapshot,
    validate_paper_market_data,
)


def _snapshot(**overrides: object) -> PaperMarketDataSnapshot:
    values: dict[str, object] = {
        "instrument_id": "NSE:RELIANCE",
        "price": Decimal(2500),
        "observed_at": datetime(2026, 9, 21, 10, 0, tzinfo=UTC),
        "source_id": "paper-feed-1",
    }
    values.update(overrides)
    return PaperMarketDataSnapshot(**values)


def _policy() -> PaperMarketDataFreshnessPolicy:
    return PaperMarketDataFreshnessPolicy(max_age_seconds=60)


def test_valid_snapshot_is_accepted() -> None:
    validate_paper_market_data(
        _snapshot(),
        instrument_id="NSE:RELIANCE",
        observed_at=datetime(2026, 9, 21, 10, 0, 30, tzinfo=UTC),
        policy=_policy(),
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("instrument_id", "", "instrument_id must not be blank"),
        ("source_id", "", "source_id must not be blank"),
        ("price", Decimal(0), "price must be greater than zero"),
        ("price", Decimal(-1), "price must be greater than zero"),
    ],
)
def test_snapshot_invariants_fail_closed(field: str, value: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _snapshot(**{field: value}).validate()


def test_instrument_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="instrument"):
        validate_paper_market_data(
            _snapshot(),
            instrument_id="NSE:TCS",
            observed_at=datetime(2026, 9, 21, 10, 0, tzinfo=UTC),
            policy=_policy(),
        )


def test_future_observation_is_rejected() -> None:
    with pytest.raises(ValueError, match="future"):
        validate_paper_market_data(
            _snapshot(observed_at=datetime(2026, 9, 21, 10, 1, tzinfo=UTC)),
            instrument_id="NSE:RELIANCE",
            observed_at=datetime(2026, 9, 21, 10, 0, tzinfo=UTC),
            policy=_policy(),
        )


def test_stale_snapshot_is_rejected() -> None:
    with pytest.raises(ValueError, match="stale"):
        validate_paper_market_data(
            _snapshot(),
            instrument_id="NSE:RELIANCE",
            observed_at=datetime(2026, 9, 21, 10, 2, 1, tzinfo=UTC),
            policy=_policy(),
        )


def test_non_utc_snapshot_is_rejected() -> None:
    with pytest.raises(ValueError, match="UTC"):
        _snapshot(
            observed_at=datetime(2026, 9, 21, 10, 0, tzinfo=timezone(timedelta(hours=1)))
        ).validate()


def test_negative_freshness_policy_is_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        PaperMarketDataFreshnessPolicy(max_age_seconds=-1).validate()


def test_snapshot_is_immutable() -> None:
    snapshot = _snapshot()
    with pytest.raises(AttributeError):
        snapshot.price = Decimal(2501)
