# TradeOS Execution Architecture

**Document:** 12_EXECUTION_ARCHITECTURE.md  
**Version:** 0.1.1  
**Status:** Architecture Baseline  
**Scope:** Order lifecycle, execution gateway, broker adapters, idempotency, fills, reconciliation, failures, recovery, and execution safety

---

## 1. Purpose

The Execution Architecture defines how an approved TradeOS decision becomes an order and how the system verifies what actually happened.

The central principle is:

> **TradeOS must never confuse an intended action with an executed action.**

The execution layer must be conservative, deterministic where possible, observable, and independently auditable.

Execution is an enforcement boundary, not a reasoning authority. It executes only an action that has passed the required upstream approvals and deterministic execution checks.

---

# 2. Execution Philosophy

Execution should optimize for:

- Correctness
- Safety
- Reliability
- Idempotency
- Reconciliation
- Observability
- Controlled latency
- Broker independence

Execution must never bypass:

```text
Strategy
   ↓
Critic
   ↓
Portfolio
   ↓
Risk
   ↓
Execution
```

No LLM, agent, broker adapter, or execution component may manufacture or elevate trading authority. Execution authorization is a deterministic enforcement step over already-approved authority and current state.

---

# 3. Execution Architecture

```text
Approved Trade Proposal
        ↓
Execution Authorization
        ↓
Execution Engine
        ↓
Pre-Order Validation
        ↓
Idempotency Check
        ↓
Broker Adapter
        ↓
Broker
        ↓
Order Status
        ↓
Fill Events
        ↓
Position Reconciliation
        ↓
Trade State
```

---

# 4. Execution Boundary

The Execution Engine is the boundary between:

```text
Decision World
```

and:

```text
External Financial System
```

Only explicitly authorized actions may cross this boundary.

---

# 5. Execution Authorization

Before an order is submitted, verify:

- Trade proposal exists
- Proposal is approved
- Risk decision is approved
- Risk decision is current
- Account is valid
- Instrument is valid
- Market is eligible
- Operating mode permits execution
- No applicable kill switch is active
- Order has not already been submitted

Execution authorization must be derived from the authoritative approval records and current deterministic state. It is not an opportunity for an agent to reconsider or expand authority.

Authorization should be uniquely bound to the approved trade proposal, account, instrument, intended order parameters, applicable risk decision, configuration/version references, and validity window. Reuse after material state change requires revalidation.

---

# 6. Final Pre-Order Check

Immediately before submission:

```text
Proposal
   ↓
Current Market State
   ↓
Current Account State
   ↓
Current Risk State
   ↓
Order Validation
```

The system should not blindly execute a stale approval.

---

# 7. Stale Authorization

An approval may expire.

Examples:

- Market moved materially
- Stop is no longer valid
- Risk changed
- Portfolio exposure changed
- Daily loss threshold changed
- Market status changed
- Data became stale

The system should support authorization expiration.

---

# 8. Order Intent

Before creating a broker order, create an internal immutable order intent.

Example:

```text
order_intent_id
trade_proposal_id
account_id
instrument_id
side
quantity
order_type
limit_price
stop_price
time_in_force
created_at
authorization_reference
```

This represents what TradeOS intended to send.

---

# 9. Intent vs Order

These must remain distinct:

```text
Order Intent
     ≠
Broker Order
     ≠
Fill
     ≠
Position
```

This distinction is fundamental to reconciliation.

---

# 10. Idempotency

Every execution request should have a unique idempotency key.

Conceptually:

```text
trade_proposal_id
+
order_intent_id
+
execution_attempt
```

The same logical order must not accidentally become multiple broker orders.

---

# 11. Duplicate Order Protection

Before submission:

```text
Check Existing Internal Order
        ↓
Check Broker State Where Possible
        ↓
Submit Only If Safe
```

If the system cannot determine whether an order already exists:

```text
DO NOT BLINDLY RESUBMIT
```

Enter reconciliation.

---

# 12. Execution Attempts

Every submission attempt should be recorded.

Example:

```text
execution_attempt_id
order_intent_id
attempt_number
broker
timestamp
request_hash
response
status
```

This allows duplicate and failure analysis.

---

# 13. Broker Adapter

TradeOS should use broker-specific adapters behind a common interface.

Conceptually:

```text
Execution Engine
      ↓
Broker Interface
      ↓
┌──────────┬──────────┬──────────┐
│ Broker A │ Broker B │ Broker C │
└──────────┴──────────┴──────────┘
```

Core TradeOS logic should not depend directly on broker-specific APIs.

---

# 14. Broker Adapter Responsibilities

The adapter should handle:

- Authentication
- Instrument mapping
- Order submission
- Order cancellation
- Order status
- Fill retrieval
- Position retrieval
- Broker-specific errors
- Rate limits
- Broker-specific order semantics

---

# 15. Canonical Order Model

TradeOS should normalize broker orders into a common internal representation.

Potential fields:

```text
order_id
client_order_id
broker_order_id
account_id
instrument_id
side
quantity
order_type
price
stop_price
time_in_force
status
filled_quantity
average_fill_price
submitted_at
updated_at
```

---

# 16. Order Types

The architecture may support:

```text
MARKET
LIMIT
STOP
STOP_LIMIT
TRAILING
```

Actual availability depends on broker and asset class.

Unsupported order types must be rejected rather than silently transformed into unsafe alternatives.

---

# 17. Time in Force

Examples:

```text
DAY
GTC
IOC
FOK
```

TradeOS must understand broker-specific semantics before using them.

---

# 18. Order Lifecycle

Canonical lifecycle:

```text
CREATED
   ↓
VALIDATING
   ↓
AUTHORIZED
   ↓
SUBMITTING
   ↓
SUBMITTED
   ↓
PARTIALLY_FILLED
   ↓
FILLED
```

Alternative terminal states:

```text
CANCELLED
REJECTED
EXPIRED
FAILED
UNKNOWN
```

---

# 19. Unknown Order State

If the broker response is ambiguous:

```text
UNKNOWN
```

must be a valid state.

The system must not assume:

```text
FAILED
```

simply because no immediate confirmation was received.

---

# 20. Reconciliation

For unknown or mismatched states:

```text
Internal State
      +
Broker State
      ↓
Reconciliation Engine
      ↓
Resolved State
```

Reconciliation should occur before further dependent actions.

---

# 21. Fill Events

A fill is actual execution evidence.

A fill record should contain:

```text
fill_id
order_id
broker_fill_id
quantity
price
fees
timestamp
```

Fills should be treated as authoritative execution evidence from the broker, subject to reconciliation.

---

# 22. Partial Fills

TradeOS must support:

```text
Requested: 100
Filled: 40
Remaining: 60
```

Position state must reflect actual filled quantity.

---

# 23. Partial Fill Management

Depending on strategy and configuration, remaining quantity may be:

- Left working
- Cancelled
- Repriced
- Re-evaluated

Any modification must remain within risk controls.

---

# 24. Fill Price

The actual average fill price should be calculated from fills.

It must not be replaced with the intended entry price.

---

# 25. Execution Slippage

Track:

```text
Expected Price
Actual Fill Price
Slippage
```

For multiple fills, use appropriate weighted calculations.

---

# 26. Execution Latency

Track:

```text
Signal Time
Authorization Time
Order Creation Time
Submission Time
Broker Acknowledgment
Fill Time
```

This enables latency analysis.

---

# 27. Market Impact

Where meaningful, execution analytics may estimate:

- Spread cost
- Market impact
- Slippage
- Liquidity consumption

This can feed strategy and execution learning.

---

# 28. Order Cancellation

Cancellation should be explicit.

```text
Cancel Request
     ↓
Broker
     ↓
Cancellation Confirmation
     ↓
Reconciliation
```

A cancellation request is not proof that an order was cancelled.

---

# 29. Cancel/Replace

If supported:

```text
Original Order
     ↓
Cancel / Replace
     ↓
New Order
```

The relationship between the original and replacement must remain traceable.

---

# 30. Order Expiration

Expired orders should record:

```text
expiration_time
reason
broker_status
internal_status
```

---

# 31. Broker Rejection

A broker may reject an order.

TradeOS should capture:

- Broker error code
- Message
- Timestamp
- Order intent
- Account
- Instrument

A broker rejection should not automatically be retried.

---

# 32. Retry Policy

Retries should be classified.

### Safe Retry

Examples:

- Certain temporary network failures
- Rate-limit responses where permitted

### Unsafe Retry

Examples:

- Unknown submission state
- Possible broker-side acceptance
- Ambiguous timeout

Unsafe retry requires reconciliation first.

---

# 33. Network Failure

If the network fails during submission:

```text
Submission Attempt
       ↓
Network Failure
       ↓
UNKNOWN
       ↓
Query Broker
       ↓
Reconcile
```

Never assume that a network failure means the broker did not receive the order.

---

# 34. Broker Disconnect

On broker disconnect:

```text
Pause New Execution
      ↓
Preserve Existing State
      ↓
Reconnect
      ↓
Fetch Orders
      ↓
Fetch Positions
      ↓
Reconcile
      ↓
Resume Only If Safe
```

---

# 35. Position Reconciliation

TradeOS should periodically compare:

```text
Internal Position
      vs
Broker Position
```

Potential results:

```text
MATCH
MISMATCH
UNKNOWN
```

---

# 36. Position Mismatch

A mismatch should trigger:

```text
Alert
+
Investigation
+
Execution Restriction if necessary
```

TradeOS must not assume the internal state is correct.

---

# 37. Account Reconciliation

Where supported, reconcile:

- Cash
- Buying power
- Margin
- Positions
- Open orders
- Realized P&L

---

# 38. Trade Closure

A trade is considered closed only after:

```text
Exit Fill
      ↓
Position Reconciliation
      ↓
Zero / Expected Remaining Position
      ↓
Trade Closed
```

---

# 39. Orphan Position

If a broker contains a position with no corresponding TradeOS record:

```text
ORPHAN POSITION
```

This is a high-priority reconciliation event.

The system should not automatically create a new strategy trade to explain it.

---

# 40. Orphan Order

If a broker reports an order not known internally:

```text
ORPHAN ORDER
```

This should be investigated before further execution.

---

# 41. Kill Switch Integration

Execution must continuously respect kill-switch state.

```text
Kill Switch
    ↓
Execution Gate
    ↓
Block New Orders
```

The execution layer should not depend on an LLM to decide whether the kill switch is active.

---

# 42. Emergency Cancellation

Depending on policy, emergency procedures may request cancellation of eligible pending orders.

Cancellation itself must be reconciled.

---

# 43. Existing Positions During Halt

A trading halt should distinguish:

```text
New Orders
```

from:

```text
Existing Risk
```

Stopping new orders does not automatically eliminate existing exposure.

Position management policy must be explicit.

---

# 44. Execution Authorization Expiration

Authorization should include a validity window where appropriate.

Example:

```text
Approved at 10:01
Expires at 10:05
```

After expiration:

```text
REQUIRE REVALIDATION
```

Exact timing should be configuration-driven.

---

# 45. Price Protection

Before submitting an order, TradeOS may apply price sanity checks.

Examples:

- Maximum deviation from reference price
- Maximum spread
- Maximum slippage estimate

If exceeded:

```text
BLOCK / REVIEW
```

---

# 46. Market Status

Execution should verify:

```text
Market Open
Instrument Tradable
No Trading Halt
Session Eligible
```

Market status should be sourced from trusted market/broker data.

---

# 47. Quantity Validation

Validate:

- Positive quantity
- Lot size
- Minimum quantity
- Maximum quantity
- Decimal precision
- Contract multiplier

Invalid quantities must be rejected before broker submission.

---

# 48. Price Validation

Validate:

- Tick size
- Decimal precision
- Price range
- Order type requirements

---

# 49. Account Validation

Before execution:

```text
Account Exists
Account Active
Buying Power Sufficient
Margin Acceptable
Trading Permissions Valid
```

---

# 50. Execution Cost Controls

Execution should monitor:

- Fees
- Slippage
- Spread
- Latency
- Market impact

Unexpected costs should become learning data.

---

# 51. Execution Observability

Every execution should generate structured logs/events.

Examples:

```text
ORDER_INTENT_CREATED
ORDER_VALIDATED
ORDER_SUBMITTED
ORDER_ACKNOWLEDGED
ORDER_PARTIALLY_FILLED
ORDER_FILLED
ORDER_CANCEL_REQUESTED
ORDER_CANCELLED
ORDER_REJECTED
ORDER_UNKNOWN
RECONCILIATION_STARTED
RECONCILIATION_COMPLETED
POSITION_MISMATCH
```

---

# 52. Execution Audit

For every order, reconstruct:

```text
Why was it created?
Who/what authorized it?
Which risk decision approved it?
What exact parameters were sent?
Which broker received it?
What did the broker return?
What fills occurred?
What position resulted?
```

---

# 53. Execution Security

Protect:

- Broker credentials
- API keys
- Account identifiers
- Order data
- Sensitive logs

Credentials should never be embedded in source code.

---

# 54. Credential Failure

If credentials expire or fail:

```text
Execution Blocked
      ↓
Alert
      ↓
Credential Recovery
      ↓
Broker Reconciliation
      ↓
Resume Only If Safe
```

---

# 55. Rate Limits

Broker/API rate limits must be respected.

The adapter should implement:

- Rate-limit detection
- Backoff
- Request prioritization
- Safe retry behavior

---

# 56. Broker-Specific Semantics

Different brokers may interpret:

- Order types
- Time in force
- Stops
- Partial fills
- Cancel requests

differently.

The adapter must normalize semantics carefully.

---

# 57. Multi-Broker Architecture

If TradeOS eventually supports multiple brokers:

```text
TradeOS
   ↓
Execution Router
   ↓
Broker Selection
   ↓
Broker Adapter
```

Routing decisions should consider:

- Account
- Instrument
- Liquidity
- Availability
- Cost
- Operational health

Routing must remain within strategy and risk constraints.

---

# 58. Shadow Execution

Before live execution, TradeOS may run:

```text
Decision
 ↓
Execution Simulation
 ↓
Compare
```

This helps validate execution behavior without financial exposure.

---

# 59. Paper Execution

Paper execution should reproduce the same internal lifecycle:

```text
Intent
 ↓
Validation
 ↓
Submission Simulation
 ↓
Fill Simulation
 ↓
Position
 ↓
Reconciliation
```

---

# 60. Execution Simulation

Simulation may model:

- Spread
- Slippage
- Latency
- Partial fills
- Order rejection
- Market movement

Simulation assumptions must be documented.

---

# 61. Execution Learning Loop

```text
Expected Execution
      ↓
Actual Execution
      ↓
Difference
      ↓
Execution Pattern
      ↓
Learning Candidate
      ↓
Validation
```

Examples:

- Persistent slippage
- Slow broker response
- Poor order type
- Excessive market impact

---

# 62. Execution Failure Learning

Repeated execution failures should be classified.

Examples:

```text
NETWORK
BROKER
ORDER_VALIDATION
MARKET_STATE
CREDENTIAL
RATE_LIMIT
RECONCILIATION
```

This allows operational improvement.

---

# 63. Duplicate Prevention Testing

Execution must be tested against:

```text
Double Click
Retry
Timeout
Network Failure
Process Restart
Broker Delay
Duplicate Event
```

Expected result:

```text
At most one logical order
```

subject to broker semantics and explicit order replacement workflows.

---

# 64. Process Restart Recovery

If TradeOS restarts during execution:

```text
Restart
 ↓
Load Pending Intents
 ↓
Query Broker
 ↓
Reconcile
 ↓
Resolve State
 ↓
Resume
```

It must not simply replay every pending action.

---

# 65. Database Failure

If internal database state is unavailable:

```text
Block New Execution
```

until the system can safely establish authoritative state.

---

# 66. Event Ordering

Execution events may arrive out of order.

The system should use:

- Event timestamps
- Broker sequence identifiers where available
- Version numbers
- Idempotent event processing

---

# 67. Duplicate Events

Duplicate broker events should not create:

- Duplicate fills
- Duplicate positions
- Duplicate trades

Event processing should be idempotent.

---

# 68. Exactly-Once vs At-Least-Once

External systems may not guarantee exactly-once delivery.

TradeOS should design around:

```text
At-Least-Once Events
+
Idempotent Processing
+
Reconciliation
```

rather than assuming perfect delivery.

---

# 69. Clock Synchronization

Execution timestamps require reliable clock synchronization.

The system should monitor clock health because timestamp errors can corrupt:

- Order sequencing
- Latency measurements
- Market-data alignment
- Audit records

---

# 70. Execution Limits

Execution should enforce:

- Maximum order quantity
- Maximum order value
- Maximum order frequency
- Maximum slippage
- Maximum open orders
- Maximum strategy exposure

These should complement, not replace, Risk controls.

---

# 71. Execution Rate Limiting

TradeOS should prevent runaway order generation.

Examples:

```text
Maximum Orders / Minute
Maximum Orders / Hour
Maximum Cancel / Replace Rate
```

Exact values should be configured per market/broker.

---

# 72. Runaway Agent Protection

If an agent generates abnormal order proposals:

```text
Pattern Detected
      ↓
Execution Gate
      ↓
Block / Escalate
```

Execution should never trust volume of requests as evidence of correctness.

---

# 73. Execution Approval Chain

For controlled live operation:

```text
Trade Proposal
 ↓
Risk Approval
 ↓
Execution Authorization
 ↓
Order Intent
 ↓
Broker
```

Each transition should be recorded.

Execution Authorization is an enforcement decision over already-granted authority; it cannot grant more authority than the upstream Risk decision and applicable configuration permit.

---

# 74. Execution Architecture Invariants

The following must remain true:

1. Intent is not execution.
2. Order is not fill.
3. Fill is not position until reconciled.
4. Unknown broker state is not failure.
5. Unknown submission must not be blindly retried.
6. Every logical order is idempotent.
7. Partial fills are first-class states.
8. Broker state must be reconciled.
9. Kill switches block new execution.
10. Risk approval is mandatory.
11. Credentials are protected.
12. Execution cannot be authorized by an LLM alone.
13. Process restart must reconcile before replay.
14. Duplicate events must be safely handled.
15. Actual fills determine actual execution outcomes.
16. Execution authorization cannot expand upstream authority.
17. Material state changes invalidate or require revalidation of stale authorization.
18. Execution workflows must not create unbounded agent coordination loops.

---

# 75. Initial Execution Implementation

The first implementation should be:

```text
Trade Proposal
      ↓
Risk Approval
      ↓
Order Intent
      ↓
Paper Broker Adapter
      ↓
Order Lifecycle
      ↓
Simulated Fills
      ↓
Position
      ↓
Reconciliation
```

Then add:

```text
Real Broker Adapter
Idempotency
Live Reconciliation
Advanced Order Types
Multi-Broker Routing
Execution Analytics
```

Live execution should be introduced only after the paper lifecycle is reliable.

---

# 76. Execution Architecture Success Criteria

The Execution System is successful when TradeOS can:

- Create explicit order intents.
- Prevent duplicate submissions.
- Normalize broker state.
- Handle partial fills.
- Reconcile orders and positions.
- Recover safely from restarts.
- Handle ambiguous broker responses.
- Respect kill switches.
- Track actual execution quality.
- Preserve complete execution audit trails.
- Learn from recurring execution failures.
- Keep execution authority bounded by upstream approvals and deterministic controls.
- Revalidate authorization when material state changes occur.

---

# 77. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS execution architecture, including order lifecycle, idempotency, broker adapters, reconciliation, recovery, and execution learning |
| 0.1.1 | Architecture Baseline | Clarified deterministic execution authority, bounded authorization, stale-approval handling, and prevention of authority expansion or unbounded execution orchestration |

---

> **Execution principle: send only what is authorized, know what the broker actually did, reconcile uncertainty before acting again, and never mistake intent for execution.**
