# TradeOS Domain Model

**Document:** `22_DOMAIN_MODEL.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Canonical domain objects, identifiers, relationships, ownership, invariants, and lifecycle boundaries

---

## 1. Purpose

This document defines the canonical domain model for TradeOS. It establishes the nouns used by the platform so that architecture, APIs, persistence, events, agents, workflows, and tests use consistent meanings.

The model follows the TradeOS principle:

> **Intent, authorization, execution evidence, and resulting state are different things and must never be conflated.**

This document complements the Project Vision, System Architecture, Agent Architecture, Risk Management, Execution Architecture, Agent Contracts, and Configuration documents.

---

## 2. Domain Design Principles

1. Domain objects have one canonical meaning.
2. Every material object has a stable identifier.
3. Historical records are append-oriented and reproducible.
4. Facts are separated from interpretations and recommendations.
5. External-system state is never assumed to equal internal intent.
6. Safety-critical calculations are deterministic.
7. Every decision references the versions/configuration used to produce it.
8. Objects must be validatable independently of an LLM.
9. Unknown state is represented explicitly where applicable.
10. Domain objects must support paper and live execution without changing their semantics.

---

# 3. Domain Map

```text
Market
  └── Instrument
        └── Market Data / Market Snapshot

Strategy
  └── Strategy Version
        └── Trade Proposal
              ├── Analysis Evidence
              ├── Prediction
              ├── Critic Review
              ├── Portfolio Review
              └── Risk Decision
                       │
                       ▼
                 Authorization
                       │
                       ▼
                  Order Intent
                       │
                       ▼
                     Order
                       │
                       ▼
                     Fill
                       │
                       ▼
                   Position
                       │
                       ▼
                     Trade
                       │
                       ▼
                  Journal Record
                       │
                       ▼
                 Learning Objects
```

---

# 4. Identifier Rules

Every persisted domain object must use a stable unique identifier.

Recommended convention:

```text
<entity>_id
```

Examples:

```text
trade_proposal_id
risk_decision_id
authorization_id
order_intent_id
order_id
fill_id
position_id
trade_id
workflow_id
strategy_id
strategy_version_id
model_version_id
configuration_version_id
```

Identifiers must not encode mutable business meaning.

---

# 5. Temporal Model

Important domain records should distinguish:

```text
occurred_at      = when the real-world event occurred
observed_at      = when TradeOS observed it
created_at       = when the record was created
updated_at       = when the record changed
valid_from       = when the object became valid
valid_until      = when applicable
```

Backtesting and decision systems must respect information availability at the decision timestamp.

---

# 6. Core Domain Objects

## 6.1 Market

Represents an exchange, venue, or logical market environment.

Required concepts:

```text
market_id
name
asset_classes
timezone
sessions
holiday_calendar
status
```

A Market defines market rules; it does not define a trading strategy.

## 6.2 Instrument

Represents a tradable security or contract.

Required concepts:

```text
instrument_id
symbol
market_id
asset_class
currency
tick_size
lot_size
contract_multiplier
trading_status
valid_from
valid_until
```

Instrument metadata must be versionable where historical changes matter.

## 6.3 Market Data Observation

Represents a point-in-time market observation.

Examples:

```text
quote
trade
ohlcv
volume
order_book
corporate_event
```

A data observation must preserve source, timestamps, quality, and provenance where applicable.

## 6.4 Market Snapshot

Represents the normalized state used by a workflow at a specific decision point.

It should reference the underlying observations rather than copying unverifiable facts into free text.

---

# 7. Strategy Domain

## 7.1 Strategy

Logical identity of a strategy.

```text
strategy_id
name
owner
status
```

## 7.2 Strategy Version

Immutable definition of a strategy at a point in time.

```text
strategy_version_id
strategy_id
version
rules
supported_markets
supported_timeframes
risk_assumptions
validation_status
created_at
approved_at
```

A production decision must reference a specific Strategy Version, never only a mutable strategy name.

---

# 8. Trade Proposal

`TradeProposal` is the canonical object representing a proposed trading action before authorization.

Minimum fields:

```text
proposal_id
workflow_id
instrument_id
market_id
direction
strategy_id
strategy_version_id
entry
stop
invalidation
target_or_exit_framework
position_size
maximum_loss
risk_percent
thesis
evidence_refs
contradictory_evidence_refs
prediction_ref
regime_ref
status
created_at
expires_at
```

A proposal is **not** an order and is **not** authorization.

Possible statuses:

```text
CREATED
ANALYZING
READY_FOR_REVIEW
REJECTED
APPROVED_FOR_AUTHORIZATION
EXPIRED
CANCELLED
```

---

# 9. Analysis Evidence

Evidence records what a component relied upon.

Each evidence reference should identify:

```text
evidence_id
source_type
source_id
observed_at
available_at
fact_or_interpretation
confidence_if_applicable
```

Agents must distinguish:

```text
FACT
CALCULATION
INFERENCE
ASSUMPTION
HYPOTHESIS
```

---

# 10. Prediction

Represents probabilistic or scenario-based model output.

```text
prediction_id
model_version_id
instrument_id
horizon
scenarios
calibration_metadata
uncertainty
created_at
```

A Prediction cannot authorize a trade.

---

# 11. Risk Decision

Represents the outcome of risk evaluation.

```text
risk_decision_id
proposal_id
account_id
risk_engine_version
risk_configuration_version
risk_amount
risk_percent
position_size
portfolio_state_ref
drawdown_state
daily_loss_state
decision
reason_codes
created_at
expires_at
```

Canonical decisions:

```text
APPROVED
REJECTED
REQUIRES_REVIEW
```

A deterministic hard rejection is terminal for that authorization attempt.

---

# 12. Execution Authorization

Represents permission for a specific action to cross the execution boundary.

```text
authorization_id
proposal_id
risk_decision_id
account_id
instrument_id
direction
approved_quantity
price_constraints
stop_constraints
operating_mode
configuration_hash
issued_at
expires_at
status
```

Authorization must be specific, time-bounded where appropriate, and immutable after issuance.

Authorization is not itself a broker order.

---

# 13. Order Intent

Represents the exact action TradeOS intends to send to an execution interface.

```text
order_intent_id
authorization_id
account_id
instrument_id
side
quantity
order_type
price
stop_price
time_in_force
idempotency_key
created_at
```

An Order Intent is immutable once submitted for execution.

---

# 14. Order

Represents a normalized broker-facing order state.

```text
order_id
order_intent_id
broker_id
broker_order_id
status
submitted_at
updated_at
filled_quantity
average_fill_price
```

The internal Order must retain the relationship to the Order Intent.

---

# 15. Fill

Represents actual execution evidence reported by a broker or simulator.

```text
fill_id
order_id
broker_fill_id
quantity
price
fees
occurred_at
observed_at
```

A Fill is evidence of execution. It must not be replaced by intended entry values.

---

# 16. Position

Represents current exposure for an account/instrument.

A Position must distinguish:

```text
intended_position
recorded_position
broker_position
```

The canonical operational position should be derived from reconciled execution evidence.

Possible states:

```text
OPENING
OPEN
REDUCING
CLOSING
CLOSED
RECONCILIATION_REQUIRED
UNKNOWN
```

---

# 17. Trade

A Trade represents the complete economic lifecycle of a strategy-driven position from entry through closure.

It should reference:

```text
trade_id
proposal_id
strategy_version_id
authorization_id
entry_order_ids
exit_order_ids
fill_ids
position_id
opened_at
closed_at
realized_pnl
fees
slippage
outcome
```

A Trade must not be marked closed until the required position reconciliation is complete.

---

# 18. Workflow

A Workflow is the bounded execution context for a multi-step TradeOS process.

```text
workflow_id
workflow_type
trigger
operating_mode
started_at
completed_at
status
iteration_count
time_budget
correlation_id
```

Workflows may produce proposals, analyses, risk decisions, orders, learning records, or reports.

---

# 19. Agent Request and Response

Agent communication uses the contracts defined in `20_AGENT_CONTRACTS.md`.

Every request/response must be traceable to:

```text
workflow_id
request_id
agent_id
agent_version
```

Agent output is interpretation or analysis unless explicitly identified as deterministic system data.

---

# 20. Configuration Snapshot

Every material decision should be reproducible against the configuration used.

```text
configuration_version_id
configuration_hash
resolved_configuration
created_at
```

Risk, Strategy, Prediction, and Execution decisions must preserve relevant configuration references.

---

# 21. Journal Record

The Journal is the historical record of decisions and outcomes.

It should reference facts rather than duplicate mutable state.

A journal record may include:

```text
journal_record_id
workflow_id
proposal_id
risk_decision_id
authorization_id
order_refs
position_refs
trade_id
evidence_refs
lessons_refs
created_at
```

Historical facts must not be rewritten to make outcomes look better.

---

# 22. Learning Objects

TradeOS learning should use separate objects.

### Learning Observation

A single observed behavior or outcome.

### Learning Pattern

A recurring pattern supported by multiple observations.

### Learning Recommendation

A proposed intervention based on a validated pattern.

### Approved Learning Rule

A governed, versioned rule approved for future use.

The lifecycle is:

```text
Observation → Pattern → Validation → Recommendation → Approval → Active Rule
```

---

# 23. Ownership

| Object | Primary Owner |
|---|---|
| Market | Market Configuration |
| Instrument | Market/Data Services |
| Market Data | Data Services |
| Strategy | Strategy Governance |
| Strategy Version | Strategy Governance |
| Trade Proposal | Workflow/Strategy subsystem |
| Prediction | Prediction subsystem |
| Risk Decision | Risk subsystem |
| Authorization | Risk/Execution boundary |
| Order Intent | Execution subsystem |
| Order | Execution/Broker Adapter |
| Fill | Broker/Execution subsystem |
| Position | Reconciliation subsystem |
| Trade | Trade/Journal subsystem |
| Configuration | Configuration subsystem |
| Learning Pattern | Learning subsystem |
| Approved Learning Rule | Governance |

No agent owns the entire domain model.

---

# 24. Cross-Domain Invariants

The following are system invariants:

1. No Order Intent without valid authorization.
2. No authorization without required Risk approval.
3. No execution of an expired authorization.
4. No live execution in a mode that forbids it.
5. No position state may be considered broker-confirmed without reconciliation evidence.
6. No Trade may be closed solely from an intended exit.
7. No production strategy decision may omit the Strategy Version.
8. No material risk decision may omit the Risk Engine/configuration version.
9. No backtest may use data unavailable at the simulated decision time.
10. No learning rule becomes active without the required governance process.
11. No historical fact may be silently rewritten.
12. Unknown external state must remain UNKNOWN until reconciled.

---

# 25. Serialization

Domain objects crossing service boundaries must use versioned schemas.

Recommended format:

```text
JSON for APIs/events
Parquet/Arrow-compatible structures for analytical datasets where appropriate
Relational records for transactional state
```

Serialization must preserve identifiers, timestamps, versions, and status semantics.

---

# 26. Implementation Rule

Application code must use these canonical domain concepts rather than inventing local equivalents.

If a new object is required, its meaning and ownership must be documented before it becomes a cross-system contract.

---

## 27. Related Documents

- `01_PROJECT_VISION.md`
- `04_SYSTEM_ARCHITECTURE.md`
- `05_AGENT_ARCHITECTURE.md`
- `08_RISK_MANAGEMENT.md`
- `12_EXECUTION_ARCHITECTURE.md`
- `20_AGENT_CONTRACTS.md`
- `21_CONFIGURATION.md`
- `23_STATE_MACHINES.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`

---

**TradeOS Domain Principle**

> **Define the object once. Preserve its identity. Never confuse intention with reality.**
