"""Tests for the paper market-data to execution bridge."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tradeos.execution import (
    AuthorizationLedger,
    AuthorizedExecutionGateway,
    ExecutionAuthorization,
    OperatingMode,
    Order,
    OrderSide,
    PaperBroker,
    PaperTradingSession,
)
from tradeos.infrastructure import InMemoryPaperMarketDataRepository
from tradeos.market_data import PaperMarketDataSnapshot
from tradeos.market_data_execution_bridge import PaperMarketDataExecutionBridge
from tradeos.market_data_stream import PaperMarketDataStream
from tradeos.portfolio import (
    AccountStateBuilder,
    PortfolioRiskLimits,
    PortfolioStateBuilder,
    PositionLedger,
)

NOW = datetime(2026, 9, 21, 10, 0, tzinfo=UTC)


def _order() -> Order:
    return Order("order-1", "AAPL", OrderSide.BUY, Decimal(2))


def _portfolio():
    account = AccountStateBuilder.snapshot(
        cash=Decimal(100000),
        buying_power=Decimal(100000),
        equity=Decimal(100000),
        available_margin=Decimal(100000),
    )
    return PortfolioStateBuilder.snapshot(
        PositionLedger(),
        account=account,
        timestamp=NOW,
    )


def _limits() -> PortfolioRiskLimits:
    return PortfolioRiskLimits(
        max_gross_exposure=Decimal(1000),
        max_portfolio_heat=Decimal("0.1"),
        max_leverage=Decimal(2),
        min_available_margin=Decimal(0),
    )


def _snapshot(price: str = "125") -> PaperMarketDataSnapshot:
    return PaperMarketDataSnapshot(
        instrument_id="AAPL",
        price=Decimal(price),
        observed_at=NOW - timedelta(seconds=10),
        source_id="paper-source",
    )


def _bridge(
    repository: InMemoryPaperMarketDataRepository,
    stream: PaperMarketDataStream,
) -> tuple[PaperMarketDataExecutionBridge, AuthorizationLedger]:
    ledger = AuthorizationLedger()
    ledger.issue(
        ExecutionAuthorization(
            authorization_id="auth-1",
            proposal_id="proposal-1",
            risk_decision_id="risk-1",
            account_id="account-1",
            instrument_id="AAPL",
            approved_quantity=Decimal(2),
            min_price=None,
            max_price=None,
            approved_stop_price=None,
            operating_mode=OperatingMode.PAPER,
            configuration_hash="config-hash",
            issued_at=NOW - timedelta(minutes=1),
            expires_at=NOW + timedelta(minutes=5),
        )
    )
    session = PaperTradingSession(AuthorizedExecutionGateway(PaperBroker(), ledger), ledger)
    return (
        PaperMarketDataExecutionBridge(
            repository=repository,
            stream=stream,
            session=session,
        ),
        ledger,
    )


def test_bridge_executes_from_latest_ordered_and_persisted_snapshot() -> None:
    repository = InMemoryPaperMarketDataRepository()
    stream = PaperMarketDataStream(instrument_id="AAPL", source_id="paper-source")
    snapshot = _snapshot()
    stream.accept(snapshot)
    repository.save(snapshot)
    bridge, ledger = _bridge(repository, stream)

    result = bridge.execute_latest(
        authorization_id="auth-1",
        risk_decision_id="risk-1",
        order=_order(),
        portfolio=_portfolio(),
        limits=_limits(),
        now=NOW,
        max_market_data_age=timedelta(minutes=1),
    )

    assert result.risk.approved is True
    assert result.execution.status.value == "FILLED"
    assert result.processing is not None
    assert result.processing.portfolio.position_for("AAPL").quantity == Decimal(2)
    assert ledger.status("auth-1").value == "CONSUMED"


def test_bridge_rejects_when_latest_snapshot_is_not_persisted() -> None:
    repository = InMemoryPaperMarketDataRepository()
    stream = PaperMarketDataStream(instrument_id="AAPL", source_id="paper-source")
    stream.accept(_snapshot())
    bridge, ledger = _bridge(repository, stream)

    with pytest.raises(ValueError, match="not persisted"):
        bridge.execute_latest(
            authorization_id="auth-1",
            risk_decision_id="risk-1",
            order=_order(),
            portfolio=_portfolio(),
            limits=_limits(),
            now=NOW,
            max_market_data_age=timedelta(minutes=1),
        )

    assert ledger.status("auth-1").value == "ACTIVE"


def test_bridge_rejects_stale_snapshot_before_execution_authorization_is_consumed() -> None:
    repository = InMemoryPaperMarketDataRepository()
    stream = PaperMarketDataStream(instrument_id="AAPL", source_id="paper-source")
    stale = PaperMarketDataSnapshot(
        instrument_id="AAPL",
        price=Decimal(125),
        observed_at=NOW - timedelta(minutes=10),
        source_id="paper-source",
    )
    stream.accept(stale)
    repository.save(stale)
    bridge, ledger = _bridge(repository, stream)

    with pytest.raises(ValueError, match="stale"):
        bridge.execute_latest(
            authorization_id="auth-1",
            risk_decision_id="risk-1",
            order=_order(),
            portfolio=_portfolio(),
            limits=_limits(),
            now=NOW,
            max_market_data_age=timedelta(minutes=1),
        )

    assert ledger.status("auth-1").value == "ACTIVE"


def test_bridge_rejects_instrument_mismatch_before_execution() -> None:
    repository = InMemoryPaperMarketDataRepository()
    stream = PaperMarketDataStream(instrument_id="MSFT", source_id="paper-source")
    snapshot = PaperMarketDataSnapshot(
        instrument_id="MSFT",
        price=Decimal(125),
        observed_at=NOW - timedelta(seconds=10),
        source_id="paper-source",
    )
    stream.accept(snapshot)
    repository.save(snapshot)
    bridge, ledger = _bridge(repository, stream)

    with pytest.raises(ValueError, match="instrument"):
        bridge.execute_latest(
            authorization_id="auth-1",
            risk_decision_id="risk-1",
            order=_order(),
            portfolio=_portfolio(),
            limits=_limits(),
            now=NOW,
            max_market_data_age=timedelta(minutes=1),
        )

    assert ledger.status("auth-1").value == "ACTIVE"


def test_bridge_rejects_negative_freshness_window() -> None:
    repository = InMemoryPaperMarketDataRepository()
    stream = PaperMarketDataStream(instrument_id="AAPL", source_id="paper-source")
    snapshot = _snapshot()
    stream.accept(snapshot)
    repository.save(snapshot)
    bridge, ledger = _bridge(repository, stream)

    with pytest.raises(ValueError, match="cannot be negative"):
        bridge.execute_latest(
            authorization_id="auth-1",
            risk_decision_id="risk-1",
            order=_order(),
            portfolio=_portfolio(),
            limits=_limits(),
            now=NOW,
            max_market_data_age=timedelta(seconds=-1),
        )

    assert ledger.status("auth-1").value == "ACTIVE"
