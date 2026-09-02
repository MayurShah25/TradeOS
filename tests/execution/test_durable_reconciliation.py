"""Tests for explicit durable reconciliation of unresolved paper runs."""

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from tradeos.execution import (
    AuditEventType,
    ExecutionEvent,
    ExecutionEventType,
    Order,
    OrderSide,
    OrderStatus,
    PaperRunStatus,
    PaperTradingReconciliation,
    PaperTradingRun,
    ReconciliationStatus,
)
from tradeos.infrastructure import SQLitePaperTradingRepository

NOW = datetime(2026, 9, 2, 10, 0, tzinfo=UTC)


def _order() -> Order:
    return Order("order-reconcile", "AAPL", OrderSide.BUY, Decimal(2))


def _run() -> PaperTradingRun:
    return PaperTradingRun(
        run_id="run-reconcile",
        proposal_id="proposal-reconcile",
        risk_decision_id="risk-reconcile",
        authorization_id="auth-reconcile",
        account_id="account-reconcile",
        instrument_id="AAPL",
        configuration_hash="config-hash",
        started_at=NOW,
        status=PaperRunStatus.RECONCILIATION_REQUIRED,
    )


def _unknown_event() -> ExecutionEvent:
    return ExecutionEvent(
        order_id="order-reconcile",
        status=OrderStatus.UNKNOWN,
        event_type=ExecutionEventType.UNKNOWN,
        timestamp=NOW,
    )


def _accepted_event() -> ExecutionEvent:
    return ExecutionEvent(
        order_id="order-reconcile",
        status=OrderStatus.ACCEPTED,
        event_type=ExecutionEventType.ACCEPTED,
        timestamp=NOW,
    )


def _filled_event() -> ExecutionEvent:
    return ExecutionEvent(
        order_id="order-reconcile",
        status=OrderStatus.FILLED,
        event_type=ExecutionEventType.FILLED,
        timestamp=NOW,
        filled_quantity=Decimal(2),
    )


def _seed(repository: SQLitePaperTradingRepository) -> None:
    repository.save_run(_run())
    repository.append_audit_event(
        __import__("tradeos.execution", fromlist=["AuditEvent"]).AuditEvent(
            event_id="run-reconcile:started",
            run_id="run-reconcile",
            event_type=AuditEventType.RECONCILIATION_REQUIRED,
            occurred_at=NOW,
            sequence=0,
            payload=(("order_id", "order-reconcile"), ("status", "UNKNOWN")),
        )
    )


def test_unknown_observation_remains_reconciliation_required(tmp_path: Path) -> None:
    with SQLitePaperTradingRepository(tmp_path / "tradeos.sqlite3") as repository:
        _seed(repository)
        result = PaperTradingReconciliation(repository).reconcile(
            "run-reconcile", _order(), _unknown_event(), NOW
        )

        assert result.status is ReconciliationStatus.UNKNOWN
        assert result.run.status is PaperRunStatus.RECONCILIATION_REQUIRED
        assert result.portfolio_updated is False
        assert repository.require_run("run-reconcile").status is PaperRunStatus.RECONCILIATION_REQUIRED


def test_accepted_observation_durably_completes_run(tmp_path: Path) -> None:
    with SQLitePaperTradingRepository(tmp_path / "tradeos.sqlite3") as repository:
        _seed(repository)
        result = PaperTradingReconciliation(repository).reconcile(
            "run-reconcile", _order(), _accepted_event(), NOW
        )

        assert result.status is ReconciliationStatus.MATCHED
        assert result.run.status is PaperRunStatus.COMPLETED
        assert result.portfolio_updated is True
        assert repository.require_run("run-reconcile").status is PaperRunStatus.COMPLETED
        assert tuple(event.event_type for event in repository.audit_events("run-reconcile")) == (
            AuditEventType.RECONCILIATION_REQUIRED,
            AuditEventType.EXECUTION_RECONCILED,
            AuditEventType.PORTFOLIO_UPDATED,
            AuditEventType.RUN_COMPLETED,
        )


def test_filled_observation_updates_position_and_completes_run(tmp_path: Path) -> None:
    with SQLitePaperTradingRepository(tmp_path / "tradeos.sqlite3") as repository:
        _seed(repository)
        pipeline = __import__(
            "tradeos.portfolio.execution_pipeline",
            fromlist=["ExecutionPortfolioPipeline"],
        ).ExecutionPortfolioPipeline()
        result = PaperTradingReconciliation(repository, pipeline).reconcile(
            "run-reconcile",
            _order(),
            _filled_event(),
            NOW,
            {"AAPL": Decimal(100)},
        )

        assert result.run.status is PaperRunStatus.COMPLETED
        assert result.portfolio_updated is True
        assert pipeline.ledger.positions()["AAPL"].quantity == Decimal(2)


def test_reconciliation_requires_pending_run(tmp_path: Path) -> None:
    with SQLitePaperTradingRepository(tmp_path / "tradeos.sqlite3") as repository:
        repository.save_run(
            PaperTradingRun(
                run_id="closed",
                proposal_id="proposal",
                risk_decision_id="risk",
                authorization_id="auth",
                account_id="account",
                instrument_id="AAPL",
                configuration_hash="config",
                started_at=NOW,
                status=PaperRunStatus.COMPLETED,
                completed_at=NOW,
            )
        )
        with pytest.raises(ValueError, match="does not require reconciliation"):
            PaperTradingReconciliation(repository).reconcile(
                "closed", _order(), _accepted_event(), NOW
            )
