# TradeOS Trading Workflows

**Document:** 07_TRADING_WORKFLOWS.md  
**Version:** 0.2.0  
**Status:** Architecture Baseline  
**Scope:** End-to-end workflows for research, analysis, trade proposals, risk, execution, trade management, journaling, learning, and recovery

---

## 1. Purpose

This document defines the operational workflows through which TradeOS moves from information to decisions, execution, outcomes, and learning.

The most important principle is:

> **A trade is a controlled workflow, not a single AI decision.**

TradeOS should preserve a clear separation between:

```text
Observation
    ↓
Analysis
    ↓
Proposal
    ↓
Critique
    ↓
Portfolio Review
    ↓
Risk Evaluation
    ↓
Risk Review
    ↓
Risk Gate
    ↓
Execution Authorization
    ↓
Execution
    ↓
Outcome
    ↓
Learning
```

---

# 2. Workflow Design Principles

Every important workflow should be:

- Explicit
- Bounded
- Auditable
- Versioned
- Idempotent where required
- Failure-aware
- Risk-first
- Observable
- Reproducible where practical
- Efficient in its use of context and computation

No workflow may bypass mandatory safety gates.

TradeOS should not run every available agent for every opportunity. The Orchestrator should select the minimum sufficient set of capabilities and context required for the workflow, and stop optional analysis when additional reasoning is unlikely to improve the decision materially.

This is not token minimization for its own sake. The objective is to **learn to think more efficiently** while preserving decision quality, safety, and auditability.

---

# 3. Operating Modes

TradeOS supports progressively increasing levels of autonomy.

```text
RESEARCH
   ↓
BACKTEST
   ↓
PAPER
   ↓
ASSISTED_LIVE
   ↓
CONTROLLED_AUTONOMOUS
   ↓
EMERGENCY
```

The current operating mode must be known before an execution workflow begins.

---

# 4. Workflow State Model

A workflow should have explicit states.

```text
CREATED
  ↓
RUNNING
  ↓
WAITING
  ↓
COMPLETED
```

Failure states:

```text
FAILED
TIMEOUT
CANCELLED
REJECTED
ESCALATED
```

A workflow must not remain indefinitely in an ambiguous state.

---

# 5. Workflow Correlation

Every trading workflow should receive a unique:

```text
workflow_id
```

Related entities should reference it:

```text
workflow_id
 ├── agent runs
 ├── strategy run
 ├── prediction
 ├── critic
 ├── portfolio review
 ├── risk decision
 ├── order
 ├── trade
 └── learning event
```

This enables complete traceability.

---

# 6. Workflow 1 — Market Data Ingestion

## Purpose

Acquire and validate market information.

```text
External Provider
      ↓
Market Data Gateway
      ↓
Schema Validation
      ↓
Data Quality Checks
      ↓
Normalization
      ↓
Store
      ↓
Publish Event
```

Potential event:

```text
market.data.updated
```

### Failure

If data is:

- Missing
- Stale
- Invalid
- Contradictory

the affected data should be marked accordingly.

No downstream workflow should silently treat invalid data as valid.

---

# 7. Workflow 2 — Market Scan

## Purpose

Identify instruments or market conditions worth analyzing.

```text
Market Data
      ↓
Market Scan
      ↓
Candidate Instruments
      ↓
Market Context
      ↓
Setup Detection
```

The scan may consider:

- Price movement
- Volume
- Volatility
- Market regime
- Technical conditions
- Fundamental events
- News
- Strategy eligibility

The scan produces candidates, not orders.

---

# 8. Workflow 3 — Setup Detection

```text
Candidate Instrument
      ↓
Relevant Strategy
      ↓
Strategy Conditions
      ↓
Setup Candidate
```

The setup should identify:

- Instrument
- Direction
- Timeframe
- Entry concept
- Invalidation
- Target concept
- Evidence
- Strategy version

If conditions are incomplete, the workflow should return:

```text
NO_SETUP
```

This is a valid result.

---

# 9. Workflow 4 — Multi-Agent Trade Analysis

Once a valid setup candidate exists:

```text
Setup Candidate
      ↓
Orchestrator
      │
      ├── Technical Agent
      ├── Fundamental Agent
      ├── News Agent
      ├── Market Regime Agent
      ├── Strategy Agent
      └── Prediction Agent
      ↓
Structured Analysis
```

Not every agent must run for every market.

The Orchestrator should select agents based on:

- Asset class
- Strategy
- Available data
- Market
- Workflow requirements
- Expected information value

The Orchestrator should avoid redundant agent calls and should stop optional analysis once sufficient evidence exists for the next workflow stage.

---

# 10. Workflow 5 — Prediction

The Prediction Agent may generate:

```text
Bullish scenario
Neutral scenario
Bearish scenario
```

with probabilities and uncertainty.

Example:

```text
Bullish: 0.67
Neutral: 0.20
Bearish: 0.13
```

Prediction output must include:

- Model version
- Horizon
- Timestamp
- Confidence/calibration metadata
- Input references

Prediction does not authorize execution.

---

# 11. Workflow 6 — Trade Proposal

The Strategy Agent combines relevant analysis into a formal proposal.

```text
Analysis
   ↓
Strategy Rules
   ↓
Trade Proposal
```

The proposal should define:

- Instrument
- Direction
- Entry
- Stop
- Target
- Quantity concept
- Strategy
- Thesis
- Evidence
- Invalidations
- Expected scenarios

A proposal is not an order.

---

# 12. Workflow 7 — Critic Review

Every trade proposal should pass through a Critic review unless a documented workflow explicitly excludes it.

```text
Trade Proposal
      ↓
Critic Agent
      ↓
┌──────────────┬──────────────┐
│              │              │
PASS         CONCERN        REJECT
```

The Critic should challenge:

- Weak evidence
- Contradictions
- Poor market regime
- Overconfidence
- Poor reward/risk
- Missing confirmation
- Data quality
- Potential overfitting

---

# 13. Workflow 8 — Portfolio Review

The Portfolio Agent evaluates the proposed trade in the context of current exposure.

```text
Trade Proposal
      +
Existing Portfolio
      ↓
Portfolio Review
      ↓
Impact Assessment
```

It should evaluate:

- Existing positions
- Correlation
- Concentration
- Directional exposure
- Sector exposure
- Currency exposure
- Margin
- Leverage
- Aggregate risk

---

# 14. Workflow 9 — Risk Authorization

This is a mandatory control sequence.

```text
Trade Proposal
      ↓
Deterministic Risk Engine
      ↓
Risk Review Agent
      ↓
Risk Gate
```

The three stages have distinct authority:

```text
Risk Engine
    = deterministic hard numerical constraints

Risk Review Agent
    = contextual review and explanation

Risk Gate
    = deterministic enforcement decision
```

Possible results:

```text
APPROVED
REJECTED
REQUIRES_REVIEW
```

### Hard Rule

If a hard risk constraint fails:

```text
Risk Engine → REJECTED
       ↓
STOP
```

No AI agent or user approval may override a hard Risk Engine rejection.

A contextual Risk Review may add concerns or require review, but it cannot convert a hard rejection into approval.

---

# 15. Position Sizing Workflow

Position sizing should be deterministic.

Conceptually:

```text
Account Equity
      +
Risk Percentage
      +
Entry
      +
Stop
      +
Instrument Rules
      ↓
Maximum Risk Amount
      ↓
Position Size
```

The exact formula depends on the instrument.

Market-specific rules must be applied.

---

# 16. Workflow 10 — Human Approval

In `ASSISTED_LIVE` mode:

```text
Risk Gate Approved
      ↓
User Review
      ↓
APPROVE / REJECT
```

The user should be able to see:

- Thesis
- Evidence
- Prediction
- Critic findings
- Portfolio impact
- Risk
- Position size
- Entry
- Stop
- Target
- Expected scenarios

Human approval is an additional authorization step where required. It cannot bypass a failed hard risk constraint.

---

# 17. Workflow 11 — Execution

Only an authorized proposal may reach execution.

```text
Risk Gate Approved
      ↓
Human Approval if Required
      ↓
Execution Authorization
      ↓
Execution Service / OMS
      ↓
Order Validation
      ↓
Broker Adapter
      ↓
Order Submission
      ↓
Order Status
      ↓
Fill Verification
```

The execution layer must not assume a fill.

Execution state is owned by the deterministic execution service/OMS, not by an autonomous reasoning agent.

---

# 18. Workflow 12 — Order State Reconciliation

After submission:

```text
Order Submitted
      ↓
Broker Status
      ↓
TradeOS Status
      ↓
Compare
```

If states disagree:

```text
UNKNOWN / MISMATCH
      ↓
Reconciliation
      ↓
Pause affected execution if necessary
```

Never create a duplicate order simply because the first order's status is uncertain.

---

# 19. Workflow 13 — Position Reconciliation

At appropriate intervals and after material events:

```text
Internal Position
      +
Broker Position
      ↓
Compare
      ↓
MATCH
or
MISMATCH
```

A mismatch should trigger:

- Investigation
- Reconciliation
- Potential execution pause

---

# 20. Workflow 14 — Trade Management

Once a position exists:

```text
Position
   ↓
Trade Management
   ↓
Monitor Conditions
   ↓
Exit Rules
```

Trade management may include:

- Stop-loss
- Trailing stop
- Trailing target
- Partial exit
- Time-based exit
- Strategy invalidation
- Risk-based exit

Trade management must remain within the original risk framework.

---

# 21. Stop-Loss Protection

The system must never widen a stop simply to avoid realizing a loss unless such behavior is explicitly defined and validated as part of a strategy.

A strategy must not modify risk controls opportunistically.

---

# 22. Workflow 15 — Trade Closure

A trade closes when the position reaches its terminal state.

```text
Position
      ↓
Exit
      ↓
Fill Verification
      ↓
Position Reconciliation
      ↓
Trade Closed
```

The trade record should use actual fills.

---

# 23. Workflow 16 — Post-Trade Analysis

Every completed trade should enter post-trade analysis.

```text
Trade Closed
      ↓
Expected vs Actual
      ↓
Decision Quality
      ↓
Execution Quality
      ↓
Risk Quality
      ↓
Mistake Detection
```

---

# 24. Decision Quality

The system should classify decisions separately from outcomes.

Examples:

```text
GOOD_DECISION_WIN
GOOD_DECISION_LOSS
BAD_DECISION_WIN
BAD_DECISION_LOSS
```

This prevents outcome bias.

---

# 25. Workflow 17 — Mistake Detection

Post-trade analysis may identify:

```text
Trading Mistake
Analysis Mistake
Process Mistake
System Mistake
Agent Mistake
```

Each identified mistake should contain:

- Type
- Evidence
- Severity
- Confidence
- Detection source
- Context

---

# 26. Workflow 18 — Repeated Mistake Detection

A single mistake is logged.

Repeated mistakes trigger pattern analysis.

```text
Mistake
 ↓
Historical Search
 ↓
Similar Mistakes
 ↓
Context Comparison
 ↓
Pattern Candidate
```

The system should evaluate:

- Frequency
- Severity
- Financial impact
- Market
- Strategy
- Regime
- Timeframe
- Recency

---

# 27. Workflow 19 — Learning Validation

A pattern should not immediately become a permanent rule.

```text
Pattern Candidate
      ↓
Evidence Review
      ↓
Statistical / Historical Validation
      ↓
Human or Governance Review
      ↓
Validated Learning Rule
```

The exact governance threshold depends on the learning type.

---

# 28. Workflow 20 — Learning Intervention

Once a learning rule is approved:

```text
Active Learning Rule
      ↓
Context Manager
      ↓
Future Trade Workflow
```

Example:

```text
Recurring Pattern:
Late Entry

Future Proposal:
Entry significantly beyond defined setup zone

System:
"Recurring late-entry pattern detected."
```

The intervention may be:

- Warning
- Additional confirmation
- Critic escalation
- Review requirement
- Trade rejection

The intervention should be measurable.

---

# 29. Workflow 21 — Measure Learning Effectiveness

TradeOS should evaluate whether a learning intervention works.

```text
Baseline
   ↓
Learning Rule Activated
   ↓
Post-Intervention Period
   ↓
Compare
```

Possible metrics:

- Mistake frequency
- Mistake severity
- Financial impact
- Compliance rate
- False intervention rate

A learning rule that does not improve outcomes should be reconsidered.

---

# 30. Workflow 22 — Agent Performance Learning

Agents should be evaluated against outcomes.

```text
Agent Output
      ↓
Prediction / Recommendation
      ↓
Actual Outcome
      ↓
Agent Performance
      ↓
Pattern Detection
```

Examples:

- Prediction overconfidence
- Technical false positives
- Critic false negatives
- News misclassification
- Regime misclassification

---

# 31. Workflow 23 — Strategy Performance Review

Strategies should be reviewed periodically.

Analyze:

- Returns
- Drawdown
- Expectancy
- Win/loss
- Regime performance
- Market performance
- Slippage
- Failure patterns
- Trade frequency

A strategy should not be judged by one trade.

---

# 32. Workflow 24 — Strategy Promotion

A research strategy should progress:

```text
DRAFT
 ↓
BACKTEST
 ↓
ROBUSTNESS TEST
 ↓
OUT-OF-SAMPLE
 ↓
WALK-FORWARD
 ↓
PAPER
 ↓
REVIEW
 ↓
APPROVED
 ↓
PRODUCTION
```

Every stage should have defined entry and exit criteria.

---

# 33. Workflow 25 — Strategy Retirement

A strategy may be retired when:

- Performance deteriorates
- Risk characteristics change
- Market regime changes
- Data assumptions fail
- Execution assumptions become invalid
- Validation criteria are no longer met

Retirement should preserve historical versions.

---

# 34. Workflow 26 — Research Experiment

```text
Hypothesis
   ↓
Experiment Definition
   ↓
Dataset Selection
   ↓
Strategy / Model
   ↓
Backtest
   ↓
Robustness
   ↓
Results
   ↓
Conclusion
```

A negative result is still valuable.

---

# 35. Workflow 27 — Research-to-Production

```text
Research
   ↓
Candidate
   ↓
Validation
   ↓
Paper
   ↓
Controlled Promotion
```

No direct:

```text
Research → Live
```

path should exist.

---

# 36. Workflow 28 — Daily Trading Cycle

A typical day may follow:

```text
Pre-Market
   ↓
Market Context
   ↓
Watchlist
   ↓
Setup Detection
   ↓
Intraday Analysis
   ↓
Trade Proposals
   ↓
Risk Evaluation
   ↓
Risk Review / Gate
   ↓
Execution
   ↓
Trade Management
   ↓
Market Close
   ↓
Post-Trade Review
   ↓
Learning Report
```

The exact schedule depends on the market.

---

# 37. Workflow 29 — End-of-Day Learning

At the end of a trading session:

```text
Trades
+
Rejected Trades
+
Missed Setups
+
Predictions
+
Agent Performance
+
Risk Events
      ↓
Daily Learning Analysis
      ↓
Lessons
      ↓
Repeated Patterns
      ↓
Coach Report
```

Rejected and missed opportunities should be analyzed where data supports it.

---

# 38. Workflow 30 — Weekly Review

A weekly review should evaluate:

- Strategy performance
- Agent performance
- Prediction calibration
- Repeated mistakes
- Risk behavior
- Execution quality
- Market regimes
- Learning interventions

The goal is to identify patterns that are difficult to see trade-by-trade.

---

# 39. Workflow 31 — Monthly Review

A longer review may evaluate:

- Strategy stability
- Portfolio risk
- Drawdown
- Behavioral trends
- Agent degradation
- Model calibration
- Data quality
- System reliability
- Cost
- Learning effectiveness

---

# 40. Workflow 32 — Emergency Halt

A critical event should trigger:

```text
Critical Event
      ↓
Safety Layer
      ↓
STOP NEW TRADING
      ↓
Cancel eligible pending orders if policy permits
      ↓
Reconcile positions
      ↓
Alert User
      ↓
Investigate
```

The exact response depends on the failure type.

---

# 41. Workflow 33 — Recovery

Recovery should be controlled.

```text
Failure
 ↓
Contain
 ↓
Diagnose
 ↓
Correct
 ↓
Test
 ↓
Reconcile
 ↓
Verify
 ↓
Resume
```

Resuming trading must not happen merely because a service restarted.

---

# 42. Workflow 34 — Data Failure

```text
Data Failure
      ↓
Mark Data Invalid
      ↓
Stop Affected Decisions
      ↓
Continue Unaffected Functions
      ↓
Alert
      ↓
Recover
      ↓
Revalidate Data
```

---

# 43. Workflow 35 — Agent Failure

```text
Agent Failure
      ↓
Log
      ↓
Retry if permitted
      ↓
Fallback if defined
      ↓
Continue only if safe
      ↓
Otherwise Escalate / Reject
```

A Risk Review Agent failure is treated differently from an optional analysis-agent failure. If required risk evaluation cannot be completed, the affected trade must not proceed to execution.

---

# 44. Workflow 36 — Broker Failure

```text
Broker Failure
      ↓
Pause New Execution
      ↓
Check Order State
      ↓
Reconcile
      ↓
Confirm Position State
      ↓
Resume Only When Safe
```

---

# 45. Workflow 37 — Configuration Change

Important configuration changes should follow:

```text
Proposed Change
      ↓
Validation
      ↓
Approval if Required
      ↓
Version
      ↓
Activate
      ↓
Audit
```

A configuration change must not silently alter historical records.

---

# 46. Workflow 38 — Model Promotion

```text
Candidate Model
      ↓
Validation
      ↓
Calibration
      ↓
Backtest / Evaluation
      ↓
Paper
      ↓
Review
      ↓
Approved Model Version
      ↓
Production
```

---

# 47. Workflow 39 — Agent Promotion

```text
Agent Prototype
      ↓
Contract Tests
      ↓
Scenario Tests
      ↓
Safety Tests
      ↓
Paper Environment
      ↓
Evaluation
      ↓
Approved
```

---

# 48. Workflow 40 — User-Initiated Trade

If the user manually proposes a trade:

```text
User Proposal
      ↓
Normalize
      ↓
Strategy / Analysis Review if applicable
      ↓
Critic
      ↓
Portfolio
      ↓
Risk Engine
      ↓
Risk Review Agent
      ↓
Risk Gate
      ↓
Execution if authorized
```

A manually initiated trade must still obey hard risk controls.

---

# 49. Workflow 41 — User Override

The user may be able to override certain recommendations.

However:

```text
User Override
      ↓
Risk Check
```

The user should not be able to bypass immutable safety controls through a normal workflow.

Any authorized override should be:

- Explicit
- Logged
- Attributed
- Time-stamped
- Reviewable

A hard Risk Engine rejection is not an overrideable recommendation.

---

# 50. Workflow 42 — No-Trade Decision

TradeOS must treat "do nothing" as a valid outcome.

Examples:

```text
No setup
Insufficient data
Risk too high
Poor reward/risk
Conflicting evidence
Portfolio exposure too high
Daily loss limit reached
Market conditions unsuitable
```

The system should not manufacture trades to remain active.

---

# 51. Workflow 43 — Missed Opportunity Analysis

TradeOS may analyze setups that were not traded.

```text
Potential Setup
      ↓
Why Not Traded?
      ↓
Valid Avoidance?
or
Missed Opportunity?
      ↓
Outcome
      ↓
Learning
```

This helps distinguish disciplined avoidance from excessive hesitation.

---

# 52. Workflow 44 — Counterfactual Analysis

Where reliable data exists, TradeOS may evaluate:

> "What would have happened if the trade had been taken?"

This must remain clearly labeled as counterfactual.

It must never be confused with actual P&L.

---

# 53. Workflow 45 — Agent Disagreement

If agents disagree:

```text
Agent Outputs
      ↓
Conflict Detection
      ↓
Critic / Orchestrator
      ↓
Resolve or Escalate
```

The system should preserve the disagreement.

Disagreement may become useful learning data.

Resolution should remain bounded; the system must not create an unbounded agent-to-agent debate loop.

---

# 54. Workflow 46 — Insufficient Evidence

If required evidence is missing:

```text
Missing Evidence
      ↓
INSUFFICIENT_DATA
      ↓
No Trade
or
Request Additional Analysis
```

The system must not fabricate missing information.

---

# 55. Workflow 47 — Token Budget Exhaustion

If an agent workflow approaches its token/cost budget:

```text
Budget Warning
      ↓
Compress / Select Relevant Context
      ↓
Terminate Optional Analysis
      ↓
Continue only if sufficient evidence remains
      ↓
Otherwise Escalate / Reject
```

Cost control must never cause unsafe risk behavior.

Token efficiency is a means to more efficient reasoning, not an objective that overrides decision quality or safety.

---

# 56. Workflow 48 — Audit Reconstruction

A historical trade should be reconstructable:

```text
Trade ID
   ↓
Workflow
   ↓
Market Data References
   ↓
Strategy Version
   ↓
Agent Outputs
   ↓
Prediction
   ↓
Critic
   ↓
Portfolio
   ↓
Risk Engine Result
   ↓
Risk Review Result
   ↓
Risk Gate Decision
   ↓
Execution Authorization
   ↓
Orders
   ↓
Fills
   ↓
Outcome
   ↓
Learning
```

---

# 57. Workflow 49 — Full Learning Loop

The complete TradeOS learning cycle is:

```text
MARKET
  ↓
ANALYSIS
  ↓
DECISION
  ↓
EXECUTION
  ↓
OUTCOME
  ↓
REVIEW
  ↓
MISTAKE / SUCCESS
  ↓
PATTERN
  ↓
VALIDATION
  ↓
LEARNING
  ↓
FUTURE CONTEXT
  ↓
NEW DECISION
```

This is one of the defining workflows of TradeOS.

Learning must improve future context and decisions without creating uncontrolled recursive agent loops.

---

# 58. Workflow 50 — Repeated Mistake Closed Loop

```text
Mistake A
   ↓
Historical Search
   ↓
Mistake A
   ↓
Mistake A
   ↓
Pattern Candidate
   ↓
Validation
   ↓
Learning Rule
   ↓
Future Trade
   ↓
Intervention
   ↓
Outcome
   ↓
Did Mistake Recur?
   ├── YES → Continue Learning
   └── NO  → Measure Improvement
```

The system should explicitly test whether the intervention worked.

---

# 59. Workflow 51 — Agent Self-Improvement Loop

Agent improvement follows:

```text
Agent Output
   ↓
Outcome
   ↓
Performance Evaluation
   ↓
Weakness Detection
   ↓
Pattern
   ↓
Recommendation
   ↓
Validation
   ↓
Agent Version Update
   ↓
Regression Testing
   ↓
Deployment
```

No uncontrolled self-modification is permitted.

Agent improvement is a governed versioned process, not a live recursive self-editing loop.

---

# 60. Workflow 52 — Learning Rule Retirement

A learning rule may become ineffective or harmful.

Therefore:

```text
Active Rule
   ↓
Performance Monitoring
   ↓
Degradation
   ↓
Review
   ↓
Modify / Disable / Retire
```

Historical activation records should remain preserved.

---

# 61. Workflow Invariants

The following must remain true:

1. No execution without authorization.
2. No execution without Risk approval.
3. Hard Risk rejection cannot be overridden.
4. Invalid data cannot silently enter decisions.
5. Unknown order state requires reconciliation.
6. Research cannot directly activate production.
7. Learning cannot silently modify safety controls.
8. Every important decision is auditable.
9. "No trade" is always a valid result.
10. Mistakes can be learned from without treating every loss as a mistake.
11. Agent disagreement is preserved.
12. Counterfactual results are not actual outcomes.
13. Risk Engine, Risk Review Agent, and Risk Gate have distinct responsibilities.
14. Execution state is owned by the deterministic Execution Service / OMS.
15. Optional agent analysis should be selected and bounded rather than run indiscriminately.
16. Efficient reasoning must never weaken safety or decision quality.
17. Agent workflows must not create unbounded coordination loops.

---

# 62. Initial Implementation Workflows

The first implementation should focus on a small vertical slice:

```text
Market Data
   ↓
Strategy
   ↓
Trade Proposal
   ↓
Risk Engine
   ↓
Risk Gate
   ↓
Paper Execution
   ↓
Journal
   ↓
Mistake Detection
   ↓
Basic Learning
```

After this works reliably, expand into:

```text
Multi-Agent Analysis
Prediction
Portfolio
Advanced Trade Management
Agent Performance Learning
Additional Markets
Live Execution
```

---

# 63. Workflow Success Criteria

The workflow architecture is successful when TradeOS can:

- Trace a decision from data to outcome.
- Stop unsafe trades.
- Execute only authorized orders.
- Reconcile uncertain states.
- Record rejected opportunities.
- Detect repeated mistakes.
- Measure learning interventions.
- Measure agent performance.
- Preserve disagreements.
- Recover safely from failures.
- Reproduce historical workflows.
- Select context and agents efficiently without sacrificing decision quality.
- Maintain bounded orchestration without unnecessary agent-to-agent loops.

---

# 64. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/05_AGENT_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/11_BACKTESTING_AND_VALIDATION.md`
- `docs/12_EXECUTION_ARCHITECTURE.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial TradeOS trading workflow architecture |
| 0.2.0 | Architecture Baseline | Aligned risk authority, execution ownership, bounded orchestration, and efficient-reasoning principles |

---

> **Workflow principle: move from evidence to action through bounded, auditable, risk-controlled steps — then learn from outcomes without creating uncontrolled loops.**
