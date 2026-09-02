"""Tests for safe inspection of interrupted paper-trading runs."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from tradeos.execution import (
    AuditEvent,
    AuditEventType,
    PaperTradingRecovery,
    PaperTradingRun,
)
from tradeos.infrastructure import SQLitePaperTradingRepository

START = datetime(2026, 9, 2, 10, tzinfo=UTC)


def _run(run_id: str) -> PaperTradingRun:
    return PaperTradingRun(
        run_id=run_id,
        proposal_id=f"proposal-{run_id}",
        risk_decision_id=f"risk-{run_id}",
        authorization_id=f"auth-{run_id}",
        account_id="account-1",
        instrument_id="AAPL",
        configuration_hash="config-1",
        started_at=START,
    )


def _event(run_id: str, sequence: int) -> AuditEvent:
    return AuditEvent(
        event_id=f"{run_id}:{sequence}:RUN_STARTED",
        run_id=run_id,
        event_type=AuditEventType.RUN_STARTED,
        occurred_at=START,
        sequence=sequence,
    )


def test_recovery_inspects_only_open_runs(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    open_run = _run("open-run")
    completed = _run("completed-run").complete(START + timedelta(seconds=5))

    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(open_run)
        repository.append_audit_event(_event(open_run.run_id, 0))
        repository.save_run(completed)

        assessments = PaperTradingRecovery(repository).inspect_open_runs()

    assert len(assessments) == 1
    assessment = assessments[0]
    assert assessment.run == open_run
    assert assessment.audit_events == (_event(open_run.run_id, 0),)
    assert assessment.requires_reconciliation is True
    assert "RUN_STARTED" in assessment.reason


def test_recovery_identifies_open_run_without_audit_history(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    run = _run("open-run")

    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(run)
        assessment = PaperTradingRecovery(repository).inspect_open_runs()[0]

    assert assessment.audit_events == ()
    assert assessment.requires_reconciliation is True
    assert assessment.reason == "run has no persisted audit history"
