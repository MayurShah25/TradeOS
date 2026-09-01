# TradeOS Agent Architecture

**Document:** `05_AGENT_ARCHITECTURE.md`  
**Version:** 0.2.0  
**Status:** Architecture Baseline  
**Scope:** Agent roles, authority, contracts, context, communication, memory, governance, learning, and runtime behavior

---

## 1. Purpose

This document defines the architecture and governance of the TradeOS agent ecosystem.

TradeOS does not use one general-purpose AI agent to perform all trading functions. Instead, it uses specialized agents with clearly bounded responsibilities.

The fundamental rule is:

> **Agents provide intelligence and services; system governance determines authority.**

The second architectural rule is:

> **Not every intelligent component is an authority, and not every system component should be an agent. Deterministic work belongs to deterministic services/engines; reasoning belongs to bounded agents; authority belongs to governed control boundaries.**

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

Agents should be specialized, replaceable, testable, observable, versioned, context-efficient, and failure-aware.

Deterministic calculations, state management, reconciliation, safety-critical validation, and enforcement should use deterministic services or engines where appropriate.

---

# 3. Agent Categories

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

Challenge, review, and provide contextual governance.

- Critic Agent
- Portfolio Agent
- Risk Review Agent

## 3.3 Operational / Learning Agents

Coordinate, learn, and explain system behavior.

- Orchestrator Agent
- Learning Agent
- Coach Agent

Deterministic components such as Market Data Service, Risk Engine, Risk Gate, Execution Service/OMS, and reconciliation services are services/engines, not AI agents.

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
     MARKET DATA          INTELLIGENCE         RESEARCH
       SERVICE                 │                  │
                               ▼                  │
          ┌───────────┬───────┼────────┬─────────┘
          ▼           ▼       ▼        ▼
      Technical   Fundamental News   Strategy
          │           │       │        │
          └───────────┴───────┼────────┘
                              ▼
                         Prediction
                              │
                              ▼
                           CRITIC
                              │
                              ▼
                          PORTFOLIO
                              │
                              ▼
                    DETERMINISTIC RISK ENGINE
                              │
                              ▼
                       RISK REVIEW AGENT
                              │
                              ▼
                          RISK GATE
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 REJECT              APPROVE
                                        │
                                        ▼
                              EXECUTION SERVICE
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

The Risk Engine, Risk Gate, and Execution Service are deterministic control boundaries. They are not replaced by LLM reasoning.

---

# 5. Agent Authority Model

Every agent has an explicit authority level.

```text
L0 — Observe
L1 — Analyze
L2 — Recommend
L3 — Govern / Review
L4 — Execute through an explicitly authorized execution boundary
```

| Component | Type | Authority |
|---|---|---|
| Market Data Service | Deterministic service | Data authority only |
| Market Data Agent | Agent | L0/L1 |
| Research | Agent | L1/L2 |
| Technical | Agent | L1/L2 |
| Fundamental | Agent | L1/L2 |
| News/Sentiment | Agent | L1/L2 |
| Strategy | Agent | L2 |
| Prediction | Agent | L1/L2 |
| Critic | Agent | L2 |
| Portfolio | Agent | L2/L3 |
| Risk Engine | Deterministic engine | Hard numerical control |
| Risk Review Agent | Agent | L3 |
| Risk Gate | Deterministic boundary | Execution enforcement |
| Execution Service | Deterministic service | Authorized execution |
| Learning | Agent | L1/L2 |
| Coach | Agent | L1/L2 |
| Orchestrator | Agent/service boundary | Workflow coordination |

**Execution authority is isolated from analytical authority.** An agent authority level never permits bypassing a higher-priority deterministic safety boundary.

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

Deterministic services and engines must have equivalent versioned contracts appropriate to their responsibilities.

---

# 7. Agent Lifecycle

Agents follow:

```text
REGISTERED → INITIALIZED → READY → RUNNING → COMPLETED
```

Failure states may include `TIMEOUT`, `FAILED`, `CANCELLED`, `DEGRADED`, and `DISABLED`.

An unhealthy agent must not silently continue producing trusted outputs.

---

# 8. Orchestrator Agent

Coordinates TradeOS workflows, invokes agents/services, passes structured context, manages state, enforces iteration and timeout limits, terminates workflows, and records outcomes.

Forbidden:

- Bypassing Risk
- Direct unauthorized execution
- Modifying immutable safety rules
- Increasing autonomy
- Granting unrestricted agent access

---

# 9. Market Data Service / Agent Boundary

Deterministic ingestion, normalization, freshness checks, validation, and market-state handling belong to the Market Data Service/Gateway.

An optional Market Data Agent may interpret data quality or research context.

It cannot authorize trades or modify strategy rules.

---

# 10. Market Research Agent

Analyzes broader market conditions and identifies research opportunities. It cannot execute, override Risk, or silently modify live strategies.

# 11. Technical Analysis Agent

Analyzes price, volume, volatility, and technical structure. Indicators are evidence, not guarantees.

# 12. Fundamental Analysis Agent

Evaluates fundamental information where applicable. It may be inactive for assets where conventional fundamentals are inappropriate.

# 13. News & Sentiment Agent

Evaluates relevant news and sentiment. External headlines are untrusted input until validated.

# 14. Market Regime Agent

Identifies market conditions such as trending, range-bound, high-volatility, low-volatility, breakout, mean-reversion, or uncertain regimes. Regime information may influence strategy selection but cannot override Risk.

# 15. Strategy Agent

Evaluates defined strategy rules and generates structured Trade Proposals containing entry, invalidation, target concept, thesis, evidence, and required confirmations.

It cannot execute, override Risk, widen stops to avoid losses, or deploy an unvalidated strategy.

# 16. Prediction Agent

Produces probabilistic forecasts or scenarios and reports uncertainty. Predictions are estimates, not guarantees, and cannot authorize execution.

# 17. Critic Agent

Acts as an adversarial reviewer, searching for contradictory evidence, missing confirmation, overconfidence, regime mismatch, poor reward/risk, data-quality issues, and overfitting.

Outputs may include:

```text
CRITIC_PASS
CRITIC_CONCERN
CRITIC_REJECT
```

It cannot force execution or override hard Risk controls.

# 18. Portfolio Agent

Evaluates a proposed trade against existing exposure, correlations, margin, leverage, concentration, and strategy exposure. It may recommend rejection or reduction but cannot override hard Risk limits.

---

# 19. Risk Review Agent

## Purpose

Provide contextual risk governance and explain risk decisions.

## Responsibilities

- Review proposed risk
- Review portfolio exposure
- Evaluate event, regime, liquidity, and stress concerns
- Evaluate drawdown and daily-loss context
- Recommend rejection, reduction, escalation, or review
- Explain the risk decision

## Authority

**L3 — Governance / Review**

The Risk Review Agent is not the sole numerical risk calculator. It cannot weaken a hard Risk Engine constraint, independently invent a trade, or convert a failed hard constraint into approval.

Forbidden:

- Increasing permitted risk without authorized configuration
- Disabling safety limits
- Enabling live trading
- Modifying immutable global rules
- Overturning a hard Risk Engine rejection
- Independently authorizing a trade

---

# 20. Deterministic Risk Engine

The Deterministic Risk Engine is authoritative for hard numerical constraints including risk per trade, position sizing, maximum monetary risk, daily loss, drawdown, portfolio exposure, leverage, margin, concentration, and other deterministic safety limits.

```text
Trade Proposal
      ↓
Deterministic Risk Engine
      ↓
Risk Review Agent
      ↓
Risk Gate
```

If the Risk Engine rejects a trade, no agent may overturn that rejection.

Risk Engine outputs must be deterministic, reproducible, versioned, and auditable.

---

# 21. Risk Gate

The Risk Gate is the deterministic enforcement boundary between risk governance and execution.

It is not an LLM decision-maker.

It produces an explicit state such as:

```text
APPROVED
REJECTED
REQUIRES_REVIEW
```

Only `APPROVED` may proceed to the execution boundary. A hard Risk Engine rejection cannot be converted to approval downstream.

---

# 22. Execution Service / Execution Agent Boundary

Deterministic order validation, idempotency, broker-state tracking, fill verification, and reconciliation belong to the Execution Service/OMS.

An Execution Agent may assist with bounded operational reasoning, but it cannot bypass deterministic execution controls.

TradeOS distinguishes:

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

Never assume an order filled. If broker state is ambiguous, mark it `UNKNOWN`, reconcile, and do not blindly resubmit.

---

# 23. Learning Agent

Analyzes outcomes and identifies opportunities for improvement.

It should compare expected versus actual outcomes, detect individual and repeated mistakes, evaluate strategies and agents, evaluate prediction calibration, and generate learning recommendations.

It cannot automatically modify immutable safety rules, increase risk, deploy unvalidated strategies, or delete unfavorable results.

# 24. Coach Agent

Turns system activity into understandable education, including trades, rejected trades, mistakes, expectations versus outcomes, and learning reports.

It cannot override Risk, execute trades, or independently change strategy rules.

# 25. Agent Memory

Agents have controlled memory access appropriate to their roles. Memory categories may include workflow, operational, trade/episodic, pattern, strategy, agent-performance, and learning memory.

# 26. Agent Performance Memory

TradeOS should measure agent performance using appropriate metrics such as signal precision, false-positive rate, prediction calibration, critic usefulness, and data-quality detection. Metrics must not encourage agents to game their scores.

# 27. Repeated Agent Mistakes

Agent behavior should be evaluated for recurring weaknesses. The Learning Agent may identify patterns and recommend future context, additional review, or validated intervention. It must not silently rewrite production instructions.

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
Validation
     ↓
Agent performance memory
     ↓
Future context / warning
```

# 28. Repeated Trader Mistakes

The system should detect recurring trading-process patterns such as late entries, FOMO, revenge trading, stop widening, premature exits, or trading outside strategy conditions.

A recurring behavioral pattern can become a validated learning rule or warning.

# 29. Learning Rule Lifecycle

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

# 30. Agent Communication Model

Agents communicate through structured messages containing, where applicable, sender, recipient, timestamp, workflow ID, message type, schema version, payload, confidence, and evidence references.

The preferred coordination pattern is orchestrated rather than unrestricted peer-to-peer communication.

# 31. Agent Loop Protection

Every workflow must have maximum iterations, maximum runtime, maximum retries, and a termination condition.

Repeated or circular communication must be detected and terminated.

**Infinite agent-to-agent loops are prohibited.**

# 32. Agent Context Management

Context should be assembled dynamically:

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

# 33. Reasoning Efficiency and Token Budgeting

Each agent should have an expected resource budget. The system may track input tokens, output tokens, calls, latency, estimated cost, and cache utilization.

However, the objective is not simply lower token usage.

> **TradeOS should learn to think more efficiently — selecting the right information, the right agent, the right amount of reasoning, and stopping unnecessary workflows early without sacrificing decision quality or safety.**

# 34. Model Selection

Different agents may use different models.

```text
Deterministic Calculation → Python / Engine
Simple Classification      → Rules / Small Model
Research Synthesis         → Appropriate Reasoning Model
Complex Strategy Review    → Strong Reasoning Model
Risk Calculation           → Deterministic Engine
Explanation                → Appropriate Language Model
```

Model selection should be configuration-driven.

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

A failed intelligence agent may sometimes result in `REQUIRES_REVIEW`. A failed Risk component must prevent new execution.

# 36. Agent Timeouts

Every agent must have a timeout. Long-running agents must not block the entire trading workflow indefinitely. Timeouts should be configurable by agent class.

# 37. Agent Retries

Retries must be bounded.

Examples:

- Temporary network error → potentially retry.
- Invalid model output → bounded retry.
- Risk engine failure → do not blindly retry into execution.
- Broker uncertainty → reconcile before retrying.

# 38. Structured Output Validation

Agent outputs must be validated before being consumed.

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

# 39. Agent Prompt Governance

Prompts and system instructions that materially affect agent behavior should be versioned, reviewed, stored appropriately, testable, and associated with agent versions.

Prompt changes can change trading behavior and should therefore be treated as meaningful software changes.

# 40. Agent Security

Agents should never receive raw credentials.

```text
Execution Service
      ↓
Broker Interface
      ↓
Credential Service
      ↓
Broker
```

Never expose raw API secrets to an LLM.

# 41. Agent Observability

Track, where appropriate:

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

# 45. Agent Abstention

Agents should be allowed to say:

```text
INSUFFICIENT_DATA
UNCERTAIN
REQUIRES_REVIEW
```

Abstention is preferable to fabricated confidence.

# 46. Confidence Is Not Authority

An agent may output:

```text
confidence = 0.95
```

and still be rejected by Risk.

Confidence informs analysis. It does not grant permission.

# 47. Agent Consensus

TradeOS should not assume that majority agent agreement means a trade is safe.

For example:

```text
Technical → BUY
Fundamental → BUY
News → BUY
Prediction → BUY
Critic → CONCERN
Risk Engine → REJECT
```

Final result:

```text
REJECT
```

Risk authority remains independent of agent consensus.

# 48. Agent Disagreement

Disagreement is valuable information.

The system should record:

- Which agents disagreed
- Why
- Evidence
- Confidence
- Final resolution

Repeated disagreement patterns can become learning signals.

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

# 51. Agent Versioning

Agent versions must change when behavior materially changes.

Example:

```text
technical_analysis.v1.0.0
technical_analysis.v1.1.0
technical_analysis.v2.0.0
```

Important decisions should record the agent version used.

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

# 53. Agent Degradation

If an agent's measured performance deteriorates materially, TradeOS should be able to:

- Flag it
- Reduce reliance
- Route work elsewhere
- Disable it
- Require review

The system should not hide degraded performance.

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

# 55. Emergency Behavior

If a critical safety issue occurs:

```text
Any Critical Component
        ↓
Emergency Signal
        ↓
Safety Layer
        ↓
STOP NEW TRADING
```

Safety signals must not depend on an LLM agreeing with them.

# 56. Agent Architecture Invariants

The following must always remain true:

1. Agents have bounded responsibilities.
2. Agents use least privilege.
3. Hard numerical risk constraints are enforced by the deterministic Risk Engine.
4. A hard Risk Engine rejection cannot be overturned.
5. Execution requires authorization through the Risk Gate.
6. Deterministic execution controls cannot be bypassed by an agent.
7. Agents cannot modify immutable safety rules.
8. Agent communication is bounded.
9. Agent outputs are schema-validated.
10. Agent failures fail safely.
11. Agent versions are auditable.
12. Learning cannot silently self-deploy.

# 57. Example: Complete Trade Workflow

```text
Market Data Service
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
Risk Review Agent
      ↓
Risk Gate
      ↓
Human Approval if Required
      ↓
Execution Service / OMS
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

This creates a governed closed learning loop.

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

# 61. Agent Architecture Success Criteria

The agent architecture is successful when:

- Every agent has a clear purpose.
- No agent has unnecessary authority.
- Hard Risk controls cannot be bypassed.
- Execution is isolated behind deterministic controls.
- Agent communication is bounded.
- Context is minimized without sacrificing required information.
- Outputs are structured.
- Failures are safe.
- Performance is measurable.
- Repeated mistakes are learnable.
- Agent weaknesses are measurable.
- Learning is governed.
- New agents can be added without redesigning the system.

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
| 0.2.0 | Architecture Baseline | Clarified agent/service boundaries, deterministic risk authority, Risk Gate enforcement, execution boundary, bounded communication, and reasoning efficiency |

---

> **Agent principle: specialize intelligence, restrict authority, validate outputs, learn from behavior, and never allow intelligence to bypass safety.**
