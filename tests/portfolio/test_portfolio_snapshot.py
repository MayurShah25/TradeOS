"""Tests for the integrated portfolio snapshot boundary."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from tradeos.execution import OrderSide
from tradeos.portfolio import AccountStateBuilder, PortfolioStateBuilder, PositionLedger


def test_snapshot_integrates_account_positions_open_orders_and_timestamp() -> None:
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))
    account = AccountStateBuilder.snapshot(
        cash=Decimal(9000),
        buying_power=Decimal(18000),
        equity=Decimal(10000),
    )
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)

    state = PortfolioStateBuilder.snapshot(ledger, account, (), timestamp)

    assert state.account == account
    assert state.position_for("AAPL") is not None
    assert state.open_orders == ()
    assert state.realized_pnl == Decimal(0)
    assert state.timestamp == timestamp


def test_snapshot_rejects_non_utc_timestamp() -> None:
    ledger = PositionLedger()
    account = AccountStateBuilder.snapshot(Decimal(1000), Decimal(1000), Decimal(1000))
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=timezone(timedelta(hours=1)))

    with pytest.raises(ValueError, match="UTC"):
        PortfolioStateBuilder.snapshot(ledger, account, (), timestamp)


def test_snapshot_rejects_naive_timestamp() -> None:
    ledger = PositionLedger()
    with pytest.raises(ValueError, match="timezone-aware"):
        PortfolioStateBuilder.snapshot(
            ledger, timestamp=datetime.fromisoformat("2026-09-02T08:00:00")
        )
