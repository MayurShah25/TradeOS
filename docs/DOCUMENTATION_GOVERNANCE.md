# TradeOS Documentation Governance

**Version:** 0.1.0  
**Status:** Architecture Baseline  
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
    │   └── 28_EVENT_CONTRACT_GOVERNANCE.md
    ├── configuration/
    │   └── 21_CONFIGURATION.md
    └── contracts/
        └── 20_AGENT_CONTRACTS.md
```

Implementation/runtime directories are intentionally not prescribed by this document. They will be defined by the implementation architecture before coding begins.

---

# 3. Documentation Roles

## `README.md` — Project Navigator

The README explains:

- What TradeOS is
- Its high-level vision
- Core principles
- Current project phase
- Documentation map
- High-level development approach

It must not become a duplicate of the detailed architecture.

## `rules.md` — Global Invariants

`rules.md` contains global instructions and non-negotiable constraints that apply across the system.

Subsystem documents cannot weaken a global rule.

## `docs/architecture/` — Architecture Specifications

Architecture documents describe system boundaries, responsibilities, workflows, domain behavior, and subsystem design.

## `docs/contracts/` — Formal Contracts

Contracts define structured interfaces and behavioral expectations between agents, services, workflows, and other system components.

## `docs/configuration/` — Configuration Architecture

Configuration documents define configuration domains, precedence, validation, and operational behavior.

## `22–28` — Canonical Governance / Contract Layer

These documents establish canonical definitions and governance for their specific domains:

```text
22 → Domain Objects
23 → State Machines
24 → Event Contracts
25 → Authority & Permissions
26 → Reasoning Efficiency & Agent Orchestration
27 → State Machine Governance
28 → Event Contract Governance
```

---

# 4. Canonical Ownership

Each architectural concept has one authoritative document or contract owner.

Examples:

```text
TradeProposal
→ 22_DOMAIN_MODEL.md

Order lifecycle
→ 23_STATE_MACHINES.md

Event schema
→ 24_EVENT_CONTRACTS.md

Authorization / permission
→ 25_AUTHORITY_AND_PERMISSION_MODEL.md

Reasoning orchestration
→ 26_REASONING_EFFICIENCY_AND_AGENT_ORCHESTRATION.md
```

A subsystem document may describe how it uses a concept but must not create a competing canonical definition.

---

# 5. Cross-Document Precedence

When documents interact, precedence is determined by concept ownership.

```text
Global invariants
      ↓
Canonical domain / contract definition
      ↓
Governance rules for that domain
      ↓
Subsystem implementation guidance
```

A subsystem document cannot override a canonical contract it does not own.

If two documents appear contradictory, the contradiction must be resolved explicitly; contributors must not choose an interpretation silently.

---

# 6. Single Definition Rule

> **No architecture document may silently redefine a concept owned by another canonical document. It must reference the canonical definition and specify only subsystem-specific behavior.**

For example:

`08_RISK_MANAGEMENT.md` may explain how Risk evaluates a `TradeProposal`, but the canonical `TradeProposal` definition belongs to `22_DOMAIN_MODEL.md`.

`12_EXECUTION_ARCHITECTURE.md` may explain how Execution consumes an `ExecutionAuthorization`, but its canonical definition belongs to the appropriate domain/authority contract.

---

# 7. Repository Paths Must Be Canonical

Documentation references must use the actual repository path.

Do not reference hypothetical paths such as:

```text
agents/
core/
execution/
```

as though those implementation directories already exist.

Future implementation paths may be introduced only when the implementation architecture defines them.

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

Architecture status should be explicit.

Recommended vocabulary:

- `Draft` — proposed and subject to change.
- `Reviewed` — examined for consistency but not necessarily final.
- `Locked` — architectural decision agreed and authoritative for the current phase.
- `Implemented` — corresponding functionality exists in code.
- `Tested` — implementation has passed the defined test requirements.
- `Production Ready` — explicitly approved for the applicable operating mode.

A document being present in GitHub does not imply that its architecture is implemented.

---

# 10. Numbering

Existing document numbering is retained.

Documents must not be renumbered merely to make the sequence contiguous.

The current sequence intentionally reflects the evolution of the architecture and supporting contract documents.

---

# 11. Codex Reading Order

Before implementing a subsystem, Codex should establish context in this order:

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

Codex must resolve conflicting requirements before generating implementation code.

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

When a canonical concept changes, search for references to it across the repository.

Check at minimum:

```text
README.md
rules.md
architecture documents
contracts
configuration
agent definitions
implementation code once coding begins
tests once coding begins
```

The objective is to prevent two documents from describing different versions of the same concept.

---

# 14. No Premature Runtime Structure

Documentation must not force implementation structure prematurely.

Until runtime architecture is explicitly approved, repository descriptions should not assume a final:

```text
src/
services/
agents/
execution/
markets/
```

layout.

This prevents Codex from treating an illustrative structure as an architectural requirement.

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

Commit messages should describe the architectural purpose of material documentation changes.

---

# 16. Consistency Principle

> **The repository must tell one coherent architectural story.**

If a reasonable engineer or coding agent can read two documents and reach two incompatible interpretations of the system, the documentation is not ready for implementation.

---

# 17. Current Locked Architecture Layer

As of this baseline:

```text
22  Domain Model                                  LOCKED
23  State Machines                                LOCKED
24  Event Contracts                               LOCKED
25  Authority & Permission Model                  LOCKED
26  Reasoning Efficiency & Agent Orchestration    LOCKED
27  State Machine Governance                      LOCKED
28  Event Contract Governance                     LOCKED
```

These documents must be treated as authoritative within their respective domains until a later governed architectural change supersedes them.

---

# 18. Core Rule

> **One concept, one canonical owner, one repository path, one authoritative definition. Subsystems may specialize behavior, but they must not create competing truths.**
