# TradeOS Agent Architecture

**Document:** 05_AGENT_ARCHITECTURE.md  
**Version:** 0.1.0  
**Status:** Architecture Baseline  
**Scope:** Agent roles, authority, contracts, context, communication, memory, governance, learning, and runtime behavior

---

## 1. Purpose

This document defines the architecture and governance of the TradeOS agent ecosystem.

TradeOS does not use one general-purpose AI agent to perform all trading functions.

Instead, it uses specialized agents with clearly bounded responsibilities.

The fundamental rule is:

> **Agents provide intelligence and services; system governance determines authority.**

No agent may bypass global safety rules, deterministic risk controls, or execution safeguards.

---

# 2. Agent Architecture Philosophy

The agent system follows:

```text
Specialization
      +
Least Privilege
      +
Structured Communication
      +
Bounded Autonomy
      +
Deterministic Governance
      +
Full Auditability
```

Agents should be:

- Specialized
- Replaceable
- Testable
- Observable
- Versioned
- Context-efficient
- Failure-aware

---

# 3. Agent Categories

TradeOS agents are grouped into three major categories.

## 3.1 Intelligence Agents

Generate analysis, research, forecasts, and recommendations.

- Market Research Agent
- Technical Analysis Agent
- Fundamental Analysis Agent
- News & Sentiment Agent
- Market Regime Agent
- Strategy Agent
- Prediction Agent

## 3.2 Governance Agents

Challenge, constrain, and authorize decisions.

- Critic Agent
- Portfolio Agent
- Risk Agent

## 3.3 Operational Agents

Coordinate, execute, record, learn, and explain.

- Orchestrator Agent
- Market Data Agent
- Execution Agent
- Learning Agent
- Coach Agent

The category does not override the detailed authority contract.

---

# 4. High-Level Agent Topology

```text
                              USER
                               │
                               ▼
                        ┌──────────────┐
                        │ ORCHESTRATOR │
                        └──────┬───────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
        DATA AGENTS      INTELLIGENCE         RESEARCH
                              │
          ┌───────────┬───────┼────────┬────────────┐
          ▼           ▼       ▼        ▼            ▼
      Technical   Fundamental News   Strategy    Prediction
          │           │       │        │            │
          └───────────┴───────┼────────┴────────────┘
                              ▼
                           CRITIC
                              │
                              ▼
                          PORTFOLIO
                              │
                              ▼
                         RISK GATE
                       HARD VETO LAYER
                              │
                       ┌──────┴──────┐
                       │             │
                    REJECT         APPROVE
                                     │
                                     ▼
                                 EXECUTION
                                     │
                                     ▼
                                   BROKER
                                     │
                                     ▼
                                  JOURNAL
                                     │
                           ┌─────────┴─────────┐
                           ▼                   ▼
                       LEARNING              COACH
                           │
                           ▼
                    VALIDATED LEARNING
                           │
                           ▼
                    FUTURE CONTEXT
```

---

# 5. Agent Authority Model

Every agent has an explicit authority level.

```text
L0 — Observe
L1 — Analyze
L2 — Recommend
L3 — Govern
L4 — Execute
```

Examples:

| Agent | Authority |
|---|---|
| Market Data | L0/L1 |
| Research | L1/L2 |
| Technical | L1/L2 |
| Fundamental | L1/L2 |
| News/Sentiment | L1/L2 |
| Strategy | L2 |
| Prediction | L1/L2 |
| Critic | L2 |
| Portfolio | L2/L3 |
| Risk | L3 |
| Execution | L4 |
| Learning | L1/L2 |
| Coach | L1/L2 |
| Orchestrator | Workflow coordination |

**Execution authority is isolated from analytical authority.**

---

# 6. Agent Contract

Every TradeOS agent must implement a formal contract.

Minimum fields:

```text
agent_id
agent_version
purpose
responsibilities
non_responsibilities
input_schema
output_schema
allowed_tools
allowed_data
allowed_memory
authority_level
callers
permitted_downstream_agents
timeout
retry_policy
token_budget
failure_policy
audit_requirements
performance_metrics
```

---

# 7. Agent Lifecycle

Agents follow:

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

Failure states may include:

```text
TIMEOUT
FAILED
CANCELLED
DEGRADED
DISABLED
```

An unhealthy agent must not silently continue producing trusted outputs.

---

# 8. Orchestrator Agent

## Purpose

Coordinates TradeOS workflows.

## Responsibilities

- Receive events
- Select workflows
- Invoke agents
- Pass structured context
- Manage workflow state
- Enforce iteration limits
- Handle timeouts
- Terminate workflows
- Record workflow outcomes

## Inputs

- System events
- User requests
- Market events
- Strategy requests
- Risk state
- Operating mode

## Outputs

- Workflow commands
- Structured agent requests
- Workflow state
- Final workflow status

## Tools

- Agent registry
- Workflow engine
- Context manager
- State manager

## Forbidden

- Bypassing Risk
- Direct unauthorized execution
- Modifying immutable safety rules
- Increasing autonomy
- Granting agents unrestricted access

---

# 9. Market Data Agent

## Purpose

Provide validated and normalized market information.

## Responsibilities

- Retrieve data
- Validate freshness
- Detect anomalies
- Normalize data
- Identify missing information
- Report data quality

## Outputs

Examples:

```text
OHLCV
Tick
Quote
Volume
Instrument metadata
Market status
Data quality
Freshness
```

## Forbidden

- Making trading decisions
- Authorizing trades
- Modifying strategy rules

---

# 10. Market Research Agent

## Purpose

Analyze broader market conditions and identify research opportunities.

## Responsibilities

- Market scanning
- Sector analysis
- Market-condition analysis
- Research hypothesis generation
- Candidate setup identification

## Outputs

- Market observations
- Candidate opportunities
- Research hypotheses
- Supporting evidence
- Contradictory evidence

## Forbidden

- Direct execution
- Risk override
- Live strategy modification

---

# 11. Technical Analysis Agent

## Purpose

Analyze price, volume, volatility, and technical structure.

## Potential Inputs

- OHLCV
- Volume
- Indicators
- Market regime
- Timeframes
- Historical context

## Potential Outputs

```text
trend
momentum
support_resistance
volatility
pattern
signal
confidence
evidence
invalidations
```

## Forbidden

- Direct execution
- Risk override
- Treating indicators as guaranteed predictions

---

# 12. Fundamental Analysis Agent

## Purpose

Evaluate fundamental information where applicable.

## Inputs

- Financial statements
- Earnings
- Valuation metrics
- Corporate information
- Macro data
- Company events

## Outputs

- Fundamental assessment
- Valuation observations
- Growth observations
- Risks
- Supporting evidence

## Forbidden

- Direct execution
- Treating fundamental analysis as certainty
- Overriding risk

For assets where conventional fundamentals are inappropriate, this agent may be inactive.

---

# 13. News & Sentiment Agent

## Purpose

Evaluate relevant news and sentiment.

## Responsibilities

- Identify material news
- Classify relevance
- Determine sentiment
- Detect potentially market-moving events
- Distinguish facts from commentary

## Outputs

- News events
- Relevance
- Sentiment
- Confidence
- Potential market impact

## Forbidden

- Trading solely from an unverified headline
- Direct execution
- Risk override

---

# 14. Market Regime Agent

## Purpose

Identify the current market environment.

Potential regimes:

```text
TRENDING_UP
TRENDING_DOWN
RANGE_BOUND
HIGH_VOLATILITY
LOW_VOLATILITY
BREAKOUT
MEAN_REVERSION
UNCERTAIN
```

The exact taxonomy will evolve.

## Outputs

- Current regime
- Regime confidence
- Supporting evidence
- Historical regime characteristics

Regime information may influence strategy selection but cannot override risk.

---

# 15. Strategy Agent

## Purpose

Determine whether a defined strategy produces a valid trade proposal.

## Responsibilities

- Evaluate strategy rules
- Identify setups
- Generate trade thesis
- Define entry concept
- Define invalidation
- Define target concept
- Identify required confirmations

## Outputs

A structured Trade Proposal.

Example:

```json
{
  "strategy_id": "example_strategy",
  "strategy_version": "1.0.0",
  "instrument": "XYZ",
  "direction": "LONG",
  "entry": 100,
  "stop": 97,
  "target": 108,
  "thesis": "Structured explanation",
  "evidence": [],
  "invalidations": []
}
```

## Forbidden

- Execution
- Risk override
- Stop widening to avoid losses
- Unvalidated strategy deployment

---

# 16. Prediction Agent

## Purpose

Estimate probabilities or scenarios.

## Outputs

Potentially:

```text
direction_probability
scenario_probabilities
expected_range
confidence
uncertainty
calibration_metadata
```

Example:

```text
Bullish scenario: 0.68
Neutral scenario: 0.21
Bearish scenario: 0.11
```

These are estimates, not guarantees.

## Forbidden

- Claiming certainty
- Direct execution
- Overriding Risk

---

# 17. Critic Agent

## Purpose

Act as an adversarial reviewer.

The Critic should actively search for reasons a proposed trade may fail.

## Responsibilities

- Challenge assumptions
- Search for contradictory evidence
- Identify missing confirmation
- Detect overconfidence
- Identify regime mismatch
- Identify poor reward/risk
- Identify data quality issues
- Identify potential overfitting

## Outputs

```text
CRITIC_PASS
CRITIC_CONCERN
CRITIC_REJECT
```

with structured reasons.

## Forbidden

- Forcing a trade
- Overriding hard Risk controls

---

# 18. Portfolio Agent

## Purpose

Evaluate the proposed trade in the context of the portfolio.

## Inputs

- Open positions
- Proposed position
- Correlations
- Exposure
- Margin
- Leverage
- Concentration
- Strategy exposure

## Outputs

- Portfolio impact
- Exposure impact
- Correlation risk
- Concentration warnings
- Recommendation

## Forbidden

- Overriding hard Risk limits

---

# 19. Risk Agent

## Purpose

Provide risk governance and explain risk decisions.

## Responsibilities

- Evaluate proposed risk
- Validate position size
- Review portfolio exposure
- Evaluate drawdown state
- Evaluate daily loss state
- Enforce configured limits
- Reject unsafe trades
- Trigger risk reduction
- Trigger trading halts

## Authority

**L3 — Governance**

The Risk Agent has hard veto authority.

However, numerical hard limits should also be enforced by a deterministic Risk Engine.

## Forbidden

The Risk Agent must not:

- Increase permitted risk without authorized configuration
- Disable safety limits
- Enable live trading
- Modify immutable global rules

---

# 20. Deterministic Risk Engine

The Risk Agent should not be the sole safety mechanism.

A deterministic Risk Engine should enforce hard numerical constraints.

```text
Trade Proposal
      ↓
Deterministic Risk Engine
      ↓
Risk Agent
      ↓
Risk Gate
```

If the deterministic engine rejects a trade, an LLM cannot overturn it.

---

# 21. Execution Agent

## Purpose

Execute authorized orders and maintain execution state.

## Responsibilities

- Validate approved orders
- Submit orders
- Track order status
- Verify fills
- Reconcile positions
- Report execution results

## Authority

**L4 — Execution**

But L4 does not mean unrestricted authority.

Execution requires an approved trade and valid operating mode.

## Forbidden

- Creating an independent strategy
- Bypassing Risk
- Increasing quantity without authorization
- Assuming a fill
- Enabling live trading

---

# 22. Learning Agent

## Purpose

Analyze outcomes and identify opportunities for improvement.

## Responsibilities

- Compare expected vs actual outcomes
- Detect mistakes
- Detect repeated mistakes
- Evaluate strategies
- Evaluate agents
- Evaluate prediction calibration
- Generate learning recommendations

## Forbidden

- Automatically modifying immutable safety rules
- Increasing risk
- Deploying unvalidated strategies
- Deleting unfavorable results

---

# 23. Coach Agent

## Purpose

Turn system activity into understandable education.

## Responsibilities

- Explain trades
- Explain rejected trades
- Explain mistakes
- Compare expectations vs outcomes
- Produce daily/weekly learning reports
- Identify educational topics
- Explain strategy behavior

## Forbidden

- Overriding risk
- Executing trades
- Changing strategy rules independently

---

# 24. Agent Memory

Agents should have controlled memory access.

Memory categories include:

```text
Current Workflow Memory
Operational Memory
Trade/Episodic Memory
Pattern Memory
Strategy Memory
Agent Performance Memory
Learning Memory
```

Agents should access only the memory relevant to their role.

---

# 25. Agent Performance Memory

TradeOS should measure how individual agents perform.

Examples:

```text
Technical Agent
- Signal precision
- False-positive rate
- Regime-specific performance

Prediction Agent
- Calibration
- Brier-like probability metrics
- Overconfidence frequency

Critic Agent
- Useful rejection rate
- Missed risks
- False objections

Data Agent
- Data-quality detection accuracy
- Freshness failures
```

Metrics should be designed carefully and should not encourage agents to game their scores.

---

# 26. Repeated Agent Mistakes

Agent behavior should be evaluated for recurring weaknesses.

Example:

```text
Prediction Agent
     ↓
Repeated high-confidence forecasts
     ↓
Poor outcomes during high volatility
     ↓
Pattern detected
     ↓
"Potential high-volatility overconfidence"
     ↓
Validation
     ↓
Agent performance memory
     ↓
Future context / warning
```

The Learning Agent should not silently rewrite the agent's instructions.

---

# 27. Repeated Trader Mistakes

The system should also detect user/trading-process patterns.

Examples:

- Repeated late entries
- Repeated FOMO
- Repeated trades immediately after losses
- Repeated stop widening
- Repeated premature exits
- Repeated trading outside strategy conditions

A recurring behavioral pattern can become a validated learning rule or warning.

---

# 28. Learning Rule Lifecycle

Learning should follow:

```text
Observed
   ↓
Logged
   ↓
Pattern Candidate
   ↓
Repeated Evidence
   ↓
Validated
   ↓
Recommendation
   ↓
Approved
   ↓
Active Learning Rule
   ↓
Measured Again
```

One observation is not enough to create a permanent rule.

---

# 29. Agent Communication Model

Agents should communicate through structured messages.

Conceptually:

```text
Agent A
   ↓
Message Contract
   ↓
Agent B
   ↓
Validated Response
```

Messages should include:

- Sender
- Recipient
- Timestamp
- Workflow ID
- Message type
- Schema version
- Payload
- Confidence where relevant
- Evidence references

---

# 30. Allowed Communication

The Orchestrator should generally control agent invocation.

Direct unrestricted agent-to-agent communication should be avoided.

Preferred:

```text
Agent A
  ↓
Orchestrator
  ↓
Agent B
```

rather than:

```text
Agent A
  ↔
Agent B
  ↔
Agent C
  ↔
Agent A
```

This reduces loops and makes workflows auditable.

---

# 31. Agent Loop Protection

Every workflow must have:

- Maximum iterations
- Maximum runtime
- Maximum retries
- Termination condition

Repeated or circular communication should trigger termination.

---

# 32. Agent Context Management

Context should be assembled dynamically.

```text
Agent Task
    ↓
Context Requirements
    ↓
Relevant Current State
    +
Relevant Memory
    +
Relevant Documents
    +
Relevant Market Data
    ↓
Compact Context
```

The agent should not automatically receive the entire project context.

---

# 33. Token Budgeting

Each agent should have an expected token budget.

The system should track:

- Input tokens
- Output tokens
- Calls
- Latency
- Estimated cost
- Cache utilization

Agents exceeding normal usage should be investigated.

---

# 34. Model Selection

Different agents may use different models.

A simple task should not require the most expensive reasoning model.

Potential mapping:

```text
Deterministic Calculation → Python
Simple Classification      → Small Model / Rules
Research Synthesis         → Reasoning Model
Complex Strategy Review    → Strong Reasoning Model
Risk Calculation           → Deterministic Engine
Explanation                → Appropriate Language Model
```

Model selection should be configuration-driven.

---

# 35. Agent Failure Behavior

If an agent fails:

```text
Agent Failure
     ↓
Record Failure
     ↓
Retry if permitted
     ↓
Fallback if defined
     ↓
Continue only if safe
     ↓
Otherwise Reject / Escalate
```

A failed intelligence agent may sometimes result in `REQUIRES_REVIEW`.

A failed Risk component must prevent new execution.

---

# 36. Agent Timeouts

Every agent must have a timeout.

Long-running agents must not block the entire trading workflow indefinitely.

Timeouts should be configurable by agent class.

---

# 37. Agent Retries

Retries must be bounded.

Not every failure should be retried.

Examples:

- Temporary network error → potentially retry.
- Invalid model output → bounded retry.
- Risk engine failure → do not blindly retry into execution.
- Broker uncertainty → reconcile before retrying.

---

# 38. Structured Output Validation

Agent outputs must be validated before being consumed.

For example:

```text
LLM Output
    ↓
Schema Validation
    ↓
Semantic Validation
    ↓
Consumer
```

Malformed output must not silently enter the trading workflow.

---

# 39. Agent Prompt Governance

Prompts and system instructions that materially affect agent behavior should be:

- Versioned
- Reviewed
- Stored appropriately
- Testable
- Associated with agent versions

Prompt changes can change trading behavior and should therefore be treated as meaningful software changes.

---

# 40. Agent Security

Agents should never receive raw credentials.

For example:

```text
Execution Agent
      ↓
Broker Interface
      ↓
Credential Service
      ↓
Broker
```

rather than:

```text
LLM
 ↓
Raw API Secret
```

---

# 41. Agent Observability

Track:

- Agent calls
- Latency
- Success/failure
- Token usage
- Output validation
- Workflow ID
- Agent version
- Model version
- Cost
- Escalations

---

# 42. Agent Audit Trail

For important decisions, retain:

- Agent ID
- Agent version
- Model
- Prompt/instruction version where appropriate
- Input references
- Output
- Timestamp
- Workflow ID
- Downstream decision

Sensitive information must be excluded or protected.

---

# 43. Agent Testing

Agents require multiple testing approaches.

### Contract Tests

Verify input/output schemas.

### Scenario Tests

Provide known situations and expected behavior.

### Regression Tests

Ensure changes do not unexpectedly alter established behavior.

### Safety Tests

Verify the agent cannot perform forbidden actions.

### Evaluation Tests

Measure analytical quality.

---

# 44. Agent Evaluation

Agent quality should not be measured only by whether a trade made money.

Evaluate:

- Analytical accuracy
- Calibration
- Consistency
- Evidence quality
- False positives
- False negatives
- Appropriate abstention
- Risk-rule compliance
- Latency
- Cost

---

# 45. Agent Abstention

Agents should be allowed to say:

```text
INSUFFICIENT_DATA
UNCERTAIN
REQUIRES_REVIEW
```

Abstention is preferable to fabricated confidence.

---

# 46. Confidence Is Not Authority

An agent may output:

```text
confidence = 0.95
```

and still be rejected by Risk.

Confidence informs analysis.

It does not grant permission.

---

# 47. Agent Consensus

TradeOS should not assume that majority agent agreement means a trade is safe.

For example:

```text
Technical → BUY
Fundamental → BUY
News → BUY
Prediction → BUY
Critic → CONCERN
Risk → REJECT
```

Final result:

```text
REJECT
```

Risk authority remains independent of agent consensus.

---

# 48. Agent Disagreement

Disagreement is valuable information.

The system should record:

- Which agents disagreed
- Why
- Evidence
- Confidence
- Final resolution

Repeated disagreement patterns can become learning signals.

---

# 49. Agent Registry

The Agent Registry should contain:

```text
agent_id
name
version
category
capabilities
permissions
tools
memory_access
model
token_budget
timeout
status
```

The Orchestrator uses the registry to determine which agents can perform a task.

---

# 50. Agent Capability Discovery

Agents should declare capabilities rather than requiring hard-coded knowledge of every agent.

Example:

```text
Capability:
"technical_analysis"

Available Agent:
technical_analysis.v1
```

This allows replacement and versioning.

---

# 51. Agent Versioning

Agent versions must change when behavior materially changes.

Example:

```text
technical_analysis.v1.0.0
technical_analysis.v1.1.0
technical_analysis.v2.0.0
```

Important decisions should record the agent version used.

---

# 52. Agent Promotion

New agents should follow:

```text
Prototype
 ↓
Evaluation
 ↓
Safety Testing
 ↓
Paper Environment
 ↓
Validation
 ↓
Production Candidate
 ↓
Approved
```

No experimental agent should automatically receive live execution privileges.

---

# 53. Agent Degradation

If an agent's measured performance deteriorates materially, TradeOS should be able to:

- Flag it
- Reduce reliance
- Route work elsewhere
- Disable it
- Require review

The system should not hide degraded performance.

---

# 54. Agent Learning Boundaries

Learning may improve:

- Context
- Warnings
- Recommendations
- Agent selection
- Model selection
- Research priorities

Learning may not independently:

- Increase risk
- Disable safeguards
- Enable live trading
- Rewrite global rules
- Delete evidence
- Deploy unvalidated behavior

---

# 55. Emergency Behavior

If a critical safety issue occurs:

```text
Any Critical Component
        ↓
Emergency Signal
        ↓
Orchestrator
        ↓
Risk / Safety Layer
        ↓
STOP NEW TRADING
```

Safety signals must not depend on an LLM agreeing with them.

---

# 56. Agent Architecture Invariants

The following must always remain true:

1. Agents have bounded responsibilities.
2. Agents use least privilege.
3. Risk has hard veto authority.
4. Execution requires authorization.
5. Agents cannot modify immutable safety rules.
6. Agent communication is bounded.
7. Agent outputs are schema-validated.
8. Agent failures fail safely.
9. Agent versions are auditable.
10. Learning cannot silently self-deploy.

---

# 57. Example: Complete Trade Workflow

```text
Market Data Agent
      ↓
Market Research Agent
      ↓
Technical Agent
      ↓
Fundamental Agent (if applicable)
      ↓
News Agent
      ↓
Strategy Agent
      ↓
Prediction Agent
      ↓
Critic Agent
      ↓
Portfolio Agent
      ↓
Deterministic Risk Engine
      ↓
Risk Agent
      ↓
Human Approval if Required
      ↓
Execution Agent
      ↓
Broker
      ↓
Trade Journal
      ↓
Learning Agent
      ↓
Coach Agent
```

The Orchestrator coordinates this workflow.

---

# 58. Example: Risk Rejection

```text
Strategy
   ↓
"BUY XYZ"
   ↓
Prediction
   ↓
"High probability"
   ↓
Critic
   ↓
"Acceptable"
   ↓
Portfolio
   ↓
"Exposure acceptable"
   ↓
Risk Engine
   ↓
"Daily loss limit reached"
   ↓
REJECT
```

No agent may override the Risk result.

---

# 59. Example: Repeated Mistake

```text
Trade 1 → Late Entry
Trade 5 → Late Entry
Trade 11 → Late Entry
Trade 16 → Late Entry
        ↓
Pattern Detection
        ↓
Recurring Behavior Identified
        ↓
Evidence Review
        ↓
Validated Learning Pattern
        ↓
Future Trade Proposal
        ↓
"Late-entry risk detected"
        ↓
Critic / Coach / User Review
        ↓
Outcome Measured
```

This creates a closed learning loop.

---

# 60. Example: Agent Overconfidence

```text
Prediction Agent
       ↓
High confidence forecasts
       ↓
Actual outcomes
       ↓
Calibration analysis
       ↓
Repeated overconfidence
       ↓
Agent performance pattern
       ↓
Learning recommendation
       ↓
Future prediction context
```

The model is not automatically retrained or replaced without governance.

---

# 61. Agent Architecture Success Criteria

The agent architecture is successful when:

- Every agent has a clear purpose.
- No agent has unnecessary authority.
- Risk cannot be bypassed.
- Execution is isolated.
- Agent communication is bounded.
- Context is minimized.
- Outputs are structured.
- Failures are safe.
- Performance is measurable.
- Repeated mistakes are learnable.
- Agent weaknesses are measurable.
- Learning is governed.
- New agents can be added without redesigning the system.

---

# 62. Related Documents

- `README.md`
- `rules.md`
- `docs/01_PROJECT_VISION.md`
- `docs/02_DESIGN_PRINCIPLES.md`
- `docs/03_ENGINEERING_PRINCIPLES.md`
- `docs/04_SYSTEM_ARCHITECTURE.md`
- `docs/06_DATA_ARCHITECTURE.md`
- `docs/07_TRADING_WORKFLOWS.md`
- `docs/08_RISK_MANAGEMENT.md`
- `docs/09_PREDICTION_ENGINE.md`
- `docs/10_LEARNING_SYSTEM.md`
- `docs/20_AGENT_CONTRACTS.md`
- `docs/21_CONFIGURATION.md`

---

## Version History

| Version | Status | Description |
|---|---|---|
| 0.1.0 | Architecture Baseline | Initial agent architecture, governance, communication, memory, and learning design |

---

> **Agent principle: specialize intelligence, restrict authority, validate outputs, learn from behavior, and never allow intelligence to bypass safety.**
