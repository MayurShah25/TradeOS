"""Immutable lifecycle audit events for promotion stage transitions."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class PromotionTransitionAuditEventType(StrEnum):
    """Lifecycle events recorded outside the execution audit boundary."""

    TRANSITION_RECORDED = "TRANSITION_RECORDED"


@dataclass(frozen=True, slots=True)
class PromotionTransitionAuditEvent:
    """Immutable audit event describing a promotion lifecycle action."""

    event_id: str
    transition_id: str
    review_id: str
    evidence_id: str
    event_type: PromotionTransitionAuditEventType
    actor_id: str
    occurred_at: datetime
    detail: str

    def __post_init__(self) -> None:
        for name, value in (
            ("event_id", self.event_id),
            ("transition_id", self.transition_id),
            ("review_id", self.review_id),
            ("evidence_id", self.evidence_id),
            ("actor_id", self.actor_id),
            ("detail", self.detail),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be blank")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        if self.occurred_at.tzinfo is not UTC:
            raise ValueError("occurred_at must use UTC")
