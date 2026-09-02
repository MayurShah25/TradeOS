"""Integration tests for durable paper-trading session persistence."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from tradeos.execution import (
    AuditEventType,
    AuthorizationLedger,
    AuthorizedExecutionGateway,
    ExecutionAuthorization,
    OperatingMode,
    Order,
    OrderSide,
    PaperBroker,
    PaperRunStatus,
    PaperTradingRun,
    PaperTradingSession,
)
from tradeos.infrastructure import SQLitePaperTradingRepository
from tradeos.portfolio import (
    AccountStateBuilder,
    PortfolioRiskLimits,
    PortfolioStateBuilder,
    PositionLedger,
    RiskContextBuilder,
)

NOW = datetime(2026, 9, 2, 10, 0, tzinfo=UTC)


def _order() -> Order:
    return Order("order-1", "AAPL", OrderSide.BUY, Decimal(2))


def _authorization() -> ExecutionAuthorization:
    return ExecutionAuthorization(
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


def _context():
    account = AccountStateBuilder.snapshot(
        cash=Decimal(100000),
        buying_power=Decimal(100000),
        equity=Decimal(100000),
        available_margin=Decimal(100000),
    )
    portfolio = PortfolioStateBuilder.snapshot(
        PositionLedger(),
        account=account,
        timestamp=NOW,
    )
    return RiskContextBuilder.build(
        portfolio,
        {"AAPL": Decimal(100)},
        NOW,
        timedelta(minutes=5),
    )


def _limits(max_gross_exposure: Decimal = Decimal(1000)) -> PortfolioRiskLimits:
    return PortfolioRiskLimits(
        max_gross_exposure=max_gross_exposure,
        max_portfolio_heat=Decimal("0.1"),
        max_leverage=Decimal(2),
        min_available_margin=Decimal(0),
    )


def _run() -> PaperTradingRun:
    return PaperTradingRun(
        run_id="run-1",
        proposal_id="proposal-1",
        risk_decision_id="risk-1",
        authorization_id="auth-1",
        account_id="account-1",
        instrument_id="AAPL",
        configuration_hash="config-hash",
        started_at=NOW,
    )


def _session(
    persistence: SQLitePaperTradingRepository,
) -> tuple[PaperTradingSession, AuthorizationLedger]:
    ledger = AuthorizationLedger()
    ledger.issue(_authorization())
    gateway = AuthorizedExecutionGateway(PaperBroker(), ledger)
    return PaperTradingSession(gateway, ledger, persistence=persistence), ledger


def test_session_persists_completed_run_and_audit_across_restart(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        session, ledger = _session(repository)
        result = session.execute(
            "auth-1",
            "risk-1",
            _order(),
            _context(),
            _limits(),
            {"AAPL": Decimal(100)},
            NOW,
            run=_run(),
        )

        assert result.run is not None
        assert result.run.status is PaperRunStatus.COMPLETED
        assert ledger.status("auth-1") is not None

    with SQLitePaperTradingRepository(database) as repository:
        persisted = repository.require_run("run-1")
        events = repository.audit_events("run-1")

    assert persisted.status is PaperRunStatus.COMPLETED
    assert tuple(event.event_type for event in events) == (
        AuditEventType.RUN_STARTED,
        AuditEventType.RISK_EVALUATED,
        AuditEventType.AUTHORIZATION_VERIFIED,
        AuditEventType.EXECUTION_SUBMITTED,
        AuditEventType.EXECUTION_RECONCILED,
        AuditEventType.PORTFOLIO_UPDATED,
        AuditEventType.RUN_COMPLETED,
    )
    assert tuple(event.sequence for event in events) == tuple(range(7))


def test_session_persists_failed_run_and_failure_audit(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        session, ledger = _session(repository)

        with pytest.raises(PermissionError, match="risk controls rejected"):
            session.execute(
                "auth-1",
                "risk-1",
                _order(),
                _context(),
                _limits(max_gross_exposure=Decimal(1)),
                {"AAPL": Decimal(100)},
                NOW,
                run=_run(),
            )

        assert ledger.status("auth-1").value == "ACTIVE"

    with SQLitePaperTradingRepository(database) as repository:
        persisted = repository.require_run("run-1")
        events = repository.audit_events("run-1")

    assert persisted.status is PaperRunStatus.FAILED
    assert persisted.completed_at == NOW
    assert tuple(event.event_type for event in events) == (
        AuditEventType.RUN_STARTED,
        AuditEventType.RISK_EVALUATED,
        AuditEventType.RUN_FAILED,
    )
    assert tuple(event.sequence for event in events) == (0, 1, 2)
