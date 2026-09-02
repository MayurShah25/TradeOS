"""Tests for the deterministic portfolio risk context."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tradeos.execution import OrderSide
from tradeos.portfolio import (
    AccountStateBuilder,
    PortfolioStateBuilder,
    PositionLedger,
    RiskContextBuilder,
)


def _portfolio(timestamp: datetime):
    ledger = PositionLedger()
    ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))
    account = AccountStateBuilder.snapshot(
        Decimal(9000), Decimal(18000), Decimal(10000)
    )
    return PortfolioStateBuilder.snapshot(ledger, account, (), timestamp)


def test_risk_context_calculates_exposure_and_heat_from_snapshot() -> None:
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)
    context = RiskContextBuilder.build(
        _portfolio(timestamp),
        {"AAPL": Decimal(120)},
        timestamp,
        timedelta(minutes=5),
    )

    assert context.exposure.gross == Decimal(1200)
    assert context.exposure.net == Decimal(1200)
    assert context.heat.gross_exposure == Decimal(1200)
    assert context.heat.ratio == Decimal("0.12")
    assert context.stale is False


def test_risk_context_marks_snapshot_stale() -> None:
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)
    context = RiskContextBuilder.build(
        _portfolio(timestamp),
        {"AAPL": Decimal(120)},
        timestamp + timedelta(minutes=6),
        timedelta(minutes=5),
    )

    assert context.stale is True


def test_risk_context_requires_account() -> None:
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)
    ledger = PositionLedger()
    portfolio = PortfolioStateBuilder.snapshot(ledger, timestamp=timestamp)

    with pytest.raises(ValueError, match="account state is required"):
        RiskContextBuilder.build(
            portfolio, {}, timestamp, timedelta(minutes=5)
        )


def test_risk_context_rejects_invalid_time_window() -> None:
    timestamp = datetime(2026, 9, 2, 8, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="max_age"):
        RiskContextBuilder.build(
            _portfolio(timestamp), {"AAPL": Decimal(100)}, timestamp, timedelta(days=-1)
        )


def test_position_ledger_can_restore_snapshot() -> None:
    ledger = PositionLedger()
    position = ledger.apply_fill("AAPL", OrderSide.BUY, Decimal(10), Decimal(100))

    restored = PositionLedger.from_positions((position,))

    assert restored.get("AAPL") == position
