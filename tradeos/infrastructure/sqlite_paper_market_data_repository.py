"""SQLite persistence for immutable paper market-data snapshots."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

from tradeos.market_data import PaperMarketDataSnapshot
from tradeos.market_data_repository import PaperMarketDataRepository


class SQLitePaperMarketDataRepository(PaperMarketDataRepository):
    """Durable local repository for validated paper market-data snapshots."""

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

    def save(self, snapshot: PaperMarketDataSnapshot) -> None:
        """Persist a validated snapshot; reject mutation under the same observation key."""
        snapshot.validate()
        existing = self.get(
            instrument_id=snapshot.instrument_id,
            source_id=snapshot.source_id,
            observed_at=snapshot.observed_at,
        )
        if existing is not None:
            if existing != snapshot:
                raise ValueError("paper market-data snapshot is immutable")
            return

        self._connection.execute(
            """
            INSERT INTO paper_market_data_snapshots (
                instrument_id, source_id, observed_at, price
            ) VALUES (?, ?, ?, ?)
            """,
            (
                snapshot.instrument_id,
                snapshot.source_id,
                _encode_datetime(snapshot.observed_at),
                str(snapshot.price),
            ),
        )
        self._connection.commit()

    def get(
        self,
        *,
        instrument_id: str,
        source_id: str,
        observed_at: datetime,
    ) -> PaperMarketDataSnapshot | None:
        """Return one snapshot by its immutable identity."""
        _validate_lookup(instrument_id, source_id, observed_at)
        row = self._connection.execute(
            """
            SELECT instrument_id, source_id, observed_at, price
            FROM paper_market_data_snapshots
            WHERE instrument_id = ? AND source_id = ? AND observed_at = ?
            """,
            (instrument_id, source_id, _encode_datetime(observed_at)),
        ).fetchone()
        return _decode_snapshot(row) if row else None

    def list_for_instrument(
        self,
        *,
        instrument_id: str,
        source_id: str | None = None,
    ) -> tuple[PaperMarketDataSnapshot, ...]:
        """Return snapshots in deterministic observation-time order."""
        if not instrument_id.strip():
            raise ValueError("instrument_id must not be blank")
        if source_id == "":
            raise ValueError("source_id must not be blank")

        if source_id is None:
            rows = self._connection.execute(
                """
                SELECT instrument_id, source_id, observed_at, price
                FROM paper_market_data_snapshots
                WHERE instrument_id = ?
                ORDER BY observed_at ASC, source_id ASC
                """,
                (instrument_id,),
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT instrument_id, source_id, observed_at, price
                FROM paper_market_data_snapshots
                WHERE instrument_id = ? AND source_id = ?
                ORDER BY observed_at ASC
                """,
                (instrument_id, source_id),
            ).fetchall()
        return tuple(_decode_snapshot(row) for row in rows)

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS paper_market_data_snapshots (
                instrument_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                price TEXT NOT NULL,
                PRIMARY KEY (instrument_id, source_id, observed_at)
            );

            CREATE INDEX IF NOT EXISTS idx_paper_market_data_instrument_time
                ON paper_market_data_snapshots(instrument_id, observed_at);
            """
        )
        self._connection.commit()


def _validate_lookup(
    instrument_id: str,
    source_id: str,
    observed_at: datetime,
) -> None:
    if not instrument_id.strip():
        raise ValueError("instrument_id must not be blank")
    if not source_id.strip():
        raise ValueError("source_id must not be blank")
    _encode_datetime(observed_at)


def _encode_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None or value.tzinfo is not UTC:
        raise ValueError("datetime must use UTC")
    return value.isoformat()


def _decode_datetime(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None or result.tzinfo is not UTC:
        raise ValueError("persisted datetime must use UTC")
    return result


def _decode_snapshot(row: sqlite3.Row) -> PaperMarketDataSnapshot:
    return PaperMarketDataSnapshot(
        instrument_id=row["instrument_id"],
        source_id=row["source_id"],
        observed_at=_decode_datetime(row["observed_at"]),
        price=__import__("decimal").Decimal(row["price"]),
    )
