"""SQLite persistence for immutable validation evidence and lineage."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from tradeos.validation import ValidationEvidence, ValidationStage
from tradeos.validation.repository import ValidationEvidenceRepository


class SQLiteValidationEvidenceRepository(ValidationEvidenceRepository):
    """Durable local repository for validation evidence snapshots."""

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

    def save(self, evidence: ValidationEvidence) -> None:
        """Persist an immutable evidence snapshot, allowing only idempotent re-save."""
        existing = self.get(evidence.evidence_id)
        if existing is not None:
            if existing != evidence:
                raise ValueError("validation evidence is immutable")
            return

        self._connection.execute(
            """
            INSERT INTO validation_evidence (
                evidence_id, strategy_id, strategy_version, dataset_version,
                configuration_version, code_version, generated_at,
                gate_results, known_limitations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence.evidence_id,
                evidence.strategy_id,
                evidence.strategy_version,
                evidence.dataset_version,
                evidence.configuration_version,
                evidence.code_version,
                _encode_datetime(evidence.generated_at),
                json.dumps(
                    [
                        {"stage": stage.value, "passed": passed}
                        for stage, passed in evidence.gate_results
                    ],
                    separators=(",", ":"),
                ),
                json.dumps(list(evidence.known_limitations), separators=(",", ":")),
            ),
        )
        self._connection.commit()

    def get(self, evidence_id: str) -> ValidationEvidence | None:
        """Return one immutable evidence snapshot, or None when unknown."""
        if not evidence_id:
            raise ValueError("evidence_id must not be empty")
        row = self._connection.execute(
            "SELECT * FROM validation_evidence WHERE evidence_id = ?",
            (evidence_id,),
        ).fetchone()
        return _decode_evidence(row) if row else None

    def list_for_strategy(
        self,
        strategy_id: str,
        *,
        strategy_version: str | None = None,
    ) -> tuple[ValidationEvidence, ...]:
        """Return evidence in stable insertion order with optional version filtering."""
        if not strategy_id:
            raise ValueError("strategy_id must not be empty")
        if strategy_version == "":
            raise ValueError("strategy_version must not be empty")

        if strategy_version is None:
            rows = self._connection.execute(
                """
                SELECT * FROM validation_evidence
                WHERE strategy_id = ?
                ORDER BY rowid ASC
                """,
                (strategy_id,),
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT * FROM validation_evidence
                WHERE strategy_id = ? AND strategy_version = ?
                ORDER BY rowid ASC
                """,
                (strategy_id, strategy_version),
            ).fetchall()
        return tuple(_decode_evidence(row) for row in rows)

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS validation_evidence (
                evidence_id TEXT PRIMARY KEY,
                strategy_id TEXT NOT NULL,
                strategy_version TEXT NOT NULL,
                dataset_version TEXT NOT NULL,
                configuration_version TEXT NOT NULL,
                code_version TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                gate_results TEXT NOT NULL,
                known_limitations TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_validation_evidence_strategy
                ON validation_evidence(strategy_id, strategy_version);
            CREATE INDEX IF NOT EXISTS idx_validation_evidence_lineage
                ON validation_evidence(
                    strategy_id, strategy_version, dataset_version,
                    configuration_version, code_version
                );
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


def _decode_evidence(row: sqlite3.Row) -> ValidationEvidence:
    gate_results = tuple(
        (ValidationStage(item["stage"]), bool(item["passed"]))
        for item in json.loads(row["gate_results"])
    )
    known_limitations = tuple(json.loads(row["known_limitations"]))
    return ValidationEvidence(
        evidence_id=row["evidence_id"],
        strategy_id=row["strategy_id"],
        strategy_version=row["strategy_version"],
        dataset_version=row["dataset_version"],
        configuration_version=row["configuration_version"],
        code_version=row["code_version"],
        generated_at=_decode_datetime(row["generated_at"]),
        gate_results=gate_results,
        known_limitations=known_limitations,
    )
