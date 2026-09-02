"""Tests for Phase 3 execution ambiguity and reconciliation-required state."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from tradeos.execution import (
    AuditEventType,
    AuthorizationLedger,
    AuthorizedExecutionGateway,
    ExecutionAuthorization,
    ExecutionOutcomeUnknownError,
    OperatingMode,
    Order,
    OrderSide,
    OrderStatus,
    PaperBroker,
    PaperRunStatus,
    PaperTradingRecovery,
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
    return Order("order-unknown", "AAPL", OrderSide.BUY, Decimal(2))


def _authorization() -> ExecutionAuthorization:
    return ExecutionAuthorization(
        authorization_id="auth-unknown",
        proposal_id="proposal-unknown",
        risk_decision_id="risk-unknown",
        account_id="account-unknown",
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


def _limits() -> PortfolioRiskLimits:
    return PortfolioRiskLimits(
        max_gross_exposure=Decimal(1000),
        max_portfolio_heat=Decimal("0.1"),
        max_leverage=Decimal(2),
        min_available_margin=Decimal(0),
    )


def _run() -> PaperTradingRun:
    return PaperTradingRun(
        run_id="run-unknown",
        proposal_id="proposal-unknown",
        risk_decision_id="risk-unknown",
        authorization_id="auth-unknown",
        account_id="account-unknown",
        instrument_id="AAPL",
        configuration_hash="config-hash",
        started_at=NOW,
    )


class AmbiguousPaperBroker(PaperBroker):
    """Simulate a submission where broker-side acceptance cannot be determined."""

    def submit(self, order: Order) -> OrderStatus:
        raise ExecutionOutcomeUnknownError("broker response was lost during submission")


def _session(
    persistence: SQLitePaperTradingRepository,
) -> tuple[PaperTradingSession, AuthorizationLedger]:
    ledger = AuthorizationLedger()
    ledger.issue(_authorization())
    gateway = AuthorizedExecutionGateway(AmbiguousPaperBroker(), ledger)
    return PaperTradingSession(gateway, ledger, persistence=persistence), ledger


def test_gateway_maps_ambiguous_submission_to_unknown_without_releasing_authorization() -> None:
    ledger = AuthorizationLedger()
    ledger.issue(_authorization())
    gateway = AuthorizedExecutionGateway(AmbiguousPaperBroker(), ledger)

    result = gateway.execute("auth-unknown", _order(), NOW)

    assert result.status is OrderStatus.UNKNOWN
    assert ledger.status("auth-unknown").value == "CONSUMED"


def test_run_can_require_reconciliation_without_becoming_terminal() -> None:
    pending = _run().require_reconciliation()

    assert pending.status is PaperRunStatus.RECONCILIATION_REQUIRED
    assert pending.completed_at is None
    assert pending.complete(NOW).status is PaperRunStatus.COMPLETED


def test_unknown_execution_persists_reconciliation_required_run(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        session, ledger = _session(repository)
        result = session.execute(
            "auth-unknown",
            "risk-unknown",
            _order(),
            _context(),
            _limits(),
            {"AAPL": Decimal(100)},
            NOW,
            run=_run(),
        )

        assert result.execution.status is OrderStatus.UNKNOWN
        assert result.processing is None
        assert result.run is not None
        assert result.run.status is PaperRunStatus.RECONCILIATION_REQUIRED
        assert ledger.status("auth-unknown").value == "CONSUMED"

        persisted = repository.require_run("run-unknown")
        events = repository.audit_events("run-unknown")

    assert persisted.status is PaperRunStatus.RECONCILIATION_REQUIRED
    assert tuple(event.event_type for event in events) == (
        AuditEventType.RUN_STARTED,
        AuditEventType.RISK_EVALUATED,
        AuditEventType.AUTHORIZATION_VERIFIED,
        AuditEventType.EXECUTION_SUBMITTED,
        AuditEventType.RECONCILIATION_REQUIRED,
    )
    assert events[-1].payload == (("order_id", "order-unknown"), ("status", "UNKNOWN"))


def test_recovery_surfaces_reconciliation_required_run_after_restart(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        session, _ledger = _session(repository)
        session.execute(
            "auth-unknown",
            "risk-unknown",
            _order(),
            _context(),
            _limits(),
            {"AAPL": Decimal(100)},
            NOW,
            run=_run(),
        )

    with SQLitePaperTradingRepository(database) as repository:
        assessments = PaperTradingRecovery(repository).inspect_open_runs()

    assert len(assessments) == 1
    assessment = assessments[0]
    assert assessment.run.status is PaperRunStatus.RECONCILIATION_REQUIRED
    assert assessment.requires_reconciliation is True
    assert "unknown execution outcome" in assessment.reason
