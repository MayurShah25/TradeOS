"""Explicit durable reconciliation for unresolved paper executions."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from .audit import AuditEvent, AuditEventType
from .lifecycle import ExecutionEvent, ExecutionEventType, ReconciliationStatus
from .models import Order, OrderStatus
from .ports import PaperTradingPersistencePort
from .run_state import PaperRunStatus, PaperTradingRun


@dataclass(frozen=True, slots=True)
class PaperReconciliationResult:
    """Immutable result of one explicit reconciliation decision."""

    run: PaperTradingRun
    status: ReconciliationStatus
    observed: ExecutionEvent
    portfolio_updated: bool
    audit_events: tuple[AuditEvent, ...]


class PaperTradingReconciliation:
    """Resolve persisted reconciliation-required runs from explicit observations."""

    def __init__(self, persistence: PaperTradingPersistencePort) -> None:
        self._persistence = persistence

    def reconcile(
        self,
        run_id: str,
        order: Order,
        observed: ExecutionEvent,
        now: datetime,
        prices: dict[str, Decimal] | None = None,
    ) -> PaperReconciliationResult:
        """Apply one verified broker observation without retrying or resubmitting."""
        order.validate()
        observed.validate()
        if observed.order_id != order.order_id:
            raise ValueError("observed execution order_id does not match order")
        if now.tzinfo is None or now.utcoffset() is None or now.tzinfo is not UTC:
            raise ValueError("now must use UTC")
        run = self._persistence.get_run(run_id)
        if run is None:
            raise ValueError("paper run does not exist")
        if run.status is not PaperRunStatus.RECONCILIATION_REQUIRED:
            raise ValueError("paper run does not require reconciliation")

        events = self._persistence.audit_events(run_id)
        if any(
            event.event_type is AuditEventType.EXECUTION_RECONCILED
            and dict(event.payload).get("status") == observed.status.value
            for event in events
        ):
            return PaperReconciliationResult(
                run=run,
                status=ReconciliationStatus.MATCHED,
                observed=observed,
                portfolio_updated=any(
                    event.event_type is AuditEventType.PORTFOLIO_UPDATED
                    for event in events
                ),
                audit_events=events,
            )

        if observed.status is OrderStatus.UNKNOWN:
            self._append_reconciled(run, observed, now, ReconciliationStatus.UNKNOWN)
            return PaperReconciliationResult(
                run=run,
                status=ReconciliationStatus.UNKNOWN,
                observed=observed,
                portfolio_updated=False,
                audit_events=self._persistence.audit_events(run_id),
            )

        self._append_reconciled(run, observed, now, ReconciliationStatus.MATCHED)
        self._persistence.append_audit_event(
            AuditEvent(
                event_id=f"{run_id}:portfolio-updated:{len(events) + 1}",
                run_id=run_id,
                event_type=AuditEventType.PORTFOLIO_UPDATED,
                occurred_at=now,
                sequence=len(events) + 1,
                payload=(("status", observed.status.value),),
            )
        )
        completed = run.complete(now)
        self._persistence.append_audit_event(
            AuditEvent(
                event_id=f"{run_id}:completed:{len(events) + 2}",
                run_id=run_id,
                event_type=AuditEventType.RUN_COMPLETED,
                occurred_at=now,
                sequence=len(events) + 2,
                payload=(("status", completed.status.value),),
            )
        )
        self._persistence.save_run(completed)
        return PaperReconciliationResult(
            run=completed,
            status=ReconciliationStatus.MATCHED,
            observed=observed,
            portfolio_updated=True,
            audit_events=self._persistence.audit_events(run_id),
        )

    def _append_reconciled(
        self,
        run: PaperTradingRun,
        observed: ExecutionEvent,
        now: datetime,
        status: ReconciliationStatus,
    ) -> None:
        events = self._persistence.audit_events(run.run_id)
        self._persistence.append_audit_event(
            AuditEvent(
                event_id=f"{run.run_id}:reconciled:{len(events)}",
                run_id=run.run_id,
                event_type=AuditEventType.EXECUTION_RECONCILED,
                occurred_at=now,
                sequence=len(events),
                payload=(
                    ("order_id", observed.order_id),
                    ("status", observed.status.value),
                    ("reconciliation", status.value),
                ),
            )
        )
