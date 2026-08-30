# TradeOS State Machine Governance

**Document:** `27_STATE_MACHINE_GOVERNANCE.md`  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Canonical state-machine governance rules established during the 01–25 consistency review

---

## 1. Purpose

TradeOS treats state as operational control, not descriptive metadata. A state determines which actions are legal, which transitions are possible, and which safeguards must apply.

`23_STATE_MACHINES.md` is the canonical source of truth for lifecycle states and legal transitions.

This document records the governance rules that must be enforced by implementation.

---

# 2. Core Rules

### Rule 1 — Canonical State Source

`23_STATE_MACHINES.md` defines canonical lifecycle states and legal transitions. Other architecture documents may explain behavior but must not create competing state vocabularies.

### Rule 2 — Explicit Transition Authority

Every material transition has an authoritative subsystem. Agents may request or recommend transitions but cannot arbitrarily mutate safety-critical state.

### Rule 3 — Deterministic Validation

Every material transition must pass deterministic validation of:

```text
current state
requested transition
authority
preconditions
required evidence
operating mode
configuration
```

### Rule 4 — Evidence Before Fact

A transition is valid only when its required evidence exists.

Examples:

```text
ORDER → FILLED
requires execution/fill evidence

POSITION → CLOSED
requires applicable closure/reconciliation evidence

STRATEGY → PRODUCTION
requires governed approval
```

### Rule 5 — UNKNOWN Is First-Class

`UNKNOWN` is not equivalent to `FAILED`.

An unknown external state requires reconciliation before a consequential assumption or duplicate financial action is made.

### Rule 6 — Material Transitions Emit Events

Material state transitions produce canonical versioned events defined by `24_EVENT_CONTRACTS.md`.

### Rule 7 — History Is Preserved

Material state transitions must remain auditable. Corrections create explicit corrective history rather than silently rewriting prior state.

---

# 3. Canonical State Transition Pipeline

```text
Current State
      ↓
Requested Transition
      ↓
State Machine
      ↓
Authority Check
      ↓
Precondition Check
      ↓
Evidence Check
      ↓
State Change
      ↓
Canonical Event
      ↓
Downstream Workflow
```

Invalid transitions terminate at validation and must not mutate state.

---

# 4. Critical UNKNOWN Rule

For external execution state:

```text
Submission
   ↓
Timeout / Ambiguous Response
   ↓
UNKNOWN
   ↓
Reconciliation
   ↓
Resolved State
```

The system must not infer:

```text
UNKNOWN → FAILED → RESUBMIT
```

without authoritative evidence and policy permitting that transition.

This rule exists to prevent duplicate orders and unintended exposure.

---

# 5. Critical Execution State Chain

```text
Trade Proposal
      ↓
Risk Decision
      ↓
Execution Authorization
      ↓
Order Intent
      ↓
Order
      ↓
Fill
      ↓
Position
      ↓
Trade
```

Each stage has its own state and evidence requirements. A later state cannot be manufactured merely because an earlier intention existed.

---

# 6. Immutable Decision Records

The following are treated as immutable historical decisions or evidence records after issuance/creation, subject to explicit corrective records:

```text
Risk Decision
Execution Authorization
Order Intent
Order Submission Record
Fill
State Transition Record
Configuration Version
Learning Observation
```

Operational current-state projections may change, but their history remains auditable.

---

# 7. Authorization Reuse

Live execution authorization is single-use by default.

A reusable authorization requires an explicit policy that defines:

```text
scope
maximum uses
validity window
permitted changes
consumption semantics
```

An authorization must never be unintentionally reusable merely because the record remains present.

---

# 8. Agent Boundary

AI agents must not perform arbitrary assignments such as:

```text
order.status = FILLED
position.status = CLOSED
strategy.status = PRODUCTION
```

Instead, agents may submit structured requests to the appropriate deterministic subsystem, which validates and applies the transition.

---

# 9. Concurrency

State transitions must be protected against races.

For example, two workers must not both consume the same single-use authorization.

Implementation may use transactions, optimistic locking, unique constraints, or equivalent mechanisms.

---

# 10. Recovery

Recovery follows:

```text
Failure / Unknown
      ↓
Assess Current State
      ↓
Reconcile if Required
      ↓
Revalidate Safety
      ↓
Resume / Block / Escalate
```

Process restart alone is never considered domain-state recovery.

---

# 11. Testing Requirements

State-machine tests must cover:

- Every legal transition
- Every illegal transition
- Terminal-state protection
- UNKNOWN behavior
- Required evidence
- Authorization expiry
- Authorization reuse
- Concurrent transitions
- Retry behavior
- Recovery behavior
- Kill-switch behavior
- Permission enforcement
- Event emission

---

## 12. Related Documents

- `22_DOMAIN_MODEL.md`
- `23_STATE_MACHINES.md`
- `24_EVENT_CONTRACTS.md`
- `25_AUTHORITY_AND_PERMISSION_MODEL.md`
- `26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md`
- `12_EXECUTION_ARCHITECTURE.md`
- `08_RISK_MANAGEMENT.md`

---

**TradeOS State Principle**

> **A state change is a governed fact: it requires legal authority, valid evidence, and an auditable transition.**
