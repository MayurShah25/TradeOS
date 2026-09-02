"""Deterministic registry for governed paper-trading runs."""

from collections.abc import Iterable

from .run_state import PaperRunStatus, PaperTradingRun


class PaperRunRegistry:
    """In-memory run registry with immutable run snapshots."""

    def __init__(self) -> None:
        self._runs: dict[str, PaperTradingRun] = {}

    def register(self, run: PaperTradingRun) -> None:
        """Register a new run, rejecting duplicate identities."""
        run.validate()
        if run.run_id in self._runs:
            raise ValueError("duplicate run_id")
        self._runs[run.run_id] = run

    def get(self, run_id: str) -> PaperTradingRun | None:
        """Return a run snapshot, or ``None`` when it is unknown."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        return self._runs.get(run_id)

    def require(self, run_id: str) -> PaperTradingRun:
        """Return a known run or raise a deterministic lookup error."""
        run = self.get(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def update(self, run: PaperTradingRun) -> None:
        """Replace an existing run with its validated immutable snapshot."""
        run.validate()
        if run.run_id not in self._runs:
            raise KeyError(run.run_id)
        self._runs[run.run_id] = run

    def complete(self, run_id: str, completed_at) -> PaperTradingRun:
        """Close an open run as completed and return the new snapshot."""
        completed = self.require(run_id).complete(completed_at)
        self.update(completed)
        return completed

    def fail(self, run_id: str, completed_at) -> PaperTradingRun:
        """Close an open run as failed and return the new snapshot."""
        failed = self.require(run_id).fail(completed_at)
        self.update(failed)
        return failed

    def runs(
        self,
        *,
        status: PaperRunStatus | None = None,
        account_id: str | None = None,
        instrument_id: str | None = None,
    ) -> tuple[PaperTradingRun, ...]:
        """Return deterministic run history, optionally filtered by identity."""
        if account_id == "":
            raise ValueError("account_id must not be empty")
        if instrument_id == "":
            raise ValueError("instrument_id must not be empty")
        values: Iterable[PaperTradingRun] = self._runs.values()
        if status is not None:
            values = (run for run in values if run.status is status)
        if account_id is not None:
            values = (run for run in values if run.account_id == account_id)
        if instrument_id is not None:
            values = (run for run in values if run.instrument_id == instrument_id)
        return tuple(values)
