"""Deterministic gateway between authorization and broker execution."""

from dataclasses import dataclass
from datetime import UTC, datetime

from .authorization import AuthorizationLedger
from .models import Order, OrderStatus
from .ports import BrokerExecutionPort


@dataclass(frozen=True, slots=True)
class ExecutionGatewayResult:
    """Immutable result of an authorized execution attempt."""

    authorization_id: str
    order_id: str
    status: OrderStatus


class AuthorizedExecutionGateway:
    """Require valid, unexpired, single-use authorization before execution."""

    def __init__(self, broker: BrokerExecutionPort, ledger: AuthorizationLedger) -> None:
        self._broker = broker
        self._ledger = ledger

    def execute(
        self,
        authorization_id: str,
        order: Order,
        now: datetime,
    ) -> ExecutionGatewayResult:
        """Validate authorization scope, consume it once, then submit the order."""
        order.validate()
        if now.tzinfo is None or now.utcoffset() is None or now.tzinfo is not UTC:
            raise ValueError("now must use UTC")

        authorization = self._ledger.consume(authorization_id)
        if not authorization.permits(order, now):
            raise PermissionError("authorization does not permit this order")

        status = self._broker.submit(order)
        return ExecutionGatewayResult(authorization_id, order.order_id, status)
