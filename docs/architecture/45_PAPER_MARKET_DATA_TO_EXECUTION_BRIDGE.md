# Paper Market Data to Execution Bridge

**Status:** Implemented / Tested  
**Phase:** 6.4

## 1. Purpose

Phase 6.4 establishes the deterministic boundary that connects validated, ordered, persisted paper market data to the existing governed paper-trading session.

The bridge supplies the execution workflow with a single authoritative market price from the latest accepted stream observation. It does not create a strategy signal, trade proposal, risk approval, execution authorization, or broker connection.

## 2. Canonical Flow

```text
Validated Snapshot
      ↓
Ordered Paper Market Data Stream
      ↓
Immutable Paper Market Data Repository
      ↓
Paper Market Data → Execution Bridge
      ↓
Coherent Risk Context + Market Price
      ↓
Deterministic Portfolio Risk Controls
      ↓
Execution Authorization
      ↓
Paper Execution
      ↓
Reconciliation / Portfolio Processing
```

The bridge requires the latest stream observation to have an exact persisted counterpart before execution can begin.

## 3. Responsibilities

The bridge:

- reads only the latest accepted stream snapshot;
- verifies the exact snapshot is persisted;
- enforces market-data freshness;
- verifies the snapshot instrument matches the order;
- builds a coherent deterministic RiskContext using that price;
- passes the price into the existing PaperTradingSession;
- leaves Risk, authorization, execution, reconciliation, and portfolio mutation to their existing boundaries.

## 4. Non-Responsibilities

The bridge must not:

- infer a trading signal from price;
- create or modify a trade proposal;
- issue or bypass execution authorization;
- override deterministic Risk rejection;
- call an external broker;
- mutate portfolio state directly;
- resubmit ambiguous orders;
- treat persistence as execution authority;
- silently repair missing or inconsistent market data.

## 5. Fail-Closed Conditions

Execution is rejected when:

1. no stream observation exists;
2. the latest observation is not exactly persisted;
3. the observation is stale, future-dated, or otherwise invalid;
4. the observation instrument does not match the order;
5. the requested freshness window is invalid.

Failures occur before the existing session consumes execution authorization.

## 6. Authority Boundary

The bridge is a data-integration boundary, not an authority boundary:

```text
Market Data
    ≠
Strategy Signal
    ≠
Trade Proposal
    ≠
Risk Approval
    ≠
Execution Authorization
    ≠
Execution
```

The existing PaperTradingSession remains responsible for deterministic risk evaluation, authorization verification, paper execution, reconciliation, and portfolio processing.

## 7. Paper-Only Scope

Phase 6.4 remains strictly within paper trading. The bridge has no live broker dependency and cannot enable live financial exposure.

## 8. Testing Requirements

Coverage includes:

- successful execution from an ordered and persisted snapshot;
- missing persistence;
- stale data;
- instrument mismatch;
- invalid freshness configuration;
- preservation of execution authorization when the bridge rejects input.

## 9. Architectural Outcome

Phase 6.4 closes the data-to-execution integration gap without collapsing authority boundaries. Market data becomes an explicit, auditable input to the existing paper execution workflow while Risk and execution authorization remain deterministic gates.