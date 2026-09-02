# 29 — Paper Trading Persistence & Audit Repository

**Status:** Implementation baseline — Phase 3  
**Canonical owner:** Execution / Infrastructure boundary

## Purpose

Provide durable local persistence for governed paper-trading runs and an append-only audit history without coupling the execution domain to a storage technology.

## Scope

This phase persists:

- `PaperTradingRun` identity and lifecycle state.
- Run status: `OPEN`, `COMPLETED`, or `FAILED`.
- Proposal, risk-decision, authorization, account, instrument, and configuration identities.
- UTC start/completion timestamps.
- Ordered audit events associated with each run.
- Structured event payloads suitable for export and later analytics.

This phase does **not** introduce live trading, broker credentials, autonomous execution, or a production distributed database.

## Storage Boundary

The domain remains independent of persistence. The existing repository abstraction defines the infrastructure boundary; SQLite is the first durable adapter for local paper trading.

```text
Paper Trading Domain
        |
        v
Repository / Persistence Boundary
        |
        v
SQLitePaperTradingRepository
        |
        v
SQLite database file
```

SQLite is deliberately used at this stage because it is durable, transactional, dependency-light, and sufficient for a single-user paper-trading run repository. PostgreSQL remains the intended production-scale direction when deployment requirements justify it.

## Run Persistence Rules

1. Every run has a stable unique `run_id`.
2. Run identity fields are validated before persistence.
3. Timestamps must be timezone-aware UTC values.
4. Open runs may transition to `COMPLETED` or `FAILED` through the domain state model.
5. Closed run snapshots are immutable.
6. A persisted run can be reopened from a later process using the same database file.
7. Run queries support status, account, and instrument filtering while preserving deterministic registration order.

## Audit Persistence Rules

Audit events are append-only records. They are never updated or deleted by the repository.

Each event contains:

- stable `event_id`;
- `run_id`;
- canonical `event_type`;
- UTC `occurred_at` timestamp;
- contiguous zero-based `sequence` within the run;
- structured key/value payload.

The repository rejects:

- events for unknown runs;
- duplicate event IDs;
- non-contiguous event sequences;
- invalid audit records.

The database additionally enforces foreign-key ownership and unique `(run_id, sequence)` values.

## Canonical Paper Run Audit Sequence

The current governed execution path records the following sequence:

```text
0 RUN_STARTED
1 RISK_EVALUATED
2 AUTHORIZATION_VERIFIED
3 EXECUTION_SUBMITTED
4 EXECUTION_RECONCILED
5 PORTFOLIO_UPDATED
6 RUN_COMPLETED
```

Failure handling may use `RUN_FAILED` in the same append-only sequence model.

## Recovery

A process restart must not erase paper-trading history. The next process can open the same SQLite database, retrieve the run snapshot, and inspect its complete audit event sequence.

Ambiguous execution state remains governed by the execution/reconciliation layer; persistence is responsible for preserving what the system actually observed, not for converting uncertainty into success.

## Export

The repository provides a serialization-friendly audit export containing event identity, event type, timestamp, sequence, run identity, and structured payload. This export is intended for later reporting, analytics, review, and archival workflows.

## Testing Requirements

The persistence adapter must verify at minimum:

- run survives repository close/reopen;
- run lifecycle updates survive restart;
- filters return deterministic snapshots;
- audit history survives restart;
- unknown runs are rejected for audit writes;
- sequence gaps are rejected;
- duplicate event IDs are rejected;
- closed runs cannot be silently rewritten.

## Phase 3 Boundary

The repository is a durable paper-trading foundation, not a live-trading persistence system. Before controlled live trading, the architecture must add stronger operational controls for migrations, backups, concurrency, retention, access control, production observability, and database availability.
