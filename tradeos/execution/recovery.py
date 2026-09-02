"""Safe inspection of interrupted paper-trading runs."""

from dataclasses import dataclass

from .audit import AuditEvent, AuditEventType
from .ports import PaperTradingPersistencePort
from .run_state import PaperRunStatus, PaperTradingRun


@dataclass(frozen=True, slots=True)
class PaperRunRecoveryAssessment:
    """Immutable assessment of one persisted run that needs recovery review."""

    run: PaperTradingRun
    audit_events: tuple[AuditEvent, ...]
    requires_reconciliation: bool
    reason: str


class PaperTradingRecovery:
    """Inspect interrupted runs without executing, retrying, or changing orders."""

    def __init__(self, persistence: PaperTradingPersistencePort) -> None:
        self._persistence = persistence

    def inspect_open_runs(self) -> tuple[PaperRunRecoveryAssessment, ...]:
        """Return runs that remain open or explicitly require reconciliation."""
        runs = self._persistence.list_runs(status=PaperRunStatus.OPEN)
        pending = self._persistence.list_runs(status=PaperRunStatus.RECONCILIATION_REQUIRED)
        assessments: list[PaperRunRecoveryAssessment] = []
        for run in (*runs, *pending):
            events = self._persistence.audit_events(run.run_id)
            assessments.append(
                PaperRunRecoveryAssessment(
                    run=run,
                    audit_events=events,
                    requires_reconciliation=True,
                    reason=_recovery_reason(run, events),
                )
            )
        return tuple(assessments)


def _recovery_reason(run: PaperTradingRun, events: tuple[AuditEvent, ...]) -> str:
    if not events:
        return "run has no persisted audit history"
    last = events[-1]
    if last.event_type is AuditEventType.RECONCILIATION_REQUIRED:
        return "run has an unknown execution outcome; explicit reconciliation is required"
    if run.status is PaperRunStatus.RECONCILIATION_REQUIRED:
        return "run has an unresolved execution outcome; explicit reconciliation is required"
    return f"run interrupted after {last.event_type.value}; explicit reconciliation is required"
