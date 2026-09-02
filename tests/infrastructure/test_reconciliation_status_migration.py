"""Tests for the Phase 3.4 SQLite status migration."""

from datetime import UTC, datetime
from pathlib import Path
import sqlite3

from tradeos.execution import PaperRunStatus, PaperTradingRun
from tradeos.infrastructure import SQLitePaperTradingRepository


NOW = datetime(2026, 9, 2, 10, 0, tzinfo=UTC)


def _run() -> PaperTradingRun:
    return PaperTradingRun(
        run_id="legacy-run",
        proposal_id="proposal-1",
        risk_decision_id="risk-1",
        authorization_id="auth-1",
        account_id="account-1",
        instrument_id="AAPL",
        configuration_hash="config-1",
        started_at=NOW,
    )


def test_legacy_database_migrates_before_reconciliation_required_save(tmp_path: Path) -> None:
    database = tmp_path / "tradeos.sqlite3"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE paper_runs (
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
        CREATE TABLE audit_events (
            event_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            sequence INTEGER NOT NULL CHECK (sequence >= 0),
            payload TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (run_id) REFERENCES paper_runs(run_id),
            UNIQUE (run_id, sequence)
        );
        CREATE INDEX idx_paper_runs_account ON paper_runs(account_id);
        CREATE INDEX idx_paper_runs_instrument ON paper_runs(instrument_id);
        CREATE INDEX idx_audit_events_run ON audit_events(run_id, sequence);
        """
    )
    connection.commit()
    connection.close()

    with SQLitePaperTradingRepository(database) as repository:
        pending = _run().require_reconciliation()
        repository.save_run(_run())
        repository.save_run(pending)
        assert repository.require_run("legacy-run").status is PaperRunStatus.RECONCILIATION_REQUIRED
