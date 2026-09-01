import pytest

from tradeos.execution import OrderStatus
from tradeos.execution.state_machine import InvalidOrderTransition, OrderStateMachine


def test_new_order_can_be_accepted() -> None:
    assert OrderStateMachine.transition(None, OrderStatus.ACCEPTED) is OrderStatus.ACCEPTED


def test_new_order_can_be_rejected() -> None:
    assert OrderStateMachine.transition(None, OrderStatus.REJECTED) is OrderStatus.REJECTED


def test_accepted_order_can_be_filled() -> None:
    assert OrderStateMachine.transition(OrderStatus.ACCEPTED, OrderStatus.FILLED) is OrderStatus.FILLED


def test_accepted_order_can_be_rejected() -> None:
    assert OrderStateMachine.transition(OrderStatus.ACCEPTED, OrderStatus.REJECTED) is OrderStatus.REJECTED


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (None, OrderStatus.FILLED),
        (OrderStatus.FILLED, OrderStatus.ACCEPTED),
        (OrderStatus.FILLED, OrderStatus.REJECTED),
        (OrderStatus.REJECTED, OrderStatus.ACCEPTED),
        (OrderStatus.REJECTED, OrderStatus.FILLED),
    ],
)
def test_invalid_transitions_are_rejected(current: OrderStatus | None, target: OrderStatus) -> None:
    with pytest.raises(InvalidOrderTransition):
        OrderStateMachine.transition(current, target)
