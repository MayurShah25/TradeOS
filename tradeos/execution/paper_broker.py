"""Deterministic in-memory broker used exclusively for paper execution."""

from .models import Order, OrderStatus
from .ports import BrokerExecutionPort


class PaperBroker(BrokerExecutionPort):
    """Accept valid orders and fill them without any external side effects."""

    def __init__(self) -> None:
        self._orders: dict[str, OrderStatus] = {}

    def submit(self, order: Order) -> OrderStatus:
        """Validate and idempotently process an order."""
        order.validate()
        existing = self._orders.get(order.order_id)
        if existing is not None:
            return existing
        self._orders[order.order_id] = OrderStatus.FILLED
        return OrderStatus.FILLED

    def status(self, order_id: str) -> OrderStatus | None:
        """Return the known status for an order."""
        return self._orders.get(order_id)
