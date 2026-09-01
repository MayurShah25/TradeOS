# TradeOS State Machines

**Document:** `23_STATE_MACHINES.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Canonical lifecycle states, legal transitions, transition authority, terminal states, recovery, and invariants

---

## 1. Purpose

This document defines the canonical state machines used by TradeOS.

State is not descriptive metadata. For safety-critical entities, state controls what actions are permitted next.

The governing principle is:

> **A component may only perform an action permitted by the current state and transition contract.**

Invalid state transitions must be rejected deterministically.

---

# 2. State-Machine Principles

1. States are explicit.
2. Transitions are explicit.
3. Every transition has an authoritative actor/service.
4. Invalid transitions are rejected.
5. Terminal states cannot silently become active states.
6. Recovery from failure requires explicit reconciliation or revalidation where applicable.
7. UNKNOWN is not equivalent to FAILED.
8. State changes generate versioned events.
9. State history is auditable.
10. LLM output cannot directly mutate safety-critical state.

---

# 3. State Transition Model

Every transition should conceptually contain:

```text
entity_id
entity_type
from_state
to_state
transition_type
actor
reason
workflow_id
occurred_at
configuration_version
```

The transition engine validates preconditions before applying the transition.

---

# 4. System Operating Mode

```text
DEVELOPMENT
TESTING
RESEARCH
PAPER
ASSISTED_LIVE
CONTROLLED_AUTONOMOUS
EMERGENCY
DISABLED
```

### Key Rules

- `DEVELOPMENT`, `TESTING`, and `RESEARCH` cannot submit live broker orders.
- `PAPER` cannot create real financial exposure.
- `ASSISTED_LIVE` requires configured human approval.
- `CONTROLLED_AUTONOMOUS` requires explicit production authorization.
- `EMERGENCY` blocks new trading.
- `DISABLED` blocks execution entirely.

---

# 5. Workflow State Machine

```text
CREATED
   ↓
RUNNING
   ├──→ WAITING
   │      ↓
   │   RUNNING
   │
   ├──→ COMPLETED
   ├──→ REJECTED
   ├──→ CANCELLED
   └──→ FAILED
```

### Transition Rules

| From | To | Authority | Condition |
|---|---|---|---|
| CREATED | RUNNING | Workflow Service | Valid workflow |
| RUNNING | WAITING | Workflow Service | Waiting on dependency |
| WAITING | RUNNING | Workflow Service | Dependency resolved |
| RUNNING | COMPLETED | Workflow Service | Success criteria met |
| RUNNING | REJECTED | Governing subsystem | Explicit rejection |
| RUNNING | CANCELLED | Authorized control | Cancellation permitted |
| RUNNING | FAILED | Workflow Service | Unrecoverable failure |

A failed workflow may not be silently resumed as though nothing happened.

---

# 6. Trade Proposal State Machine

```text
CREATED
   ↓
ANALYZING
   ↓
READY_FOR_REVIEW
   ├──→ REJECTED
   └──→ APPROVED_FOR_AUTHORIZATION
               ↓
            EXPIRED
```

Possible cancellation from non-terminal pre-execution states:

```text
CREATED / ANALYZING / READY_FOR_REVIEW
                ↓
             CANCELLED
```

### Rules

- A Strategy component may create or update a proposal only while it is mutable.
- Once submitted for governance review, critical trading fields become immutable for that review attempt.
- A rejected proposal cannot become approved without a new review attempt/version.
- An expired proposal requires revalidation.

---

# 7. Risk Decision State

Risk decisions are immutable records rather than mutable workflow state.

Canonical decision values:

```text
APPROVED
REJECTED
REQUIRES_REVIEW
EXPIRED
```

### Rules

- `REJECTED` due to a hard deterministic constraint cannot be converted to `APPROVED` by an agent.
- `REQUIRES_REVIEW` must return to the governance workflow.
- `APPROVED` is valid only within its configured validity window.
- A changed material input requires a new Risk Decision.

---

# 8. Execution Authorization State Machine

```text
ISSUED
  ↓
VALID
  ├──→ CONSUMED
  ├──→ EXPIRED
  └──→ REVOKED
```

### Rules

- Authorization is immutable.
- `CONSUMED` means the authorized execution intent was created/consumed according to policy.
- `EXPIRED` cannot be used for submission.
- `REVOKED` cannot be used for submission.
- A material change to price, quantity, stop, account, instrument, risk, or operating mode invalidates the authorization unless explicitly permitted by the contract.

---

# 9. Order Intent State Machine

```text
CREATED
   ↓
VALIDATING
   ↓
AUTHORIZED
   ↓
SUBMITTING
   ├──→ SUBMITTED
   ├──→ FAILED
   └──→ UNKNOWN
```

An Order Intent is immutable once submission begins.

---

# 10. Order State Machine

Canonical path:

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
```

`UNKNOWN` is a non-terminal reconciliation state.

### Critical Rule

```text
UNKNOWN
   ↓
RECONCILIATION
   ↓
RESOLVED STATE
```

Never infer failure merely from timeout or missing response.

---

# 11. Position State Machine

```text
NONE
 ↓
OPENING
 ↓
OPEN
 ↓
REDUCING
 ↓
CLOSING
 ↓
CLOSED
```

Exceptional states:

```text
RECONCILIATION_REQUIRED
UNKNOWN
```

### Rules

- Position state must reflect actual fills, not intended orders.
- A position cannot be marked `CLOSED` until required reconciliation confirms closure.
- An unexpected broker position creates a reconciliation event.

---

# 12. Trade Lifecycle State Machine

```text
PROPOSED
   ↓
AUTHORIZED
   ↓
OPENING
   ↓
OPEN
   ↓
MANAGING
   ↓
CLOSING
   ↓
CLOSED
```

Exceptional states:

```text
CANCELLED
INVALIDATED
RECONCILIATION_REQUIRED
UNKNOWN
```

A Trade is an economic lifecycle, not merely an order lifecycle.

---

# 13. Strategy Lifecycle

```text
DRAFT
 ↓
RESEARCH
 ↓
BACKTEST
 ↓
ROBUSTNESS_VALIDATION
 ↓
OOS_VALIDATION
 ↓
PAPER
 ↓
APPROVED
 ↓
PRODUCTION
```

Possible states:

```text
PAUSED
RETIRED
REJECTED
```

### Promotion Rule

Promotion requires documented evidence and the required governance approval. No AI agent may independently promote a strategy into production.

---

# 14. Model Lifecycle

```text
RESEARCH
 ↓
VALIDATION
 ↓
SHADOW
 ↓
PAPER
 ↓
PRODUCTION
```

Possible states:

```text
DEGRADED
DISABLED
RETIRED
```

A degraded model must not silently remain trusted for workflows requiring production-quality predictions.

---

# 15. Agent Lifecycle

```text
REGISTERED
 ↓
INITIALIZED
 ↓
READY
 ↓
RUNNING
 ↓
COMPLETED
```

Failure states:

```text
TIMEOUT
FAILED
CANCELLED
DEGRADED
DISABLED
```

An unhealthy agent must not silently produce trusted output.

---

# 16. Agent Request Lifecycle

```text
CREATED
 ↓
DISPATCHED
 ↓
RUNNING
 ├──→ SUCCESS
 ├──→ PARTIAL
 ├──→ ABSTAIN
 ├──→ INSUFFICIENT_DATA
 ├──→ REQUIRES_REVIEW
 ├──→ FAILED
 ├──→ TIMEOUT
 └──→ REJECTED
```

Responses are immutable records.

---

# 17. Risk State Machine

Account/portfolio risk state may follow:

```text
NORMAL
  ↓
CAUTION
  ↓
REDUCED_RISK
  ↓
HALT_NEW_TRADES
  ↓
EMERGENCY
```

Transitions may occur in either direction only through explicit risk policy.

A restart does not automatically return the system to `NORMAL`.

---

# 18. Kill-Switch State

```text
ARMED
 ↓
TRIGGERED
 ↓
LOCKED
 ↓
RECOVERY_REVIEW
 ↓
ARMED
```

Different scopes may exist:

```text
ORDER
INSTRUMENT
STRATEGY
ACCOUNT
MARKET
PLATFORM
```

A triggered kill switch must block the actions covered by its scope.

---

# 19. Reconciliation State

```text
NOT_REQUIRED
 ↓
REQUIRED
 ↓
IN_PROGRESS
 ↓
MATCHED
```

Alternative result:

```text
MISMATCH
```

Mismatches require investigation and may trigger execution restrictions.

---

# 20. Configuration Lifecycle

```text
DRAFT
 ↓
VALIDATED
 ↓
REVIEWED
 ↓
APPROVED
 ↓
ACTIVE
 ↓
DEPRECATED
 ↓
RETIRED
```

An active configuration version is immutable.

Rollback activates a previous valid version rather than editing history.

---

# 21. Learning Pattern Lifecycle

```text
OBSERVED
 ↓
PATTERN_CANDIDATE
 ↓
SUPPORTED
 ↓
VALIDATED
 ↓
RECOMMENDATION
 ↓
APPROVED
 ↓
ACTIVE_RULE
 ↓
REVALIDATION
```

A pattern can also become:

```text
REJECTED
EXPIRED
RETIRED
```

One observation cannot directly become an active rule.

---

# 22. Research Experiment Lifecycle

```text
IDEA
 ↓
HYPOTHESIS
 ↓
DESIGNED
 ↓
RUNNING
 ↓
COMPLETED
 ↓
EVALUATED
```

Possible outcomes:

```text
SUPPORTED
REJECTED
INCONCLUSIVE
```

Research artifacts cannot directly alter production behavior.

---

# 23. State Transition Authority

| State Domain | Authoritative Component |
|---|---|
| Workflow | Workflow Service |
| Trade Proposal | Strategy/Workflow subsystem |
| Risk Decision | Risk subsystem |
| Authorization | Risk/Execution boundary |
| Order Intent | Execution subsystem |
| Order | Execution/Broker Adapter |
| Fill | Broker/Execution subsystem |
| Position | Reconciliation subsystem |
| Trade | Trade subsystem |
| Strategy | Strategy Governance |
| Model | Model Governance |
| Agent | Agent Runtime |
| Risk State | Risk Engine |
| Kill Switch | Safety/Risk subsystem |
| Configuration | Configuration subsystem |
| Learning Rule | Governance |

Agents may recommend transitions but must not mutate state outside their authority.

---

# 24. Illegal Transition Examples

The following must be rejected:

```text
Risk REJECTED → Execution
Expired Authorization → Order Submission
Order UNKNOWN → Automatic Resubmission
Position CLOSED → Broker-Confirmed OPEN without new evidence
Strategy RESEARCH → PRODUCTION without validation
Learning Recommendation → ACTIVE_RULE without approval
EMERGENCY → NORMAL after service restart
```

---

# 25. State and Events

Every material state transition should produce a versioned event.

Example:

```text
risk.approved
order.submitted
order.filled
position.reconciliation_required
strategy.promoted
configuration.activated
learning.rule.approved
```

Event contracts are defined in `24_EVENT_CONTRACTS.md`.

---

# 26. State History

State history should be append-only for material operational records.

At minimum preserve:

```text
entity_id
previous_state
new_state
actor
reason
timestamp
workflow_id
correlation_id
configuration_version
```

---

# 27. Recovery Rule

Failure recovery must follow:

```text
FAILURE
 ↓
ASSESS STATE
 ↓
RECONCILE IF NECESSARY
 ↓
REVALIDATE SAFETY
 ↓
RESUME / BLOCK
```

Never use process restart as a substitute for domain-state recovery.

---

# 28. State-Machine Testing

Tests must cover:

- Every legal transition
- Every illegal transition
- Terminal-state protection
- Timeout behavior
- UNKNOWN behavior
- Recovery behavior
- Kill-switch behavior
- Permission enforcement
- Concurrent transition conflicts
- Replay/idempotency

---

# 29. Concurrency

State transitions must be protected against race conditions.

For example:

```text
Risk Approved
      ↓
Two execution workers receive same authorization
      ↓
Only one may consume the authorization
```

Use deterministic concurrency controls such as unique constraints, optimistic locking, or transactional state transitions.

---

# 30. Implementation Rule

State machines should be represented in executable code and covered by automated tests.

The documentation is the contract; the implementation must enforce the contract rather than merely document it.

---

## 31. Related Documents

- `22_DOMAIN_MODEL.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`
- `12_EXECUTION_ARCHITECTURE.md`
- `08_RISK_MANAGEMENT.md`
- `20_AGENT_CONTRACTS.md`

---

**TradeOS State Principle**

> **If the system does not know its state, it must stop assuming and start reconciling.**
