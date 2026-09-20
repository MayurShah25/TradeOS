"""SQLite persistence for immutable promotion transitions and lifecycle history."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from tradeos.validation.promotion import PromotionStage, PromotionStageTransition
from tradeos.validation.promotion_audit import (
    PromotionTransitionAuditEvent,
    PromotionTransitionAuditEventType,
)
from tradeos.validation.promotion_repository import PromotionTransitionRepository


class SQLitePromotionTransitionRepository(PromotionTransitionRepository):
    """Durable local repository for promotion transitions and lifecycle audit history."""

    def __init__(self, database_path: str | Path) -> None:
        self._connection = sqlite3.connect(str(database_path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def save(self, transition: PromotionStageTransition) -> None:
        existing = self.get(transition.transition_id)
        if existing is not None:
            if existing != transition:
                raise ValueError("promotion transition is immutable")
            return
        self._connection.execute(
            """
            INSERT INTO promotion_transitions (
                transition_id, review_id, evidence_id, strategy_id,
                strategy_version, from_stage, to_stage
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transition.transition_id,
                transition.review_id,
                transition.evidence_id,
                transition.strategy_id,
                transition.strategy_version,
                transition.from_stage.value,
                transition.to_stage.value,
            ),
        )
        self._connection.commit()

    def get(self, transition_id: str) -> PromotionStageTransition | None:
        if not transition_id:
            raise ValueError("transition_id must not be empty")
        row = self._connection.execute(
            "SELECT * FROM promotion_transitions WHERE transition_id = ?",
            (transition_id,),
        ).fetchone()
        return _decode_transition(row) if row else None

    def list_for_strategy(self, strategy_id: str) -> tuple[PromotionStageTransition, ...]:
        if not strategy_id:
            raise ValueError("strategy_id must not be empty")
        rows = self._connection.execute(
            """
            SELECT * FROM promotion_transitions
            WHERE strategy_id = ?
            ORDER BY rowid ASC
            """,
            (strategy_id,),
        ).fetchall()
        return tuple(_decode_transition(row) for row in rows)

    def list_for_review(self, review_id: str) -> tuple[PromotionStageTransition, ...]:
        if not review_id:
            raise ValueError("review_id must not be empty")
        rows = self._connection.execute(
            """
            SELECT * FROM promotion_transitions
            WHERE review_id = ?
            ORDER BY rowid ASC
            """,
            (review_id,),
        ).fetchall()
        return tuple(_decode_transition(row) for row in rows)

    def append_audit_event(self, event: PromotionTransitionAuditEvent) -> None:
        transition = self.get(event.transition_id)
        if transition is None:
            raise ValueError("audit event references unknown transition")
        if (
            transition.review_id != event.review_id
            or transition.evidence_id != event.evidence_id
        ):
            raise ValueError("audit event lineage does not match transition")
        existing = self._connection.execute(
            "SELECT * FROM promotion_transition_audit WHERE event_id = ?",
            (event.event_id,),
        ).fetchone()
        if existing is not None:
            if _decode_audit_event(existing) != event:
                raise ValueError("promotion transition audit event is immutable")
            return
        self._connection.execute(
            """
            INSERT INTO promotion_transition_audit (
                event_id, transition_id, review_id, evidence_id, event_type,
                actor_id, occurred_at, detail
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.transition_id,
                event.review_id,
                event.evidence_id,
                event.event_type.value,
                event.actor_id,
                _encode_datetime(event.occurred_at),
                event.detail,
            ),
        )
        self._connection.commit()

    def list_audit_history(
        self, *, transition_id: str | None = None
    ) -> tuple[PromotionTransitionAuditEvent, ...]:
        if transition_id == "":
            raise ValueError("transition_id must not be empty")
        if transition_id is None:
            rows = self._connection.execute(
                "SELECT * FROM promotion_transition_audit ORDER BY rowid ASC"
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT * FROM promotion_transition_audit
                WHERE transition_id = ?
                ORDER BY rowid ASC
                """,
                (transition_id,),
            ).fetchall()
        return tuple(_decode_audit_event(row) for row in rows)

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS promotion_transitions (
                transition_id TEXT PRIMARY KEY,
                review_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                from_stage TEXT NOT NULL,
                to_stage TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_promotion_transitions_strategy
                ON promotion_transitions(strategy_id);
            CREATE INDEX IF NOT EXISTS idx_promotion_transitions_review
                ON promotion_transitions(review_id);

            CREATE TABLE IF NOT EXISTS promotion_transition_audit (
                event_id TEXT PRIMARY KEY,
                transition_id TEXT NOT NULL,
                review_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                detail TEXT NOT NULL,
                FOREIGN KEY(transition_id) REFERENCES promotion_transitions(transition_id)
            );

            CREATE INDEX IF NOT EXISTS idx_promotion_transition_audit_transition
                ON promotion_transition_audit(transition_id);
            """
        )
        self._connection.commit()


def _encode_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None or value.tzinfo is not UTC:
        raise ValueError("datetime must use UTC")
    return value.isoformat()


def _decode_datetime(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None or result.tzinfo is not UTC:
        raise ValueError("persisted datetime must use UTC")
    return result


def _decode_transition(row: sqlite3.Row) -> PromotionStageTransition:
    return PromotionStageTransition(
        transition_id=row["transition_id"],
        review_id=row["review_id"],
        evidence_id=row["evidence_id"],
        strategy_id=row["strategy_id"],
        strategy_version=row["strategy_version"],
        from_stage=PromotionStage(row["from_stage"]),
        to_stage=PromotionStage(row["to_stage"]),
    )


def _decode_audit_event(row: sqlite3.Row) -> PromotionTransitionAuditEvent:
    return PromotionTransitionAuditEvent(
        event_id=row["event_id"],
        transition_id=row["transition_id"],
        review_id=row["review_id"],
        evidence_id=row["evidence_id"],
        event_type=PromotionTransitionAuditEventType(row["event_type"]),
        actor_id=row["actor_id"],
        occurred_at=_decode_datetime(row["occurred_at"]),
        detail=row["detail"],
    )
