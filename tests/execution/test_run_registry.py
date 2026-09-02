import datetime as dt  # noqa: I001

import pytest

from tradeos.execution import PaperRunRegistry, PaperRunStatus, PaperTradingRun


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


def test_register_get_and_require_return_immutable_snapshot() -> None:
    registry = PaperRunRegistry()
    run = make_run()
    registry.register(run)

    assert registry.get(run.run_id) == run
    assert registry.require(run.run_id) == run
    assert registry.runs() == (run,)


def test_duplicate_run_id_is_rejected() -> None:
    registry = PaperRunRegistry()
    registry.register(make_run())

    with pytest.raises(ValueError, match="duplicate run_id"):
        registry.register(make_run())


def test_unknown_run_is_distinguished_from_closed_run() -> None:
    registry = PaperRunRegistry()
    registry.register(make_run())
    completed = registry.complete("run-1", START + dt.timedelta(seconds=1))

    assert completed.status is PaperRunStatus.COMPLETED
    assert registry.get("unknown") is None
    with pytest.raises(KeyError):
        registry.require("unknown")


def test_fail_updates_registry_without_mutating_original() -> None:
    registry = PaperRunRegistry()
    run = make_run()
    registry.register(run)

    failed = registry.fail(run.run_id, START + dt.timedelta(seconds=2))

    assert run.status is PaperRunStatus.OPEN
    assert failed.status is PaperRunStatus.FAILED
    assert registry.require(run.run_id) == failed


def test_closed_run_cannot_be_completed_again() -> None:
    registry = PaperRunRegistry()
    registry.register(make_run())
    registry.complete("run-1", START + dt.timedelta(seconds=1))

    with pytest.raises(ValueError, match="already closed"):
        registry.complete("run-1", START + dt.timedelta(seconds=2))


def test_runs_are_filterable_and_keep_registration_order() -> None:
    registry = PaperRunRegistry()
    first = make_run("run-1", "account-1")
    second = make_run("run-2", "account-2")
    third = make_run("run-3", "account-1")
    registry.register(first)
    registry.register(second)
    registry.register(third)
    completed_third = registry.complete("run-3", START + dt.timedelta(seconds=1))

    assert registry.runs(account_id="account-1") == (first, completed_third)
    assert registry.runs(status=PaperRunStatus.COMPLETED) == (completed_third,)
    assert registry.runs(instrument_id="instrument-1") == (first, second, completed_third)


def test_empty_lookup_and_filters_are_rejected() -> None:
    registry = PaperRunRegistry()

    with pytest.raises(ValueError, match="run_id"):
        registry.get("")
    with pytest.raises(ValueError, match="account_id"):
        registry.runs(account_id="")
    with pytest.raises(ValueError, match="instrument_id"):
        registry.runs(instrument_id="")
