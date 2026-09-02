"""Tests for the governed paper-trading session."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tradeos.execution import (
    AuditEventType,
    AuditTrail,
    AuthorizationLedger,
    AuthorizedExecutionGateway,
    ExecutionAuthorization,
    OperatingMode,
    Order,
    OrderSide,
    PaperBroker,
    PaperTradingRun,
    PaperTradingSession,
)
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


def _authorization(risk_decision_id: str = "risk-1") -> ExecutionAuthorization:
    return ExecutionAuthorization(
        authorization_id="auth-1",
        proposal_id="proposal-1",
        risk_decision_id=risk_decision_id,
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


def _session(audit_trail: AuditTrail | None = None) -> tuple[PaperTradingSession, AuthorizationLedger]:
    ledger = AuthorizationLedger()
    ledger.issue(_authorization())
    gateway = AuthorizedExecutionGateway(PaperBroker(), ledger)
    return PaperTradingSession(gateway, ledger, audit_trail=audit_trail), ledger


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


def _limits() -> PortfolioRiskLimits:
    return PortfolioRiskLimits(
        max_gross_exposure=Decimal(1000),
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


def test_session_sequences_risk_authorization_execution_and_reconciliation() -> None:
    session, ledger = _session()

    result = session.execute(
        "auth-1",
        "risk-1",
        _order(),
        _context(),
        _limits(),
        {"AAPL": Decimal(100)},
        NOW,
    )

    assert result.risk.approved is True
    assert result.execution.status.value == "FILLED"
    assert result.processing.reconciled is True
    assert result.processing.portfolio.position_for("AAPL").quantity == Decimal(2)
    assert ledger.status("auth-1").value == "CONSUMED"


def test_session_records_complete_governed_run_audit() -> None:
    audit = AuditTrail()
    session, ledger = _session(audit)

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
    assert result.run.status.value == "COMPLETED"
    assert tuple(event.event_type for event in result.audit_events) == (
        AuditEventType.RUN_STARTED,
        AuditEventType.RISK_EVALUATED,
        AuditEventType.AUTHORIZATION_VERIFIED,
        AuditEventType.EXECUTION_SUBMITTED,
        AuditEventType.EXECUTION_RECONCILED,
        AuditEventType.PORTFOLIO_UPDATED,
        AuditEventType.RUN_COMPLETED,
    )
    assert tuple(event.sequence for event in result.audit_events) == tuple(range(7))
    assert audit.events("run-1") == result.audit_events
    assert ledger.status("auth-1").value == "CONSUMED"


def test_session_rejects_risk_failure_before_consuming_authorization() -> None:
    session, ledger = _session()
    limits = PortfolioRiskLimits(
        max_gross_exposure=Decimal(1),
        max_portfolio_heat=Decimal("0.1"),
        max_leverage=Decimal(2),
        min_available_margin=Decimal(0),
    )

    with pytest.raises(PermissionError, match="risk controls rejected"):
        session.execute(
            "auth-1",
            "risk-1",
            _order(),
            _context(),
            limits,
            {"AAPL": Decimal(100)},
            NOW,
        )

    assert ledger.status("auth-1").value == "ACTIVE"


def test_session_rejects_authorization_bound_to_different_risk_decision() -> None:
    session, ledger = _session()

    with pytest.raises(PermissionError, match="does not match the risk decision"):
        session.execute(
            "auth-1",
            "risk-2",
            _order(),
            _context(),
            _limits(),
            {"AAPL": Decimal(100)},
            NOW,
        )

    assert ledger.status("auth-1").value == "ACTIVE"


def test_session_rejects_missing_price_before_execution() -> None:
    session, ledger = _session()

    with pytest.raises(ValueError, match="missing price"):
        session.execute(
            "auth-1",
            "risk-1",
            _order(),
            _context(),
            _limits(),
            {},
            NOW,
        )

    assert ledger.status("auth-1").value == "ACTIVE"
