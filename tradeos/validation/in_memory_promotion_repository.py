"""In-memory persistence for immutable promotion transitions and lifecycle history."""

from tradeos.validation.promotion import PromotionStageTransition
from tradeos.validation.promotion_audit import PromotionTransitionAuditEvent
from tradeos.validation.promotion_repository import PromotionTransitionRepository


class InMemoryPromotionTransitionRepository(PromotionTransitionRepository):
    """Deterministic repository that rejects mutation and duplicate lifecycle events."""

    def __init__(self) -> None:
        self._transitions: dict[str, PromotionStageTransition] = {}
        self._audit_events: dict[str, PromotionTransitionAuditEvent] = {}

    def get(self, transition_id: str) -> PromotionStageTransition | None:
        if not transition_id:
            raise ValueError("transition_id must not be empty")
        return self._transitions.get(transition_id)

    def save(self, transition: PromotionStageTransition) -> None:
        existing = self.get(transition.transition_id)
        if existing is not None and existing != transition:
            raise ValueError("promotion transition is immutable")
        self._transitions[transition.transition_id] = transition

    def list_for_strategy(self, strategy_id: str) -> tuple[PromotionStageTransition, ...]:
        if not strategy_id:
            raise ValueError("strategy_id must not be empty")
        return tuple(
            transition
            for transition in self._transitions.values()
            if transition.strategy_id == strategy_id
        )

    def list_for_review(self, review_id: str) -> tuple[PromotionStageTransition, ...]:
        if not review_id:
            raise ValueError("review_id must not be empty")
        return tuple(
            transition
            for transition in self._transitions.values()
            if transition.review_id == review_id
        )

    def append_audit_event(self, event: PromotionTransitionAuditEvent) -> None:
        transition = self.get(event.transition_id)
        if transition is None:
            raise ValueError("audit event references unknown transition")
        if (
            transition.review_id != event.review_id
            or transition.evidence_id != event.evidence_id
        ):
            raise ValueError("audit event lineage does not match transition")
        existing = self._audit_events.get(event.event_id)
        if existing is not None and existing != event:
            raise ValueError("promotion transition audit event is immutable")
        self._audit_events[event.event_id] = event

    def list_audit_history(
        self, *, transition_id: str | None = None
    ) -> tuple[PromotionTransitionAuditEvent, ...]:
        if transition_id == "":
            raise ValueError("transition_id must not be empty")
        return tuple(
            event
            for event in self._audit_events.values()
            if transition_id is None or event.transition_id == transition_id
        )
