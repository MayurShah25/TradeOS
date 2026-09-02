from datetime import UTC, datetime, timedelta

import pytest

from tradeos.execution import PaperRunStatus, PaperTradingRun


START = datetime(2026, 1, 1, 10, tzinfo=UTC)


def make_run() -> PaperTradingRun:
    return PaperTradingRun(
        run_id="run-1",
        proposal_id="proposal-1",
        risk_decision_id="risk-1",
        authorization_id="auth-1",
        account_id="account-1",
        instrument_id="instrument-1",
        configuration_hash="config-1",
        started_at=START,
    )


def test_run_validates_and_completes_immutably() -> None:
    run = make_run()
    completed = run.complete(START + timedelta(seconds=1))

    assert run.status is PaperRunStatus.OPEN
    assert completed.status is PaperRunStatus.COMPLETED
    assert completed.completed_at == START + timedelta(seconds=1)


def test_run_can_fail_without_being_treated_as_open() -> None:
    failed = make_run().fail(START + timedelta(seconds=1))

    assert failed.status is PaperRunStatus.FAILED
    assert failed.completed_at is not None


def test_closed_run_cannot_transition_again() -> None:
    completed = make_run().complete(START + timedelta(seconds=1))

    with pytest.raises(ValueError, match="already closed"):
        completed.fail(START + timedelta(seconds=2))


def test_completion_before_start_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot precede"):
        make_run().complete(START - timedelta(seconds=1))


def test_non_utc_timestamps_are_rejected() -> None:
    from datetime import timezone

    timestamp = START.astimezone(timezone(timedelta(hours=1)))
    with pytest.raises(ValueError, match="UTC"):
        make_run().complete(timestamp)
