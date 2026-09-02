# TradeOS

**Version:** 0.2.3  
**Status:** Phase 3 Paper Trading Foundation Implemented — Durable Reconciliation Implemented  
**Project Type:** Personal AI-Assisted Multi-Market Trading Operating System

## Overview

TradeOS is a modular, AI-assisted trading operating system designed for personal use. It combines market research, strategy analysis, prediction, risk management, portfolio analysis, execution, backtesting, paper trading, and continuous learning into one disciplined and explainable system.

> **The system should improve trading discipline and decision quality without allowing intelligence to override risk controls.**

TradeOS is not intended to predict markets with certainty. It is intended to make better-structured decisions under uncertainty while preserving capital, enforcing deterministic safety boundaries, maintaining auditability, and learning from outcomes.

## Core Principles

- **Capital preservation first.** No strategy, prediction, agent, or opportunity may override hard risk controls.
- **Intelligence does not equal authority.** Agents provide analysis and recommendations; deterministic governance and safety boundaries control what the system may do.
- **Deterministic work stays deterministic.** Calculations, validation, state management, reconciliation, and enforcement belong in deterministic services/engines where appropriate.
- **Evidence before belief.** Strategies must earn promotion through testing and evidence.
- **Explainability.** Decisions must preserve the evidence, reasoning outputs, risk decisions, and outcomes needed for audit and review.
- **Modularity.** Markets, strategies, models, agents, brokers, and data providers should be replaceable through defined boundaries.
- **Reasoning efficiency.** Use bounded workflows, structured inputs, selective model calls, summaries, and caching where justified.
- **Safety before automation.** Progression is **Research → Backtest → Walk-Forward Validation → Paper Trading → Controlled Live Trading**.
- **No trade is a valid outcome.** A rejected opportunity is a successful governance outcome when constraints are not satisfied.

The global constitutional rules are defined by `rules.md`; detailed documents refine implementation without weakening those rules.

## Documentation Baseline

The documentation baseline currently consists of:

- `rules.md` — global constitutional rules.
- `docs/DOCUMENTATION_GOVERNANCE.md` — documentation hierarchy, ownership, lifecycle, review, and change-control rules.
- `docs/architecture/01_PROJECT_VISION.md` through `19_TESTING_ARCHITECTURE.md` — core architecture documentation.
- `docs/contracts/20_AGENT_CONTRACTS.md` — agent boundaries and contracts.
- `docs/configuration/21_CONFIGURATION.md` — configuration architecture and policy.
- `docs/architecture/22_DOMAIN_MODEL.md` through `32_DURABLE_EXECUTION_RECONCILIATION.md` — domain, state, event, authority, reasoning, governance, persistence, recovery, reconciliation, and durable reconciliation architecture.

**All numbered documents 01–32 are accounted for in the repository. No numbered documentation gap is currently known.**

The documentation set is treated as the baseline for implementation. Future documentation changes must follow the governance process and must not silently contradict canonical rules or contracts.

## Documentation Map

| Range / File | Location | Purpose |
|---|---|---|
| Global rules | `rules.md` | Constitutional rules and non-negotiable boundaries |
| Governance | `docs/DOCUMENTATION_GOVERNANCE.md` | Documentation hierarchy and change control |
| 01–19 | `docs/architecture/` | Core architecture through testing |
| 20 | `docs/contracts/` | Agent boundaries and contracts |
| 21 | `docs/configuration/` | Configuration |
| 22 | `docs/architecture/` | Domain model |
| 23 | `docs/architecture/` | State machines |
| 24 | `docs/architecture/` | Event contracts |
| 25 | `docs/architecture/` | Authority and permission model |
| 26 | `docs/architecture/` | Reasoning efficiency and agent orchestration |
| 27 | `docs/architecture/` | State-machine governance |
| 28 | `docs/architecture/` | Event-contract governance |
| 29 | `docs/architecture/` | Paper-trading persistence and audit repository |
| 30 | `docs/architecture/` | Safe paper-trading recovery |
| 31 | `docs/architecture/` | Execution reconciliation semantics |
| 32 | `docs/architecture/` | Durable execution reconciliation |

## Implementation Roadmap

### Phase 1 — Documentation Baseline
Completed as the prerequisite baseline represented by the repository documentation set.

### Phase 2 — Foundation
The core configuration, domain, portfolio, execution, testing, and infrastructure foundation is implemented incrementally behind explicit contracts and safety boundaries.

### Phase 3 — Paper Trading Foundation
**COMPLETED.** Durable paper-run persistence, append-only audit history, persistent session integration, restart coverage, failure persistence, safe interrupted-run recovery inspection, explicit reconciliation-required state, and durable reconciliation are implemented. Real broker/live execution remains out of scope.

### Phase 4 — Strategy & Backtesting
**NEXT.** Implement strategy interfaces, historical simulation, metrics, robustness checks, and walk-forward validation.

### Phase 5 — Multi-Agent Intelligence
Implement the orchestrator and specialized bounded agents according to the contracts.

### Phase 6 — Paper Trading Operations
Introduce broader real-time data workflows, simulated execution operations, reconciliation workflows, and operational monitoring.

### Phase 7 — Dashboard & Learning
Add monitoring, journal, coaching, learning reports, and analytics.

### Phase 8 — Controlled Live Trading
Only after explicit validation gates, risk controls, reconciliation, testing, and governance requirements are satisfied.

## Execution Integrity

TradeOS explicitly distinguishes:

```text
Trade Proposal
    ≠
Order Intent
    ≠
Broker Order
    ≠
Fill
    ≠
Position
```

An intended order is not proof of execution. Ambiguous broker state must remain `UNKNOWN` until reconciled; the system must not blindly resubmit an order when broker-side state is uncertain.

## Risk Governance

Risk controls include configurable boundaries for risk per trade, daily loss, portfolio exposure, correlated exposure, drawdown, position limits, leverage, liquidity, strategy-specific limits, and market-specific constraints.

The documentation baseline preserves the principle that a hard risk rejection cannot be overturned downstream and that stops must never be widened simply to avoid realizing a loss.

## Research, Validation & Learning

New strategies follow a governed progression:

```text
Research Idea
     ↓
Research Sandbox
     ↓
Strategy Specification
     ↓
Historical Backtest
     ↓
Robustness Testing
     ↓
Walk-Forward Validation
     ↓
Paper Trading
     ↓
Review
     ↓
Controlled Promotion
```

Backtesting must account for relevant transaction costs, slippage, liquidity, spreads, partial fills, market hours, corporate actions, data quality, and execution latency. Historical evaluation must avoid look-ahead bias and data leakage.

Learning follows a governed path from observation and logging through repeated evidence, validation, recommendation, approval, activation, and measurement. Learning may recommend improvements but must not silently modify immutable safety controls or deploy unvalidated behavior.

## Security

Secrets must never be committed to GitHub. Broker credentials, API keys, cloud credentials, database passwords, and LLM-provider credentials must use environment variables or appropriate secrets management.

The system is **not ready for live trading** merely because the documentation phase is complete.

## Current Readiness

### Documentation
**READY / BASELINE LOCKED**

The repository currently contains the complete numbered documentation sequence **01–32**, plus the global rules and documentation-governance documents. No numbered documentation gap is currently known.

### Coding
**PHASE 3 COMPLETE — READY FOR PHASE 4**

The durable paper-trading repository, session integration, recovery inspection, explicit reconciliation-required lifecycle, and durable reconciliation boundary are implemented and covered by CI. The next implementation increment is the strategy and backtesting foundation.

### Live Trading
**NOT READY**

Live trading remains gated behind implementation, testing, validation, paper trading, reconciliation, and explicit controlled-live authorization.

## Change & Documentation Governance

The repository follows this documentation process:

```text
Discuss
  ↓
Agree
  ↓
Lock
  ↓
Update Canonical Document
  ↓
Update Dependencies
  ↓
Cross-Document Review
```

One concept should have one canonical owner and one authoritative definition. Documentation changes must preserve the hierarchy and must not silently weaken global rules or contracts.

## Disclaimer

TradeOS is a personal research, education, and trading-system development project. Financial markets involve substantial risk, including possible loss of capital. Historical backtests do not guarantee future results. Live trading should be introduced only after appropriate testing, validation, risk controls, reconciliation, and appropriate human review.

---

> **Research deeply. Decide systematically. Risk conservatively. Execute precisely. Learn continuously.**
