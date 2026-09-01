"""Deterministic execution-to-portfolio processing boundary."""

from dataclasses import dataclass
from decimal import Decimal

from tradeos.execution import Order, OrderStateMachine, OrderStatus
from tradeos.execution.lifecycle import ExecutionEvent, ExecutionEventType, ExecutionReconciler

from .portfolio_state import PortfolioState, PortfolioStateBuilder
from .position_ledger import PositionLedger


@dataclass(frozen=True, slots=True)
class ExecutionProcessingResult:
    """Immutable result of processing one execution event."""

    order: Order
    status: OrderStatus
    reconciled: bool
    portfolio: PortfolioState


class ExecutionPortfolioPipeline:
    """Connect order state, execution events, reconciliation, and accounting."""

    def __init__(self, ledger: PositionLedger | None = None) -> None:
        self._ledger = ledger or PositionLedger()

    @property
    def ledger(self) -> PositionLedger:
        """Return the deterministic position ledger used by this pipeline."""
        return self._ledger

    def process(
        self,
        order: Order,
        current_status: OrderStatus | None,
        event: ExecutionEvent,
        observed_status: OrderStatus | None,
        fill_price: Decimal | None = None,
    ) -> ExecutionProcessingResult:
        """Process an execution event and mutate accounting only after reconciliation."""
        order.validate()
        event.validate()
        if event.order_id != order.order_id:
            raise ValueError("execution event order_id does not match order")

        expected_event_type = ExecutionEventType(event.status.value)
        if event.event_type is not expected_event_type:
            raise ValueError("execution event status and event_type must agree")

        status = OrderStateMachine.transition(current_status, event.status)
        reconciliation = ExecutionReconciler.reconcile(
            order.order_id, status, observed_status
        )
        if not reconciliation.matched:
            raise ValueError("execution reconciliation mismatch")

        if status is OrderStatus.FILLED:
            if fill_price is None:
                raise ValueError("fill_price is required for a filled execution")
            self._ledger.apply_fill(
                order.instrument_id,
                order.side,
                event.filled_quantity,
                fill_price,
            )

        return ExecutionProcessingResult(
            order=order,
            status=status,
            reconciled=True,
            portfolio=PortfolioStateBuilder.snapshot(self._ledger),
        )
