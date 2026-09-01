"""Deterministic order lifecycle transition rules."""

from typing import ClassVar

from tradeos.execution.models import OrderStatus


class InvalidOrderTransition(ValueError):
    """Raised when an order attempts an unsupported lifecycle transition."""


class OrderStateMachine:
    """Enforce the canonical paper-execution lifecycle."""

    _TRANSITIONS: ClassVar[dict[OrderStatus | None, frozenset[OrderStatus]]] = {
        None: frozenset({OrderStatus.ACCEPTED, OrderStatus.REJECTED}),
        OrderStatus.ACCEPTED: frozenset({OrderStatus.FILLED, OrderStatus.REJECTED}),
        OrderStatus.FILLED: frozenset(),
        OrderStatus.REJECTED: frozenset(),
    }

    @classmethod
    def transition(cls, current: OrderStatus | None, target: OrderStatus) -> OrderStatus:
        """Return target when the lifecycle transition is valid."""
        if target not in cls._TRANSITIONS.get(current, frozenset()):
            current_name = current.value if current else "NEW"
            raise InvalidOrderTransition(
                f"Invalid order transition: {current_name} -> {target.value}"
            )
        return target
