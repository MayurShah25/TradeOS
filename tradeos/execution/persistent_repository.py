"""Durable repository for paper-trading runs and append-only audit events."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from .audit import AuditEvent, AuditEventType
from .run_registry import PaperRunRegistry
from .run_state import PaperRunStatus, PaperTradingRun


class SqlitePaperRunAuditRepository:
    """SQLite-backed persistence boundary for governed paper-trading history."""

    def __init__(self, database: str | Path) -> None:
        self._connection = sqlite3.connect(str(database))
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def save_run(self, run: PaperTradingRun) -> None:
        """Persist a validated run snapshot under its stable identifier."""
        run.validate()
        existing = self.get_run(run.run_id)
        if existing is None:
            self._connection.execute(
                "INSERT INTO paper_runs (run_id, proposal_id, risk_decision_id, authorization_id, account_id, instrument_id, configuration_hash, started_at, status, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                self._run_values(run),
            )
        else:
            self._validate_identity_unchanged(existing, run)
            self._connection.execute(
                "UPDATE paper_runs SET status = ?, completed_at = ? WHERE run_id = ?",
                (run.status.value, self._encode_datetime(run.completed_at), run.run_id),
            )
        self._connection.commit()

    def get_run(self, run_id: str) -> PaperTradingRun | None:
        """Return a persisted run snapshot, or None when it is unknown."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        row = self._connection.execute(
            "SELECT * FROM paper_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return None if row is None else self._run_from_row(row)

    def require_run(self, run_id: str) -> PaperTradingRun:
        """Return a persisted run or raise a deterministic lookup error."""
        run = self.get_run(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def runs(
        self,
        *,
        status: PaperRunStatus | None = None,
        account_id: str | None = None,
        instrument_id: str | None = None,
    ) -> tuple[PaperTradingRun, ...]:
        """Return persisted runs in registration order with optional filters."""
        if account_id == "":
            raise ValueError("account_id must not be empty")
        if instrument_id == "":
            raise ValueError("instrument_id must not be empty")
        clauses: list[str] = []
        parameters: list[str] = []
        if status is not None:
            clauses.append("status = ?")
            parameters.append(status.value)
        if account_id is not None:
            clauses.append("account_id = ?")
            parameters.append(account_id)
        if instrument_id is not None:
            clauses.append("instrument_id = ?")
            parameters.append(instrument_id)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"SELECT * FROM paper_runs{where} ORDER BY registration_order", parameters
        ).fetchall()
        return tuple(self._run_from_row(row) for row in rows)

    def append_audit_event(self, event: AuditEvent) -> None:
        """Append one immutable audit event with a contiguous per-run sequence."""
        event.validate()
        if self.get_run(event.run_id) is None:
            raise KeyError(event.run_id)
        next_sequence = self._connection.execute(
            "SELECT COALESCE(MAX(sequence) + 1, 0) FROM audit_events WHERE run_id = ?",
            (event.run_id,),
        ).fetchone()[0]
        if event.sequence != next_sequence:
            raise ValueError("audit sequence must be contiguous")
        try:
            self._connection.execute(
                "INSERT INTO audit_events (event_id, run_id, event_type, occurred_at, sequence, payload) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    event.run_id,
                    event.event_type.value,
                    self._encode_datetime(event.occurred_at),
                    event.sequence,
                    json.dumps(event.payload, separators=(",", ":")),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            self._connection.rollback()
            raise ValueError("duplicate event_id") from exc

    def audit_events(self, run_id: str) -> tuple[AuditEvent, ...]:
        """Return the immutable ordered audit history for a run."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        rows = self._connection.execute(
            "SELECT event_id, run_id, event_type, occurred_at, sequence, payload "
            "FROM audit_events WHERE run_id = ? ORDER BY sequence",
            (run_id,),
        ).fetchall()
        return tuple(self._event_from_row(row) for row in rows)

    def hydrate_registry(self, registry: PaperRunRegistry) -> None:
        """Load all persisted run snapshots into an in-memory registry."""
        for run in self.runs():
            if registry.get(run.run_id) is None:
                registry.register(run)
            else:
                registry.update(run)

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS paper_runs (
                registration_order INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL UNIQUE,
                proposal_id TEXT NOT NULL,
                risk_decision_id TEXT NOT NULL,
                authorization_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                configuration_hash TEXT NOT NULL,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL,
                completed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                payload TEXT NOT NULL,
                UNIQUE(run_id, sequence),
                FOREIGN KEY(run_id) REFERENCES paper_runs(run_id)
            );
            """
        )
        self._connection.commit()

    @staticmethod
    def _validate_identity_unchanged(
        existing: PaperTradingRun, replacement: PaperTradingRun
    ) -> None:
        fields = (
            "proposal_id",
            "risk_decision_id",
            "authorization_id",
            "account_id",
            "instrument_id",
            "configuration_hash",
            "started_at",
        )
        if any(getattr(existing, field) != getattr(replacement, field) for field in fields):
            raise ValueError("run identity cannot change")
        if existing.status is not PaperRunStatus.OPEN and replacement.status is not existing.status:
            raise ValueError("closed run status cannot change")

    @staticmethod
    def _run_values(run: PaperTradingRun) -> tuple[object, ...]:
        return (
            run.run_id,
            run.proposal_id,
            run.risk_decision_id,
            run.authorization_id,
            run.account_id,
            run.instrument_id,
            run.configuration_hash,
            SqlitePaperRunAuditRepository._encode_datetime(run.started_at),
            run.status.value,
            SqlitePaperRunAuditRepository._encode_datetime(run.completed_at),
        )

    @staticmethod
    def _run_from_row(row: tuple[Any, ...]) -> PaperTradingRun:
        completed_at = None
        if row[10] is not None:
            completed_at = SqlitePaperRunAuditRepository._decode_datetime(row[10])
        return PaperTradingRun(
            run_id=row[1],
            proposal_id=row[2],
            risk_decision_id=row[3],
            authorization_id=row[4],
            account_id=row[5],
            instrument_id=row[6],
            configuration_hash=row[7],
            started_at=SqlitePaperRunAuditRepository._decode_datetime(row[8]),
            status=PaperRunStatus(row[9]),
            completed_at=completed_at,
        )

    @staticmethod
    def _event_from_row(row: tuple[Any, ...]) -> AuditEvent:
        event = AuditEvent(
            event_id=row[0],
            run_id=row[1],
            event_type=AuditEventType(row[2]),
            occurred_at=SqlitePaperRunAuditRepository._decode_datetime(row[3]),
            sequence=row[4],
            payload=tuple(tuple(item) for item in json.loads(row[5])),
        )
        event.validate()
        return event

    @staticmethod
    def _encode_datetime(value: datetime | None) -> str | None:
        return None if value is None else value.isoformat()

    @staticmethod
    def _decode_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value).astimezone(UTC)
