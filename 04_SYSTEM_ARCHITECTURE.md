# TradeOS System Architecture

**Document:** 04_SYSTEM_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Logical architecture, system boundaries, data flow, runtime components, and major integration points

---

## 1. Purpose

This document defines the logical architecture of TradeOS.

It translates the Project Vision, Global Rules, Design Principles, and Engineering Principles into a concrete system structure.

The architecture is designed around five priorities:

1. Safety
2. Deterministic risk control
3. Modular intelligence
4. Explainability and auditability
5. Continuous learning without uncontrolled self-modification

This document describes **what components exist, how they interact, and where responsibilities belong**.

Detailed implementation contracts will be defined in subsequent documents.

---

# 2. Architectural Model

TradeOS is a layered, modular, event-driven system.

At a high level:

```text
                         ┌───────────────────┐
                         │       USER        │
                         │ Dashboard / CLI   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   ORCHESTRATOR    │
                         │ Workflow Manager  │
                         └─────────┬─────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │  MARKET &   │       │ INTELLIGENCE│       │  RESEARCH   │
      │    DATA     │       │    LAYER    │       │    LAYER    │
      └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                         ┌───────────────────┐
                         │  DECISION LAYER   │
                         │ Critic / Portfolio│
                         └─────────┬─────────┘
                                   ▼
                         ┌───────────────────┐
                         │    RISK GATE      │
                         │ Deterministic +   │
                         │ Risk Agent        │
                         └─────────┬─────────┘
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                      REJECT              APPROVE
                                             │
                                             ▼
                                  ┌───────────────────┐
                                  │ EXECUTION LAYER   │
                                  │ OMS / Broker      │
                                  └─────────┬─────────┘
                                            ▼
                                         MARKET
                                            │
                                            ▼
                                  ┌───────────────────┐
                                  │ JOURNAL / AUDIT   │
                                  └─────────┬─────────┘
                                            ▼
                                  ┌───────────────────┐
                                  │ LEARNING SYSTEM   │
                                  │ Mistakes / Models │
                                  └─────────┬─────────┘
                                            │
                                  Validated Learning
                                            │
                                            ▼
                                  Future Decisions
```

---

# 3. Architectural Layers

TradeOS is divided into the following logical layers.

## Layer 1 — User Experience

Responsible for:

- Dashboard
- Trade proposals
- Approvals
- Rejections
- Alerts
- Reports
- Learning feedback
- System status

The UI must not bypass core safety controls.

---

## Layer 2 — Orchestration

Responsible for:

- Workflow coordination
- Agent invocation
- State transitions
- Event handling
- Workflow termination
- Context selection

The Orchestrator coordinates.

It does not own risk authority.

---

## Layer 3 — Market & Data

Responsible for:

- Market data ingestion
- Historical data
- Real-time data
- Data normalization
- Data validation
- Instrument metadata
- Market profiles

---

## Layer 4 — Intelligence

Responsible for:

- Technical analysis
- Fundamental analysis
- News and sentiment
- Market regime analysis
- Strategy evaluation
- Prediction
- Research

---

## Layer 5 — Decision Governance

Responsible for:

- Critic review
- Portfolio analysis
- Risk evaluation
- Position sizing
- Trade authorization

This is where intelligence becomes a governed decision.

---

## Layer 6 — Execution

Responsible for:

- Order creation
- Order validation
- Order submission
- Fill verification
- Position reconciliation
- Trade management

---

## Layer 7 — Journal & Audit

Responsible for:

- Decision records
- Orders
- Positions
- Outcomes
- Agent outputs
- Strategy versions
- Model versions
- Configuration references

---

## Layer 8 — Learning

Responsible for:

- Outcome analysis
- Mistake detection
- Repeated-pattern detection
- Strategy learning
- Agent performance
- Behavioral learning
- Coaching

Learning recommendations must be validated before becoming active system behavior.

---

# 4. Core Components

The initial architecture contains these major components.

```text
tradeos/
├── core/
├── orchestration/
├── agents/
├── markets/
├── data/
├── strategies/
├── prediction/
├── portfolio/
├── risk/
├── execution/
├── backtesting/
├── learning/
├── dashboard/
├── storage/
├── monitoring/
├── config/
└── tests/
```

The physical repository structure may evolve while preserving logical boundaries.

---

# 5. Orchestrator

The Orchestrator is the workflow coordinator.

It is responsible for:

- Receiving system events
- Selecting workflows
- Invoking appropriate agents
- Passing structured context
- Maintaining workflow state
- Enforcing iteration limits
- Handling timeouts
- Terminating workflows
- Recording workflow outcomes

It must not:

- Override Risk
- Place unauthorized orders
- Modify immutable safety rules
- Give agents unrestricted context

---

# 6. Event Bus

TradeOS should use an event-driven communication model.

Examples:

```text
market.data.updated
setup.detected
analysis.completed
trade.proposed
trade.criticized
portfolio.reviewed
risk.approved
risk.rejected
order.submitted
order.filled
order.rejected
position.updated
trade.closed
risk.limit.reached
learning.pattern.detected
```

Events should be structured and versioned.

---

# 7. Market Data Gateway

The Market Data Gateway provides a normalized interface over different data providers.

```text
Provider A ─┐
Provider B ─┼──> Market Data Gateway ──> Normalized Data
Provider C ─┘
```

Responsibilities:

- Ingest data
- Validate data
- Normalize schemas
- Track freshness
- Detect anomalies
- Provide historical data
- Provide real-time data

The Gateway should not make trading decisions.

---

# 8. Market Adapter

Each supported market should have a market adapter/profile.

Conceptually:

```text
Market Interface
      │
      ├── NSE/BSE
      ├── US Equities
      ├── Options
      ├── Crypto
      ├── Forex
      ├── Gold
      └── Commodities
```

Market adapters encapsulate:

- Trading sessions
- Time zones
- Tick size
- Lot size
- Contract specifications
- Market holidays
- Order constraints
- Margin rules
- Leverage rules

---

# 9. Intelligence Layer

The intelligence layer contains specialized analytical components.

Initial components:

```text
Technical Analysis
Fundamental Analysis
News/Sentiment
Market Regime
Strategy
Prediction
Research
Critic
```

These components produce structured outputs rather than directly executing trades.

---

# 10. Strategy Engine

The Strategy Engine provides a common framework for strategy plugins.

Each strategy must declare:

- Identifier
- Version
- Supported markets
- Timeframes
- Required data
- Entry conditions
- Exit conditions
- Risk assumptions
- Position sizing requirements
- Validation status

Strategies produce proposals.

They do not execute trades.

---

# 11. Prediction Engine

The Prediction Engine may contain:

- Statistical models
- Machine learning models
- LLM-assisted reasoning
- Regime models
- Probability estimators

Predictions should be represented as probabilities or scenario estimates.

The Prediction Engine must not directly authorize execution.

---

# 12. Critic Layer

The Critic evaluates a proposed trade from an adversarial perspective.

It should look for:

- Contradictory evidence
- Weak assumptions
- Data problems
- Overfitting
- Poor risk/reward
- Market-regime mismatch
- Excessive confidence
- Missing confirmation

The Critic may recommend rejection or further analysis.

It cannot override hard Risk rules.

---

# 13. Portfolio Layer

The Portfolio Layer evaluates the proposed trade in relation to the existing portfolio.

It should calculate or retrieve:

- Exposure
- Concentration
- Correlation
- Directional risk
- Sector risk
- Market risk
- Currency risk
- Leverage
- Margin
- Aggregate downside

Portfolio constraints may reject otherwise valid strategy signals.

---

# 14. Risk Architecture

Risk is deliberately separated into two cooperating components:

```text
                 ┌──────────────────────┐
Trade Proposal → │ Deterministic Risk   │
                 │ Engine               │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Risk Agent           │
                 │ Explanation / Review  │
                 └──────────┬───────────┘
                            │
                            ▼
                       RISK GATE
                       /                           REJECT    APPROVE
```

The deterministic Risk Engine should enforce hard numerical constraints.

The Risk Agent can provide contextual reasoning and explanations.

The Risk Agent must not weaken deterministic constraints.

---

# 15. Risk Gate

The Risk Gate is a mandatory checkpoint before execution.

Minimum checks should include:

- Risk per trade
- Stop-loss
- Position size
- Daily loss
- Drawdown
- Portfolio exposure
- Correlation
- Leverage
- Margin
- Liquidity
- Data freshness
- Operating mode

The output should be explicit:

```text
APPROVED
REJECTED
REQUIRES_REVIEW
```

Only `APPROVED` may proceed toward execution.

---

# 16. Execution Architecture

Execution should be separated from strategy logic.

```text
Approved Trade
      ↓
Execution Engine
      ↓
Order Validator
      ↓
Broker Interface
      ↓
Broker Adapter
      ↓
External Broker
```

The Execution Engine must:

- Validate order parameters
- Enforce authorized operating mode
- Prevent duplicate orders
- Submit orders
- Verify order state
- Verify fills
- Reconcile positions
- Report execution results

---

# 17. Order Management System

The OMS should track:

- Order ID
- Client order ID
- Broker order ID
- Instrument
- Side
- Quantity
- Price
- Order type
- Status
- Fill quantity
- Average fill
- Timestamps
- Strategy
- Trade proposal
- Workflow

Order state should be modeled explicitly.

Example:

```text
CREATED
  ↓
VALIDATED
  ↓
SUBMITTED
  ↓
ACKNOWLEDGED
  ↓
PARTIALLY_FILLED
  ↓
FILLED
```

Alternative terminal states include:

```text
REJECTED
CANCELLED
EXPIRED
FAILED
UNKNOWN
```

`UNKNOWN` must trigger reconciliation rather than assumptions.

---

# 18. Position Management

Position state should be independently reconciled with the broker.

The system must distinguish between:

- Intended position
- Recorded position
- Broker-reported position

Differences must trigger reconciliation.

---

# 19. Trade Journal

Every completed or rejected trade proposal should produce a journal record where appropriate.

The journal should contain:

- Market
- Instrument
- Strategy
- Thesis
- Evidence
- Prediction
- Critic findings
- Portfolio analysis
- Risk decision
- Execution
- Outcome
- Lessons

The journal is a major input to the Learning System.

---

# 20. Learning Architecture

The Learning System is a first-class subsystem.

It should analyze:

```text
Trade Journal
     │
     ├── Outcome Analysis
     ├── Mistake Detection
     ├── Pattern Detection
     ├── Strategy Performance
     ├── Agent Performance
     ├── Prediction Calibration
     └── Behavioral Learning
```

The purpose is not simply to report performance.

It is to identify repeatable patterns.

---

# 21. Repeated-Mistake Learning Loop

A central TradeOS capability is learning from recurring mistakes.

The lifecycle is:

```text
Decision
   ↓
Outcome
   ↓
Post-Trade Analysis
   ↓
Mistake Classification
   ↓
Pattern Candidate
   ↓
Repeated Evidence
   ↓
Validated Pattern
   ↓
Learning Recommendation
   ↓
Approved Learning Rule
   ↓
Future Decision Context
   ↓
New Outcome
   └───────────────→ Learning
```

A single mistake should not automatically become a permanent rule.

---

# 22. Mistake Taxonomy

The Learning System should classify mistakes.

## Trading Mistakes

Examples:

- Late entry
- Chasing price
- Ignoring stop
- Weak setup
- Overtrading
- Premature exit
- Holding invalidated trade
- Excessive risk

## Analysis Mistakes

Examples:

- Misread trend
- Ignored contradictory evidence
- Indicator overreliance
- Poor regime interpretation
- Prediction overconfidence

## Process Mistakes

Examples:

- Missing confirmation
- Incomplete checklist
- Poor context
- Risk review failure
- Execution preparation failure

## System Mistakes

Examples:

- Duplicate signal
- Agent loop
- Data error
- Incorrect calculation
- Position reconciliation error
- Order-state error

---

# 23. Repeated-Mistake Detection

The system should distinguish:

```text
Observed Once
     ↓
Logged

Observed Repeatedly
     ↓
Pattern Candidate

Repeated With Evidence
     ↓
Validated Pattern

Validated Pattern
     ↓
Learning Recommendation
```

Patterns should consider:

- Frequency
- Severity
- Financial impact
- Market
- Strategy
- Market regime
- Agent
- Timeframe
- Recency
- Statistical significance where appropriate

---

# 24. Behavioral Learning

TradeOS should learn behavioral patterns such as:

- Repeated late entries
- Repeated FOMO entries
- Repeated trades after losses
- Repeated risk increases
- Repeated premature exits
- Repeated stop widening
- Repeated trading outside preferred conditions

Behavioral insights may produce warnings or constraints.

They must be distinguishable from hard risk rules.

---

# 25. Agent Learning

TradeOS should also evaluate the agents themselves.

Examples:

```text
Technical Agent
    ↓
Repeatedly overweights weak breakout signals

Prediction Agent
    ↓
Consistent overconfidence in high volatility

Critic Agent
    ↓
Frequently identifies valid risks

Strategy Agent
    ↓
Strong performance in trending regimes
```

Agent performance becomes part of system learning.

---

# 26. Learning Governance

The Learning Agent may:

- Detect patterns
- Generate reports
- Recommend rule changes
- Recommend strategy changes
- Recommend agent adjustments

It may not:

- Change immutable safety rules
- Increase permitted risk
- Enable live trading
- Deploy an unvalidated strategy
- Modify historical records

Proposed changes require validation and appropriate approval.

---

# 27. Memory Architecture

TradeOS should distinguish different types of memory.

### Short-Term Memory

Current workflow state.

### Operational Memory

Current positions, orders, system state, and recent events.

### Episodic Memory

Individual trades and decisions.

### Pattern Memory

Validated recurring patterns.

### Strategy Memory

Strategy performance and validation history.

### Agent Memory

Agent-specific performance and known weaknesses.

### User Learning Memory

Long-term educational observations relevant to the trading workflow.

Memory must have ownership, scope, retention, and access rules.

---

# 28. Context Manager

The Context Manager determines what information an agent receives.

Example:

```text
Agent Request
      ↓
Context Manager
      ↓
Relevant Memory
      +
Current Market State
      +
Relevant Strategy
      +
Risk State
      ↓
Compact Agent Context
```

The Context Manager is essential for token efficiency.

---

# 29. Agent Registry

The Agent Registry should maintain metadata for every agent.

Examples:

- Agent ID
- Version
- Capabilities
- Tools
- Permissions
- Context requirements
- Timeout
- Token budget
- Model
- Status

The registry should make agent capabilities discoverable without requiring every agent to know every other agent.

---

# 30. Agent Runtime

The Agent Runtime should provide a common execution environment.

It should manage:

- Agent invocation
- Input validation
- Output validation
- Context injection
- Timeouts
- Retries
- Token accounting
- Logging
- Error handling

Agents should not implement these concerns independently.

---

# 31. Research Layer

The Research Layer should provide isolated environments for:

- Strategy ideas
- Model experiments
- Data analysis
- Indicator research
- Academic research
- Hypothesis testing

Research outputs should be versioned.

Research code must not directly activate production trading.

---

# 32. Backtesting Layer

The Backtesting Engine should share interfaces with production strategy logic where practical.

This reduces divergence between:

```text
Backtest Strategy
```

and:

```text
Production Strategy
```

The backtester should support:

- Historical data
- Transaction costs
- Slippage
- Position sizing
- Risk rules
- Market sessions
- Metrics
- Trade logs
- Reproducibility

---

# 33. Paper Trading Layer

Paper trading should reproduce the live execution path as closely as practical while using simulated capital.

```text
Real Market Data
      ↓
Real Strategy
      ↓
Real Risk
      ↓
Paper Execution
      ↓
Simulated Portfolio
```

This provides a safer bridge between research and live trading.

---

# 34. Operating Mode Architecture

Operating mode should be a first-class system state.

```text
RESEARCH
BACKTEST
PAPER
ASSISTED_LIVE
CONTROLLED_AUTONOMOUS
EMERGENCY
```

The mode must be checked by execution controls.

A strategy cannot independently decide to move the system into a more autonomous mode.

---

# 35. Kill Switch

The system should have multiple kill-switch layers.

```text
User Kill Switch
       +
Risk Kill Switch
       +
System Safety Kill Switch
       +
Broker/Execution Safety
```

Any authoritative safety layer may stop new trading.

---

# 36. Storage Architecture

PostgreSQL is the intended primary structured datastore.

Potential storage domains:

```text
PostgreSQL
├── instruments
├── market metadata
├── strategies
├── models
├── agents
├── trade proposals
├── orders
├── positions
├── trades
├── risk decisions
├── agent outputs
├── learning patterns
├── backtest runs
└── audit events
```

Large historical datasets may use specialized/object storage depending on scale.

---

# 37. Cache Architecture

A cache such as Redis may be used for:

- Short-lived state
- Frequently accessed market state
- Workflow state
- Rate-limit tracking
- Temporary agent context

The cache must not become the authoritative source for durable trading history.

---

# 38. Security Architecture

Security boundaries should exist between:

```text
Research
    ↓
Development
    ↓
Paper
    ↓
Live
```

Live broker credentials must be protected more strongly than research credentials.

Agents should never receive raw secrets.

---

# 39. Configuration Architecture

Configuration should be centrally managed.

Conceptually:

```text
Environment
     ↓
Configuration
     ↓
Validation
     ↓
Runtime
```

Configuration must include:

- Risk parameters
- Operating mode
- Agent limits
- Data freshness
- Broker configuration
- Strategy settings

Safety-critical values require additional protection.

---

# 40. Observability Architecture

Every important workflow should be traceable.

A useful trace may look like:

```text
workflow_id
   ↓
trade_proposal_id
   ↓
strategy_run_id
   ↓
prediction_id
   ↓
critic_id
   ↓
portfolio_review_id
   ↓
risk_decision_id
   ↓
order_id
   ↓
fill_id
   ↓
position_id
   ↓
trade_id
   ↓
learning_event_id
```

This provides end-to-end auditability.

---

# 41. Data Flow: Candidate Trade

A candidate trade should flow through:

```text
Market Data
     ↓
Data Validation
     ↓
Market Context
     ↓
Strategy Evaluation
     ↓
Prediction
     ↓
Critic
     ↓
Portfolio Review
     ↓
Risk Engine
     ↓
Risk Agent / Risk Gate
     ↓
Human Approval if Required
     ↓
Execution
```

---

# 42. Data Flow: Rejected Trade

Rejection is also a useful outcome.

```text
Trade Proposal
     ↓
Risk / Portfolio / Critic
     ↓
REJECTED
     ↓
Reason Recorded
     ↓
Journal
     ↓
Learning System
```

TradeOS should learn from rejected opportunities as well as executed trades.

---

# 43. Data Flow: Completed Trade

```text
Execution
     ↓
Fill
     ↓
Position
     ↓
Trade Management
     ↓
Exit
     ↓
Trade Closed
     ↓
Journal
     ↓
Outcome Analysis
     ↓
Mistake / Pattern Detection
     ↓
Learning
```

---

# 44. Data Flow: Repeated Mistake

```text
Trade #1
   ↓
Mistake: Late Entry
   ↓
Trade #7
   ↓
Mistake: Late Entry
   ↓
Trade #14
   ↓
Mistake: Late Entry
   ↓
Pattern Detection
   ↓
"Late Entry Pattern"
   ↓
Evidence Review
   ↓
Validated Learning
   ↓
Future Setup Warning
```

The system should track whether the intervention reduces recurrence.

---

# 45. Autonomy Boundaries

Autonomy should exist at multiple levels.

### Level 0 — Observe

System only analyzes.

### Level 1 — Recommend

System proposes decisions.

### Level 2 — Assist

System executes only after user approval.

### Level 3 — Controlled Autonomy

System executes within explicit constraints.

### Level 4 — Emergency

System prevents new trading.

No component may independently increase its autonomy level.

---

# 46. Architectural Invariants

The following must remain true:

1. Risk can veto strategy.
2. Execution cannot bypass Risk.
3. Agents cannot modify immutable safety rules.
4. Research cannot silently modify production.
5. Live mode must be explicit.
6. Data integrity is mandatory.
7. Important decisions are auditable.
8. Agent communication is bounded.
9. Learning cannot silently self-deploy.
10. The system must fail safely.

---

# 47. Failure Scenarios

### Market Data Failure

```text
Data failure
 ↓
Mark data invalid/stale
 ↓
Reject affected trade proposals
 ↓
Alert
```

### Broker Failure

```text
Broker uncertainty
 ↓
Pause new execution
 ↓
Reconcile orders/positions
 ↓
Alert
```

### Risk Engine Failure

```text
Risk unavailable
 ↓
No new trades
 ↓
Alert
```

### Agent Timeout

```text
Agent timeout
 ↓
Terminate workflow branch
 ↓
Retry if permitted
 ↓
Otherwise reject/escalate
```

### Position Mismatch

```text
Internal Position ≠ Broker Position
 ↓
Stop new affected orders
 ↓
Reconcile
 ↓
Resume only after consistency
```

---

# 48. Architecture Decision Boundaries

This document intentionally does not finalize every technology choice.

Future documents will define details for:

- Agent contracts
- Data schemas
- Database tables
- APIs
- Risk parameters
- Prediction architecture
- Learning architecture
- Deployment
- Security

Those decisions should be recorded in:

`decisions/ARCHITECTURAL_DECISIONS.md`

---

# 49. Initial Implementation Boundary

The first implementation should be intentionally narrow.

Recommended first vertical slice:

```text
One Market
   ↓
One Data Provider
   ↓
One Strategy
   ↓
Deterministic Risk Engine
   ↓
Backtesting
   ↓
Paper Trading
   ↓
Trade Journal
   ↓
Basic Learning
```

Then progressively introduce:

```text
Additional Agents
Additional Strategies
Additional Markets
Prediction Models
Advanced Learning
Live Execution
```

This prevents the project from becoming an untestable distributed system before the core workflow is proven.

---

# 50. Architectural Success Criteria

The architecture is successful when:

- Components are independently testable.
- Markets are pluggable.
- Strategies are pluggable.
- Agents are bounded.
- Risk is authoritative.
- Execution is isolated.
- Research is isolated.
- Learning is measurable.
- Repeated mistakes can be detected.
- Important decisions are reconstructable.
- AI context is controlled.
- Failure produces safer behavior.
- The first implementation can remain small.

---

# 51. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`
- `docs/23_CODEX_IMPLEMENTATION_PLAN.md`
- `decisions/ARCHITECTURAL_DECISIONS.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS system architecture, including repeated-mistake learning |

---

> **Architecture principle: intelligence may propose, governance decides, risk authorizes, execution verifies, and learning improves the next decision.**
