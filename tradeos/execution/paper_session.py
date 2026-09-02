"""Deterministic paper-trading orchestration boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Self

from .audit import AuditEvent, AuditEventType, AuditTrail
from .authorization import AuthorizationLedger
from .authorized_gateway import AuthorizedExecutionGateway, ExecutionGatewayResult
from .lifecycle import ExecutionEvent, ExecutionEventType
from .models import Order, OrderStatus
from .ports import PaperTradingPersistencePort
from .run_state import PaperTradingRun

if TYPE_CHECKING:
    from tradeos.portfolio.execution_pipeline import (
        ExecutionPortfolioPipeline,
        ExecutionProcessingResult,
    )
    from tradeos.portfolio.portfolio_risk_controls import (
        PortfolioRiskLimits,
        PortfolioRiskResult,
    )
    from tradeos.portfolio.risk_context import RiskContext


@dataclass(frozen=True, slots=True)
class PaperTradingResult:
    """Immutable result of one governed paper-trading attempt."""

    risk: PortfolioRiskResult
    execution: ExecutionGatewayResult
    processing: ExecutionProcessingResult
    run: PaperTradingRun | None = None
    audit_events: tuple[AuditEvent, ...] = ()


class PaperTradingSession:
    """Sequence risk, authorization, execution, and reconciliation for paper trading."""

    def __init__(
        self,
        gateway: AuthorizedExecutionGateway,
        authorization_ledger: AuthorizationLedger,
        portfolio_pipeline: ExecutionPortfolioPipeline | None = None,
        audit_trail: AuditTrail | None = None,
        persistence: PaperTradingPersistencePort | None = None,
    ) -> None:
        from tradeos.portfolio.execution_pipeline import ExecutionPortfolioPipeline

        self._gateway = gateway
        self._authorization_ledger = authorization_ledger
        self._portfolio_pipeline = portfolio_pipeline or ExecutionPortfolioPipeline()
        self._persistence = persistence
        self._audit_trail = audit_trail or (AuditTrail() if persistence is not None else None)

    def execute(
        self,
        authorization_id: str,
        risk_decision_id: str,
        order: Order,
        context: RiskContext,
        limits: PortfolioRiskLimits,
        prices: dict[str, Decimal],
        now: datetime,
        run: PaperTradingRun | None = None,
    ) -> PaperTradingResult:
        """Run one order through hard risk controls and the authorized paper boundary."""
        from tradeos.portfolio.portfolio_risk_controls import PortfolioRiskControls

        order.validate()
        context.validate()
        if now.tzinfo is None or now.utcoffset() is None or now.tzinfo is not UTC:
            raise ValueError("now must use UTC")
        audit_trail = self._audit_trail
        if run is not None:
            run.validate()
            if run.risk_decision_id != risk_decision_id or run.authorization_id != authorization_id:
                raise PermissionError("run identity does not match execution request")
            if run.instrument_id != order.instrument_id:
                raise PermissionError("run instrument does not match order")
            if audit_trail is None:
                raise ValueError("audit_trail is required when run is supplied")
            self._persist_run(run)

        try:
            if run is not None:
                self._record(audit_trail, run, AuditEventType.RUN_STARTED, now, {})

            risk = PortfolioRiskControls.evaluate(context, limits, order, prices)
            if run is not None:
                self._record(
                    audit_trail,
                    run,
                    AuditEventType.RISK_EVALUATED,
                    now,
                    {"approved": str(risk.approved)},
                )
            if not risk.approved:
                raise PermissionError("portfolio risk controls rejected the order")

            authorization = self._authorization_ledger.get(authorization_id)
            if authorization.risk_decision_id != risk_decision_id:
                raise PermissionError("authorization does not match the risk decision")
            if run is not None:
                if run.account_id != authorization.account_id:
                    raise PermissionError("run account does not match authorization account")
                self._record(audit_trail, run, AuditEventType.AUTHORIZATION_VERIFIED, now, {})

            execution = self._gateway.execute(authorization_id, order, now)
            if run is not None:
                self._record(
                    audit_trail,
                    run,
                    AuditEventType.EXECUTION_SUBMITTED,
                    now,
                    {"order_id": order.order_id, "status": execution.status.value},
                )

            accepted_event = ExecutionEvent(
                order_id=order.order_id,
                status=OrderStatus.ACCEPTED,
                event_type=ExecutionEventType.ACCEPTED,
                timestamp=now,
            )
            self._portfolio_pipeline.process(order, None, accepted_event, OrderStatus.ACCEPTED)

            event_type = ExecutionEventType(execution.status.value)
            filled_quantity = order.quantity if execution.status is OrderStatus.FILLED else Decimal(0)
            event = ExecutionEvent(
                order_id=order.order_id,
                status=execution.status,
                event_type=event_type,
                timestamp=now,
                filled_quantity=filled_quantity,
            )
            processing = self._portfolio_pipeline.process(
                order,
                OrderStatus.ACCEPTED,
                event,
                execution.status,
                prices[order.instrument_id] if execution.status is OrderStatus.FILLED else None,
            )
            if run is not None:
                self._record(
                    audit_trail,
                    run,
                    AuditEventType.EXECUTION_RECONCILED,
                    now,
                    {"status": execution.status.value},
                )
                self._record(audit_trail, run, AuditEventType.PORTFOLIO_UPDATED, now, {})
                completed = run.complete(now)
                self._record(
                    audit_trail,
                    run,
                    AuditEventType.RUN_COMPLETED,
                    now,
                    {"status": completed.status.value},
                )
                self._persist_run(completed)
                assert audit_trail is not None
                return PaperTradingResult(
                    risk,
                    execution,
                    processing,
                    completed,
                    audit_trail.events(run.run_id),
                )
            return PaperTradingResult(risk, execution, processing)
        except Exception:
            if run is not None:
                self._persist_failure(run, now)
            raise

    def _persist_run(self, run: PaperTradingRun) -> None:
        if self._persistence is not None:
            self._persistence.save_run(run)

    def _persist_failure(self, run: PaperTradingRun, now: datetime) -> None:
        try:
            failed = run.fail(now)
            audit_trail = self._audit_trail
            if audit_trail is not None:
                self._record(audit_trail, run, AuditEventType.RUN_FAILED, now, {})
            self._persist_run(failed)
        except Exception:  # noqa: BLE001
            # Preserve the original execution exception; recovery can inspect the open run.
            return

    def _record(
        self,
        audit_trail: AuditTrail | None,
        run: PaperTradingRun,
        event_type: AuditEventType,
        occurred_at: datetime,
        payload: dict[str, str],
    ) -> None:
        if audit_trail is None:
            raise ValueError("audit_trail is required")
        sequence = len(audit_trail.events(run.run_id))
        event = AuditEvent(
            event_id=f"{run.run_id}:{sequence}:{event_type.value}",
            run_id=run.run_id,
            event_type=event_type,
            occurred_at=occurred_at,
            sequence=sequence,
            payload=tuple(sorted(payload.items())),
        )
        audit_trail.append(event)
        if self._persistence is not None:
            self._persistence.append_audit_event(event)
