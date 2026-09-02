import datetime as dt

import pytest

from tradeos.execution import (
    AuditEvent,
    AuditEventType,
    PaperRunRegistry,
    PaperRunStatus,
    PaperTradingRun,
    SqlitePaperRunAuditRepository,
)

START = dt.datetime(2026, 1, 1, 10, tzinfo=dt.UTC)


def make_run(run_id: str = "run-1", account_id: str = "account-1") -> PaperTradingRun:
    return PaperTradingRun(
        run_id=run_id,
        proposal_id=f"proposal-{run_id}",
        risk_decision_id=f"risk-{run_id}",
        authorization_id=f"auth-{run_id}",
        account_id=account_id,
        instrument_id="instrument-1",
        configuration_hash="config-1",
        started_at=START,
    )


def make_event(
    run_id: str, sequence: int, event_type: AuditEventType = AuditEventType.RUN_STARTED
) -> AuditEvent:
    return AuditEvent(
        event_id=f"{run_id}:{sequence}:{event_type.value}",
        run_id=run_id,
        event_type=event_type,
        occurred_at=START + dt.timedelta(seconds=sequence),
        sequence=sequence,
        payload=(("status", "OPEN"),),
    )


def test_runs_and_audit_survive_repository_reopen(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    run = make_run()
    completed = run.complete(START + dt.timedelta(seconds=10))
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.save_run(run)
        repository.save_run(completed)
        repository.append_audit_event(make_event(run.run_id, 0))
        repository.append_audit_event(make_event(run.run_id, 1, AuditEventType.RUN_COMPLETED))
    with SqlitePaperRunAuditRepository(database) as repository:
        assert repository.get_run(run.run_id) == completed
        assert repository.audit_events(run.run_id)[1].event_type is AuditEventType.RUN_COMPLETED


def test_runs_are_filterable_and_registration_order_is_durable(
    tmp_path: pytest.TempPathFactory,
) -> None:
    database = tmp_path / "tradeos.db"
    first = make_run("run-1", "account-1")
    second = make_run("run-2", "account-2")
    third = make_run("run-3", "account-1")
    completed = third.complete(START + dt.timedelta(seconds=1))
    with SqlitePaperRunAuditRepository(database) as repository:
        for run in (first, second, third):
            repository.save_run(run)
        repository.save_run(completed)
    with SqlitePaperRunAuditRepository(database) as repository:
        assert repository.runs(account_id="account-1") == (first, completed)
        assert repository.runs(status=PaperRunStatus.COMPLETED) == (completed,)


def test_run_identity_cannot_change(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    run = make_run()
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.save_run(run)
        with pytest.raises(ValueError, match="run identity cannot change"):
            repository.save_run(make_run(account_id="different"))


def test_closed_run_cannot_reopen(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    run = make_run()
    completed = run.complete(START + dt.timedelta(seconds=1))
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.save_run(completed)
        with pytest.raises(ValueError, match="closed run status cannot change"):
            repository.save_run(run)


def test_audit_requires_known_run_and_contiguous_sequence(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    with SqlitePaperRunAuditRepository(database) as repository:
        with pytest.raises(KeyError, match="missing"):
            repository.append_audit_event(make_event("missing", 0))
        repository.save_run(make_run())
        with pytest.raises(ValueError, match="contiguous"):
            repository.append_audit_event(make_event("run-1", 1))


def test_duplicate_audit_event_is_rejected(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.save_run(make_run())
        event = make_event("run-1", 0)
        repository.append_audit_event(event)
        with pytest.raises(ValueError, match="duplicate event_id"):
            repository.append_audit_event(event)


def test_hydrate_registry_restores_persisted_runs(tmp_path: pytest.TempPathFactory) -> None:
    database = tmp_path / "tradeos.db"
    run = make_run()
    completed = run.complete(START + dt.timedelta(seconds=1))
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.save_run(completed)
    registry = PaperRunRegistry()
    with SqlitePaperRunAuditRepository(database) as repository:
        repository.hydrate_registry(registry)
    assert registry.require(run.run_id) == completed
