"""Execution ports separating core order intent from broker implementations."""

from abc import ABC, abstractmethod

from .models import Order, OrderStatus


class BrokerExecutionPort(ABC):
    """Boundary for broker order submission."""

    @abstractmethod
    def submit(self, order: Order) -> OrderStatus:
        """Submit a validated order and return its normalized status."""
        raise NotImplementedError
