"""SQLite persistence for governed paper-trading runs and append-only audit events."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from tradeos.execution import AuditEvent, AuditEventType, PaperRunStatus, PaperTradingRun


class SQLitePaperTradingRepository:
    """Durable local repository for paper runs and their audit histories."""

    def __init__(self, database_path: str | Path) -> None:
        self._path = str(database_path)
        self._connection = sqlite3.connect(self._path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._connection.close()

    def __enter__(self) -> "SQLitePaperTradingRepository":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def save_run(self, run: PaperTradingRun) -> None:
        """Insert or replace a validated run snapshot."""
        run.validate()
        self._connection.execute(
            """
            INSERT INTO paper_runs (
                run_id, proposal_id, risk_decision_id, authorization_id,
                account_id, instrument_id, configuration_hash,
                started_at, status, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                proposal_id=excluded.proposal_id,
                risk_decision_id=excluded.risk_decision_id,
                authorization_id=excluded.authorization_id,
                account_id=excluded.account_id,
                instrument_id=excluded.instrument_id,
                configuration_hash=excluded.configuration_hash,
                started_at=excluded.started_at,
                status=excluded.status,
                completed_at=excluded.completed_at
            """,
            (
                run.run_id,
                run.proposal_id,
                run.risk_decision_id,
                run.authorization_id,
                run.account_id,
                run.instrument_id,
                run.configuration_hash,
                _encode_datetime(run.started_at),
                run.status.value,
                _encode_datetime(run.completed_at),
            ),
        )
        self._connection.commit()

    def get_run(self, run_id: str) -> PaperTradingRun | None:
        """Return a persisted run snapshot, or None when it is unknown."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        row = self._connection.execute(
            "SELECT * FROM paper_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return _decode_run(row) if row else None

    def require_run(self, run_id: str) -> PaperTradingRun:
        """Return a persisted run or raise KeyError."""
        run = self.get_run(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def list_runs(
        self,
        *,
        status: PaperRunStatus | None = None,
        account_id: str | None = None,
        instrument_id: str | None = None,
    ) -> tuple[PaperTradingRun, ...]:
        """Return runs in stable registration order with optional filters."""
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
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"SELECT * FROM paper_runs {where} ORDER BY rowid ASC", parameters
        ).fetchall()
        return tuple(_decode_run(row) for row in rows)

    def append_audit_event(self, event: AuditEvent) -> None:
        """Append one immutable audit event with contiguous per-run sequencing."""
        event.validate()
        if self.get_run(event.run_id) is None:
            raise KeyError(event.run_id)
        expected = self._connection.execute(
            "SELECT COUNT(*) AS count FROM audit_events WHERE run_id = ?", (event.run_id,)
        ).fetchone()["count"]
        if event.sequence != expected:
            raise ValueError("audit sequence must be contiguous")
        try:
            self._connection.execute(
                """
                INSERT INTO audit_events (
                    event_id, run_id, event_type, occurred_at, sequence, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.event_type.value,
                    _encode_datetime(event.occurred_at),
                    event.sequence,
                    json.dumps(dict(event.payload), sort_keys=True),
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as exc:
            self._connection.rollback()
            if "event_id" in str(exc):
                raise ValueError("duplicate event_id") from exc
            raise

    def audit_events(self, run_id: str) -> tuple[AuditEvent, ...]:
        """Return the complete immutable audit history for a run."""
        if not run_id:
            raise ValueError("run_id must not be empty")
        rows = self._connection.execute(
            "SELECT * FROM audit_events WHERE run_id = ? ORDER BY sequence ASC", (run_id,)
        ).fetchall()
        return tuple(_decode_event(row) for row in rows)

    def export_audit_events(self, run_id: str) -> tuple[dict[str, object], ...]:
        """Return audit records in a serialization-friendly representation."""
        return tuple(
            {
                "event_id": event.event_id,
                "run_id": event.run_id,
                "event_type": event.event_type.value,
                "occurred_at": event.occurred_at.isoformat(),
                "sequence": event.sequence,
                "payload": dict(event.payload),
            }
            for event in self.audit_events(run_id)
        )

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS paper_runs (
                run_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                risk_decision_id TEXT NOT NULL,
                authorization_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                instrument_id TEXT NOT NULL,
                configuration_hash TEXT NOT NULL,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('OPEN', 'COMPLETED', 'FAILED')),
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                sequence INTEGER NOT NULL CHECK (sequence >= 0),
                payload TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (run_id) REFERENCES paper_runs(run_id),
                UNIQUE (run_id, sequence)
            );

            CREATE INDEX IF NOT EXISTS idx_paper_runs_account
                ON paper_runs(account_id);
            CREATE INDEX IF NOT EXISTS idx_paper_runs_instrument
                ON paper_runs(instrument_id);
            CREATE INDEX IF NOT EXISTS idx_audit_events_run
                ON audit_events(run_id, sequence);
            """
        )
        self._connection.commit()


def _encode_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None or value.tzinfo is not UTC:
        raise ValueError("datetime must use UTC")
    return value.isoformat()


def _decode_datetime(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None or result.tzinfo is not UTC:
        raise ValueError("persisted datetime must use UTC")
    return result


def _decode_run(row: sqlite3.Row) -> PaperTradingRun:
    run = PaperTradingRun(
        run_id=row["run_id"],
        proposal_id=row["proposal_id"],
        risk_decision_id=row["risk_decision_id"],
        authorization_id=row["authorization_id"],
        account_id=row["account_id"],
        instrument_id=row["instrument_id"],
        configuration_hash=row["configuration_hash"],
        started_at=_decode_datetime(row["started_at"]),
        status=PaperRunStatus(row["status"]),
        completed_at=_decode_datetime(row["completed_at"]) if row["completed_at"] else None,
    )
    run.validate()
    return run


def _decode_event(row: sqlite3.Row) -> AuditEvent:
    payload = tuple(sorted(json.loads(row["payload"]).items())) if row["payload"] else ()
    event = AuditEvent(
        event_id=row["event_id"],
        run_id=row["run_id"],
        event_type=AuditEventType(row["event_type"]),
        occurred_at=_decode_datetime(row["occurred_at"]),
        sequence=row["sequence"],
        payload=payload,
    )
    event.validate()
    return event
