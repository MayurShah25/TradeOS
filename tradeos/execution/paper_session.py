"""Deterministic paper-trading orchestration boundary."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from tradeos.portfolio.execution_pipeline import (
    ExecutionPortfolioPipeline,
    ExecutionProcessingResult,
)
from tradeos.portfolio.portfolio_risk_controls import (
    PortfolioRiskLimits,
    PortfolioRiskResult,
    PortfolioRiskControls,
)
from tradeos.portfolio.risk_context import RiskContext

from .authorized_gateway import AuthorizedExecutionGateway, ExecutionGatewayResult
from .authorization import AuthorizationLedger
from .lifecycle import ExecutionEvent, ExecutionEventType
from .models import Order, OrderStatus


@dataclass(frozen=True, slots=True)
class PaperTradingResult:
    """Immutable result of one governed paper-trading attempt."""

    risk: PortfolioRiskResult
    execution: ExecutionGatewayResult
    processing: ExecutionProcessingResult


class PaperTradingSession:
    """Sequence risk, authorization, execution, and reconciliation for paper trading."""

    def __init__(
        self,
        gateway: AuthorizedExecutionGateway,
        authorization_ledger: AuthorizationLedger,
        portfolio_pipeline: ExecutionPortfolioPipeline | None = None,
    ) -> None:
        self._gateway = gateway
        self._authorization_ledger = authorization_ledger
        self._portfolio_pipeline = portfolio_pipeline or ExecutionPortfolioPipeline()

    def execute(
        self,
        authorization_id: str,
        risk_decision_id: str,
        order: Order,
        context: RiskContext,
        limits: PortfolioRiskLimits,
        prices: dict[str, Decimal],
        now: datetime,
    ) -> PaperTradingResult:
        """Run one order through hard risk controls and the authorized paper boundary."""
        order.validate()
        context.validate()
        if now.tzinfo is None or now.utcoffset() is None or now.tzinfo is not UTC:
            raise ValueError("now must use UTC")

        risk = PortfolioRiskControls.evaluate(context, limits, order, prices)
        if not risk.approved:
            raise PermissionError("portfolio risk controls rejected the order")

        authorization = self._authorization_ledger.get(authorization_id)
        if authorization.risk_decision_id != risk_decision_id:
            raise PermissionError("authorization does not match the risk decision")

        execution = self._gateway.execute(authorization_id, order, now)
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
            None,
            event,
            execution.status,
            prices[order.instrument_id] if execution.status is OrderStatus.FILLED else None,
        )
        return PaperTradingResult(risk, execution, processing)
