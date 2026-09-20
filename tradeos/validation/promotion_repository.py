"""Persistence port for immutable promotion transitions and lifecycle history."""

from abc import ABC, abstractmethod

from tradeos.validation.promotion import PromotionStageTransition
from tradeos.validation.promotion_audit import PromotionTransitionAuditEvent


class PromotionTransitionRepository(ABC):
    """Persistence boundary for immutable promotion transitions and lifecycle events."""

    @abstractmethod
    def get(self, transition_id: str) -> PromotionStageTransition | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, transition: PromotionStageTransition) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_for_strategy(self, strategy_id: str) -> tuple[PromotionStageTransition, ...]:
        raise NotImplementedError

    @abstractmethod
    def list_for_review(self, review_id: str) -> tuple[PromotionStageTransition, ...]:
        raise NotImplementedError

    @abstractmethod
    def append_audit_event(self, event: PromotionTransitionAuditEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_audit_history(
        self, *, transition_id: str | None = None
    ) -> tuple[PromotionTransitionAuditEvent, ...]:
        raise NotImplementedError
