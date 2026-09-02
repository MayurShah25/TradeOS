# TradeOS Documentation Governance

**Version:** 0.2.0  
**Status:** Architecture Baseline — Phase 3 Complete  
**Purpose:** Define the repository documentation hierarchy, authority boundaries, canonical references, and rules for maintaining consistency as TradeOS evolves.

---

## 1. Documentation Is Part of the Architecture

TradeOS documentation is treated as an engineering specification, not merely explanatory material.

Codex and future contributors must use the repository's canonical documentation hierarchy rather than infer architecture from isolated files.

---

## 2. Repository Documentation Structure

The current documentation structure is:

```text
TradeOS/
├── README.md
├── rules.md
└── docs/
    ├── DOCUMENTATION_GOVERNANCE.md
    ├── architecture/
    │   ├── 01–19 subsystem architecture
    │   ├── 22_DOMAIN_MODEL.md
    │   ├── 23_STATE_MACHINES.md
    │   ├── 24_EVENT_CONTRACTS.md
    │   ├── 25_AUTHORITY_AND_PERMISSION_MODEL.md
    │   ├── 26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md
    │   ├── 27_STATE_MACHINE_GOVERNANCE.md
    │   ├── 28_EVENT_CONTRACT_GOVERNANCE.md
    │   ├── 29_PAPER_TRADING_PERSISTENCE_AND_AUDIT.md
    │   ├── 30_PAPER_TRADING_RECOVERY.md
    │   ├── 31_EXECUTION_RECONCILIATION.md
    │   └── 32_DURABLE_EXECUTION_RECONCILIATION.md
    ├── configuration/
    │   └── 21_CONFIGURATION.md
    └── contracts/
        └── 20_AGENT_CONTRACTS.md
```

Implementation/runtime directories are defined by the approved implementation architecture and may evolve while preserving logical boundaries.

---

# 3. Documentation Roles

## `README.md` — Project Navigator

The README explains what TradeOS is, its high-level vision, core principles, current project phase, documentation map, and development approach. It must reflect repository reality without duplicating detailed architecture.

## `rules.md` — Global Invariants

`rules.md` contains global instructions and non-negotiable constraints that apply across the system. Subsystem documents cannot weaken a global rule.

## `docs/architecture/` — Architecture Specifications

Architecture documents describe system boundaries, responsibilities, workflows, domain behavior, and subsystem design.

## `docs/contracts/` — Formal Contracts

Contracts define structured interfaces and behavioral expectations between agents, services, workflows, and system components.

## `docs/configuration/` — Configuration Architecture

Configuration documents define configuration domains, precedence, validation, and operational behavior.

## Canonical Governance / Contract Layer

```text
22 → Domain Objects
23 → State Machines
24 → Event Contracts
25 → Authority & Permissions
26 → Reasoning Efficiency & Agent Orchestration
27 → State Machine Governance
28 → Event Contract Governance
29 → Paper-Trading Persistence & Audit
30 → Safe Paper-Trading Recovery
31 → Execution Reconciliation Semantics
32 → Durable Execution Reconciliation
```

---

# 4. Canonical Ownership

Each architectural concept has one authoritative document or contract owner.

Examples:

```text
TradeProposal → 22_DOMAIN_MODEL.md
Order lifecycle → 23_STATE_MACHINES.md
Event schema → 24_EVENT_CONTRACTS.md
Authorization / permission → 25_AUTHORITY_AND_PERMISSION_MODEL.md
Reasoning orchestration → 26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md
Paper-run persistence → 29_PAPER_TRADING_PERSISTENCE_AND_AUDIT.md
Recovery inspection → 30_PAPER_TRADING_RECOVERY.md
Execution reconciliation → 31_EXECUTION_RECONCILIATION.md
Durable reconciliation → 32_DURABLE_EXECUTION_RECONCILIATION.md
```

A subsystem document may describe how it uses a concept but must not create a competing canonical definition.

---

# 5. Cross-Document Precedence

When documents interact, precedence is determined by concept ownership:

```text
Global invariants
      ↓
Canonical domain / contract definition
      ↓
Governance rules for that domain
      ↓
Subsystem implementation guidance
```

A subsystem document cannot override a canonical contract it does not own. Apparent contradictions must be resolved explicitly.

---

# 6. Single Definition Rule

> **No architecture document may silently redefine a concept owned by another canonical document. It must reference the canonical definition and specify only subsystem-specific behavior.**

For example, `08_RISK_MANAGEMENT.md` may explain how Risk evaluates a `TradeProposal`, but the canonical `TradeProposal` definition belongs to `22_DOMAIN_MODEL.md`.

---

# 7. Repository Paths Must Be Canonical

Documentation references must use actual repository paths. Illustrative future paths must not be presented as implemented structures.

---

# 8. README Must Reflect Reality

The README must not claim that an implementation directory, subsystem, document, or capability exists when it has not been established in the repository.

Status statements must distinguish between:

```text
documented
reviewed
locked
implemented
tested
production-ready
```

These are not interchangeable states.

---

# 9. Documentation Status

Recommended vocabulary:

- `Draft` — proposed and subject to change.
- `Reviewed` — examined for consistency but not necessarily final.
- `Locked` — authoritative for the current phase.
- `Implemented` — corresponding functionality exists in code.
- `Tested` — implementation has passed defined test requirements.
- `Production Ready` — explicitly approved for the applicable operating mode.

A document being present in GitHub does not imply that its architecture is implemented.

---

# 10. Numbering

Existing document numbering is retained. Documents must not be renumbered merely to make the sequence contiguous. Numbering reflects the evolution of the architecture and supporting contract documents.

---

# 11. Codex Reading Order

Before implementing a subsystem, establish context in this order:

```text
rules.md
   ↓
README.md
   ↓
DOCUMENTATION_GOVERNANCE.md
   ↓
Relevant canonical contracts / governance
   ↓
Relevant subsystem architecture
   ↓
Relevant agent contracts
   ↓
Implementation-specific specifications
```

Conflicting requirements must be resolved before implementation.

---

# 12. Documentation Changes

Architecture changes should follow:

```text
Identify conflict / gap
        ↓
Discuss architectural consequence
        ↓
Agree on correction
        ↓
Lock decision
        ↓
Update canonical document
        ↓
Update dependent references
        ↓
Run consistency review
```

Do not silently patch downstream documents while leaving the canonical definition unchanged.

---

# 13. Avoid Documentation Drift

When a canonical concept changes, search for references across:

```text
README.md
rules.md
architecture documents
contracts
configuration
agent definitions
implementation code
tests
```

The objective is one coherent definition of each concept.

---

# 14. Implementation Structure

The repository may use concrete runtime directories once implementation architecture establishes them. Physical structure may evolve without changing logical ownership or safety boundaries.

---

# 15. Change Traceability

Material architectural decisions should be traceable through:

```text
Decision
 ↓
Canonical document
 ↓
Dependent documents
 ↓
Implementation change
 ↓
Tests
```

Commit messages should describe the architectural purpose of material changes.

---

# 16. Consistency Principle

> **The repository must tell one coherent architectural story.**

If a reasonable engineer or coding agent can read two documents and reach two incompatible interpretations of the system, the documentation is not ready for implementation.

---

# 17. Current Locked Architecture Layer

The following documents are canonical and locked within their respective domains:

```text
22  Domain Model                                  LOCKED
23  State Machines                                LOCKED
24  Event Contracts                               LOCKED
25  Authority & Permission Model                  LOCKED
26  Reasoning Efficiency & Agent Orchestration    LOCKED
27  State Machine Governance                      LOCKED
28  Event Contract Governance                     LOCKED
29  Paper-Trading Persistence & Audit             IMPLEMENTED / TESTED
30  Safe Paper-Trading Recovery                   IMPLEMENTED / TESTED
31  Execution Reconciliation Semantics            IMPLEMENTED / TESTED
32  Durable Execution Reconciliation              IMPLEMENTED / TESTED
```

These documents must be treated as authoritative until a later governed architectural change supersedes them.

---

# 18. Phase 3 Closure

Phase 3 is complete for its approved paper-trading scope:

- deterministic market-data and paper-execution boundaries
- portfolio/risk context and hard pre-trade risk controls
- execution authorization and single-use execution gateway
- execution outcome reconciliation semantics
- governed paper-trading session
- immutable paper-run state and append-only audit
- durable SQLite paper-run/audit persistence
- safe recovery inspection
- explicit `RECONCILIATION_REQUIRED` handling for ambiguous outcomes
- durable reconciliation for verified outcomes

Live broker connectivity, live financial exposure, automatic retry/resubmission of ambiguous orders, and controlled-live promotion remain out of scope.

---

# 19. Core Rule

> **One concept, one canonical owner, one repository path, one authoritative definition. Subsystems may specialize behavior, but they must not create competing truths.**
