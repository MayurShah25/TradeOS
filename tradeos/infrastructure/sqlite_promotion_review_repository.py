"""SQLite persistence for immutable promotion reviews and governance history."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from tradeos.validation import PromotionReview, PromotionReviewDecision, PromotionEligibility
from tradeos.validation.review_audit import (
    PromotionReviewAuditEvent,
    PromotionReviewAuditEventType,
)
from tradeos.validation.review_repository import PromotionReviewRepository


class SQLitePromotionReviewRepository(PromotionReviewRepository):
    """Durable local repository for promotion review snapshots and audit history."""

    def __init__(self, database_path: str | Path) -> None:
        self._connection = sqlite3.connect(str(database_path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def save(self, review: PromotionReview) -> None:
        """Persist an immutable review snapshot, allowing only idempotent re-save."""
        existing = self.get(review.review_id)
        if existing is not None:
            if existing != review:
                raise ValueError("promotion review is immutable")
            return
        self._connection.execute(
            """
            INSERT INTO promotion_reviews (
                review_id, evidence_id, strategy_id, strategy_version,
                eligibility, decision, reviewer_id, reviewed_at, rationale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.review_id,
                review.evidence_id,
                review.strategy_id,
                review.strategy_version,
                review.eligibility.value,
                review.decision.value,
                review.reviewer_id,
                _encode_datetime(review.reviewed_at) if review.reviewed_at else None,
                review.rationale,
            ),
        )
        self._connection.commit()

    def get(self, review_id: str) -> PromotionReview | None:
        """Return one immutable review snapshot, or None when unknown."""
        if not review_id:
            raise ValueError("review_id must not be empty")
        row = self._connection.execute(
            "SELECT * FROM promotion_reviews WHERE review_id = ?", (review_id,)
        ).fetchone()
        return _decode_review(row) if row else None

    def list_for_evidence(self, evidence_id: str) -> tuple[PromotionReview, ...]:
        """Return review snapshots in stable insertion order."""
        if not evidence_id:
            raise ValueError("evidence_id must not be empty")
        rows = self._connection.execute(
            """
            SELECT * FROM promotion_reviews
            WHERE evidence_id = ?
            ORDER BY rowid ASC
            """,
            (evidence_id,),
        ).fetchall()
        return tuple(_decode_review(row) for row in rows)

    def append_audit_event(self, event: PromotionReviewAuditEvent) -> None:
        """Append an immutable audit event, allowing only idempotent re-save."""
        if self.get(event.review_id) is None:
            raise ValueError("audit event references unknown review")
        existing = self._connection.execute(
            "SELECT * FROM promotion_review_audit WHERE event_id = ?", (event.event_id,)
        ).fetchone()
        if existing is not None:
            if _decode_audit_event(existing) != event:
                raise ValueError("promotion review audit event is immutable")
            return
        self._connection.execute(
            """
            INSERT INTO promotion_review_audit (
                event_id, review_id, evidence_id, event_type,
                actor_id, occurred_at, detail
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
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
        self, *, review_id: str | None = None
    ) -> tuple[PromotionReviewAuditEvent, ...]:
        """Return append-only governance history in stable insertion order."""
        if review_id == "":
            raise ValueError("review_id must not be empty")
        if review_id is None:
            rows = self._connection.execute(
                "SELECT * FROM promotion_review_audit ORDER BY rowid ASC"
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT * FROM promotion_review_audit
                WHERE review_id = ?
                ORDER BY rowid ASC
                """,
                (review_id,),
            ).fetchall()
        return tuple(_decode_audit_event(row) for row in rows)

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS promotion_reviews (
                review_id TEXT PRIMARY KEY,
                evidence_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                eligibility TEXT NOT NULL,
                decision TEXT NOT NULL,
                reviewer_id TEXT,
                reviewed_at TEXT,
                rationale TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_promotion_reviews_evidence
                ON promotion_reviews(evidence_id);

            CREATE TABLE IF NOT EXISTS promotion_review_audit (
                event_id TEXT PRIMARY KEY,
                review_id TEXT NOT NULL,
                evidence_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                detail TEXT NOT NULL,
                FOREIGN KEY(review_id) REFERENCES promotion_reviews(review_id)
            );

            CREATE INDEX IF NOT EXISTS idx_promotion_review_audit_review
                ON promotion_review_audit(review_id, rowid);
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


def _decode_review(row: sqlite3.Row) -> PromotionReview:
    reviewed_at = row["reviewed_at"]
    return PromotionReview(
        review_id=row["review_id"],
        evidence_id=row["evidence_id"],
        strategy_id=row["strategy_id"],
        strategy_version=row["strategy_version"],
        eligibility=PromotionEligibility(row["eligibility"]),
        decision=PromotionReviewDecision(row["decision"]),
        reviewer_id=row["reviewer_id"],
        reviewed_at=_decode_datetime(reviewed_at) if reviewed_at else None,
        rationale=row["rationale"],
    )


def _decode_audit_event(row: sqlite3.Row) -> PromotionReviewAuditEvent:
    return PromotionReviewAuditEvent(
        event_id=row["event_id"],
        review_id=row["review_id"],
        evidence_id=row["evidence_id"],
        event_type=PromotionReviewAuditEventType(row["event_type"]),
        actor_id=row["actor_id"],
        occurred_at=_decode_datetime(row["occurred_at"]),
        detail=row["detail"],
    )
