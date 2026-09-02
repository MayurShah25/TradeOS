import datetime as dt
from pathlib import Path

import pytest

from tradeos.execution import AuditEvent, AuditEventType, PaperRunStatus, PaperTradingRun
from tradeos.infrastructure import SQLitePaperTradingRepository

START = dt.datetime(2026, 1, 1, 10, tzinfo=dt.UTC)


def make_run(run_id: str = "run-1") -> PaperTradingRun:
    return PaperTradingRun(
        run_id=run_id,
        proposal_id=f"proposal-{run_id}",
        risk_decision_id=f"risk-{run_id}",
        authorization_id=f"auth-{run_id}",
        account_id="account-1",
        instrument_id="instrument-1",
        configuration_hash="config-1",
        started_at=START,
    )


def make_event(run_id: str, sequence: int, event_type: AuditEventType) -> AuditEvent:
    return AuditEvent(
        event_id=f"{run_id}:{sequence}:{event_type.value}",
        run_id=run_id,
        event_type=event_type,
        occurred_at=START,
        sequence=sequence,
        payload=(("approved", "True"),),
    )


def test_run_survives_repository_reopen(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    run = make_run()
    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(run)
    with SQLitePaperTradingRepository(database) as repository:
        assert repository.require_run(run.run_id) == run
        assert repository.list_runs() == (run,)


def test_run_update_is_persistent_and_filterable(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    run = make_run()
    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(run)
        completed = run.complete(START + dt.timedelta(seconds=5))
        repository.save_run(completed)
    with SQLitePaperTradingRepository(database) as repository:
        assert repository.get_run(run.run_id) == completed
        assert repository.list_runs(status=PaperRunStatus.COMPLETED) == (completed,)


def test_audit_history_is_append_only_and_survives_reopen(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    run = make_run()
    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(run)
        repository.append_audit_event(make_event(run.run_id, 0, AuditEventType.RUN_STARTED))
        repository.append_audit_event(make_event(run.run_id, 1, AuditEventType.RISK_EVALUATED))
    with SQLitePaperTradingRepository(database) as repository:
        events = repository.audit_events(run.run_id)
        assert [event.sequence for event in events] == [0, 1]
        assert events[1].event_type is AuditEventType.RISK_EVALUATED
        assert repository.export_audit_events(run.run_id)[1]["payload"] == {"approved": "True"}


def test_audit_rejects_unknown_run_and_non_contiguous_sequence(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        with pytest.raises(KeyError):
            repository.append_audit_event(make_event("unknown", 0, AuditEventType.RUN_STARTED))
        repository.save_run(make_run())
        with pytest.raises(ValueError, match="contiguous"):
            repository.append_audit_event(make_event("run-1", 1, AuditEventType.RUN_STARTED))


def test_duplicate_audit_event_is_rejected(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    with SQLitePaperTradingRepository(database) as repository:
        repository.save_run(make_run())
        event = make_event("run-1", 0, AuditEventType.RUN_STARTED)
        repository.append_audit_event(event)
        with pytest.raises(ValueError, match="duplicate event_id"):
            repository.append_audit_event(event)
