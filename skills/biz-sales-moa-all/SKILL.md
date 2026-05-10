---
name: biz-sales-moa-all
description: "BIZ/SALES MOA All — Full parallel analysis with all 12 business/sales agents. Always utilizes all 12 agents regardless of problem type. Maximum perspective coverage using MoA (Mixture of Agents) pattern."
trigger: manual
tags:
  - sales
  - moa
  - multi-agent
  - business-strategy
  - full-analysis
  - 12-agents
---

# BIZ/SALES MOA All Protocol

**Full parallel execution** of all 12 BIZ/SALES specialized agents — always utilizes all 12 regardless of the problem.

---

## Full List of 12 Agents

| # | Agent | Core Domain |
|---|-------|------------|
| 1 | `biz-sales` | B2B sales/customer acquisition |
| 2 | `biz-strategy` | Business strategy/competitive advantage |
| 3 | `biz-gap-theory` | GAP analysis |
| 4 | `review-harsh-critic` | Critical review |
| 5 | `biz-aarrr-funnel` | AARRR funnel |
| 6 | `biz-plg` | PLG growth |
| 7 | `biz-growth-loop` | Growth loops |
| 8 | `biz-gtm` | Market entry |
| 9 | `biz-bmc` | Business model |
| 10 | `biz-flywheel` | Flywheel |
| 11 | `biz-ai-monetization` | AI monetization |
| 12 | `biz-unconscious-purchase` | Unconscious purchase |

---

## Parallel Execution (all 12 simultaneously)

```
Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-sales (B2B sales/customer acquisition).
Analyze only from the biz-sales perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-strategy (business strategy/competitive advantage).
Analyze only from the biz-strategy perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-gap-theory (GAP analysis).
Analyze only from the GAP perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in review-harsh-critic (critical review).
Analyze only from the critical perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-aarrr-funnel (AARRR funnel).
Analyze only from the AARRR perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-plg (PLG growth).
Analyze only from the PLG perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-growth-loop (growth loops).
Analyze only from the Growth Loop perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-gtm (market entry).
Analyze only from the GTM perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-bmc (business model).
Analyze only from the BMC perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-flywheel (flywheel).
Analyze only from the Flywheel perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-ai-monetization (AI monetization).
Analyze only from the AI Monetization perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")

Task(subagent_type="general-purpose", run_in_background=True,
  prompt="You are an expert in biz-unconscious-purchase (unconscious purchase).
Analyze only from the unconscious purchase perspective. Completely ignore other perspectives.

{problem}

Response format:
### Key Findings (3+, with specific evidence)
### Most Critical Single Risk
### Immediate Recommendations")
```

---

## Integrated Synthesis (after collecting all 12 results)

1. **Cross blind spots**: Items flagged by 3+ agents simultaneously
2. **Tradeoffs**: Conflicts between frameworks stated explicitly
3. **Top action items**: 3 things you can do today
4. **6-month pivot signals**: Success conditions by metric

---

## Output Format

```
### Analysis Agents: 12 (full)
### Problem: {user_problem}

---
### Cross Blind Spots (flagged by 3+ agents simultaneously)
...

### Integrated Recommendations
...

### Tradeoffs
...

### Top 3 Action Items (today)
1. ...
2. ...
3. ...

### 6-Month Pivot Signals
- When [metric] achieved → [next step]
```

---

## Documentation Obligation (MANDATORY)

After pipeline execution, **agent responses and final conclusions must be saved as a document**. Skipping documentation means the pipeline is considered **incomplete**.

### Saving Rules

1. **Save path**: `docs/research/[YYYYMMDD]-[topic-summary].md` (project docs folder)
2. **Save timing**: **Immediately before** returning the final answer to the user
3. **DOC_INDEX.md update**: Register in the `docs/DOC_INDEX.md` top table after saving
4. **Content to save**:

```markdown
# [biz-sales-moa-all] {Topic Summary}
**Date**: {YYYY-MM-DD}  **Skill**: biz-sales-moa-all

## Original Problem
{problem}

## 12 Agent Response Summary
{Key findings + risks + recommendations summary for each agent}

## Cross Blind Spots (flagged by 3+ agents simultaneously)
{Item list}

## Final Conclusion
{Integrated recommendations + Top 3 action items + tradeoffs + 6-month pivot signals}
```
