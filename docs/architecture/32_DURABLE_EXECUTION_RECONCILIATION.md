# Durable Execution Reconciliation

## Purpose

Phase 3.5 adds an explicit, persisted reconciliation command for paper runs that are in `RECONCILIATION_REQUIRED`.

The command consumes a verified execution observation. It never retries submission, releases consumed authorization, or calls a broker submission boundary.

## Boundary

`PaperTradingReconciliation` is a recovery-side application service between persisted run state and the portfolio execution pipeline.

Inputs:

- persisted `run_id`
- the original `Order` identity and immutable order attributes
- one verified `ExecutionEvent`
- UTC reconciliation time
- a fill price map when the observed event is `FILLED`

Outputs:

- immutable `PaperReconciliationResult`
- durable audit history
- terminal `COMPLETED` state only after a known execution outcome has been processed

## Outcome rules

| Observation | Result | Portfolio | Run |
|---|---|---|---|
| `UNKNOWN` | remains `UNKNOWN` | unchanged | `RECONCILIATION_REQUIRED` |
| `ACCEPTED` | `MATCHED` | processed, no position fill | `COMPLETED` |
| `REJECTED` | `MATCHED` | processed, no position fill | `COMPLETED` |
| `FILLED` | `MATCHED` | accepted transition plus fill applied | `COMPLETED` |

An unknown observation is never converted into success or failure. A verified known observation is the only input that can resolve the pending execution.

## Audit sequence

For a successful reconciliation the durable sequence is:

1. `RECONCILIATION_REQUIRED`
2. `EXECUTION_RECONCILED`
3. `PORTFOLIO_UPDATED`
4. `RUN_COMPLETED`

An `UNKNOWN` observation records `EXECUTION_RECONCILED` with reconciliation status `UNKNOWN` and leaves the run non-terminal.

## Safety properties

- No broker submission occurs during reconciliation.
- No automatic retry or resubmission is possible through this boundary.
- A consumed authorization is not released automatically.
- Portfolio mutation happens only for a verified known outcome.
- `FILLED` requires a valid fill price and positive fill quantity through the existing portfolio pipeline.
- Reconciliation is rejected for missing or already-closed runs.
- Order identity is checked before any state transition.

## Persistence limitation

Run snapshots and audit events are durable, but the current repository API persists them as separate operations. The reconciliation service therefore does not claim database-level atomicity across portfolio mutation, audit append, and run completion.

A future transactional repository boundary should couple these effects into one durable unit before any live execution capability is introduced.

## Live-execution boundary

This phase remains paper-only. The reconciliation service consumes an observation; it does not obtain that observation by submitting an order. Any future live adapter must preserve the same rule: ambiguous submission remains unresolved until independently verified evidence is supplied.
