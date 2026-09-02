# 30 — Paper Trading Recovery

**Status:** Implementation baseline — Phase 3 recovery safety  
**Canonical owner:** Execution / Infrastructure boundary

## Purpose

Provide a safe recovery inspection boundary for paper-trading runs that remain `OPEN` after a process interruption.

## Safety Rule

An interrupted run is **not** automatically retried, resubmitted, completed, or converted into a successful execution.

Recovery only reconstructs the persisted run and audit history and marks the run as requiring explicit reconciliation.

## Recovery Flow

```text
Persisted OPEN Run
        ↓
Load Run Snapshot
        ↓
Load Append-Only Audit History
        ↓
Build Recovery Assessment
        ↓
Require Explicit Reconciliation
        ↓
No Automatic Order Retry
```

## Recovery Assessment

Each assessment contains:

- the immutable `PaperTradingRun` snapshot;
- the complete persisted audit history available for the run;
- a `requires_reconciliation` safety flag;
- a deterministic reason describing the last known audit boundary.

Runs that are already `COMPLETED` or `FAILED` are not returned as interrupted runs.

Creating an assessment is read-only: inspecting recovery state must not mutate the persisted run or audit history.

## Ambiguous Execution

If the last persisted event is before or around broker submission, persistence cannot prove that no broker-side action occurred. Therefore recovery must treat the run as requiring reconciliation rather than issuing another order.

This preserves the execution integrity rule:

```text
Unknown broker state
        ≠
No execution
```

## Boundary

The recovery component is deliberately read-only with respect to trading state. It does not submit orders, alter authorization, mutate risk decisions, or bypass the execution gateway.

A future reconciliation service may consume a recovery assessment and, after explicit broker verification, apply a governed lifecycle transition.

## Testing Requirements

Recovery tests must verify:

- only `OPEN` runs are surfaced;
- persisted audit history is returned in sequence order;
- runs without audit history remain recoverable and require reconciliation;
- closed runs are excluded;
- recovery performs no execution or retry action;
- recovery inspection does not mutate persisted state.
