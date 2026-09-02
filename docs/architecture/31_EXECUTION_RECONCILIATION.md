# 31 — Execution Outcome & Reconciliation

**Status:** Implementation baseline — Phase 3.4
**Canonical owner:** Execution boundary

## Purpose

Define the deterministic semantics for execution outcomes that are known, rejected, or ambiguous, especially when a submission response may have been lost.

## Core Rule

> **An ambiguous execution outcome is not a failed execution. It requires reconciliation.**

TradeOS must preserve the distinction between:

```text
KNOWN SUCCESS
KNOWN REJECTION / FAILURE
UNKNOWN BROKER STATE
```

## Outcome Flow

```text
Authorized Order
      ↓
Execution Attempt
      ↓
Broker Observation
      ├── FILLED / ACCEPTED / REJECTED
      │        ↓
      │    Normal processing
      │
      └── UNKNOWN
               ↓
      RECONCILIATION_REQUIRED
               ↓
       Broker verification
               ↓
        MATCHED / MISMATCHED / UNKNOWN
```

## Run Lifecycle

Paper runs use these states:

```text
OPEN
  ├──→ RECONCILIATION_REQUIRED
  ├──→ COMPLETED
  └──→ FAILED
```

`RECONCILIATION_REQUIRED` is non-terminal. It must not carry `completed_at` and may only become terminal after an explicit resolution path.

A process restart must preserve this state.

## Ambiguous Submission

The authorized execution gateway consumes the authorization before submission. If the broker adapter reports that the outcome cannot be determined, the gateway returns `UNKNOWN` rather than throwing an ordinary failure.

This produces:

```text
Authorization = CONSUMED
Execution = UNKNOWN
Run = RECONCILIATION_REQUIRED
```

This is intentional. A consumed authorization does not prove that a broker order was created, and an ambiguous response does not prove that it was not created.

## Portfolio Safety

An `UNKNOWN` execution must not:

- create a fill;
- change position quantity;
- update portfolio state as though a fill occurred;
- complete the run;
- retry or resubmit the order.

Only verified execution evidence may update the portfolio.

## Reconciliation Results

The execution reconciler distinguishes:

```text
MATCHED
MISMATCHED
UNKNOWN
```

`UNKNOWN` includes both an absent observation and an explicit unknown broker outcome. It is never converted into `FAILED` merely because a response was unavailable.

A mismatch requires investigation and execution restriction according to the applicable safety policy. It is not silently converted into success.

## Recovery

Recovery inspection must surface both `OPEN` interrupted runs and runs already marked `RECONCILIATION_REQUIRED`.

Recovery remains inspection-only until a future explicit reconciliation command supplies verified external evidence.

No recovery path may blindly resubmit an order.

## Persistence

SQLite persists the `RECONCILIATION_REQUIRED` state and migrates earlier Phase 3 databases that used the previous run-status constraint.

Audit history records `RECONCILIATION_REQUIRED` after an ambiguous execution submission. The event is append-only and remains part of the run's deterministic history.

## Testing Requirements

At minimum verify:

- ambiguous broker submission becomes `UNKNOWN`;
- authorization remains consumed after ambiguous submission;
- unknown execution does not update the portfolio;
- run becomes `RECONCILIATION_REQUIRED` and remains non-terminal;
- reconciliation-required state survives restart;
- recovery surfaces reconciliation-required runs;
- explicit unknown observation remains `UNKNOWN` in the reconciler;
- legacy SQLite databases can migrate to the new run state;
- known failures still use the terminal failure path;
- no automatic retry or resubmission occurs.
