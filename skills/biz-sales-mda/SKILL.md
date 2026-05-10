---
name: biz-sales-mda
description: "Use when user wants deep debate-driven insights on any topic. 3-Round Multi-agent Debate Architecture — user selects 3 agents from available pool, then runs 3 rounds of structured debate (independent analysis, cross-critique, final rebuttal + convergence) to derive robust insights."
---

# 3-Round MDA (Multi-agent Debate Architecture)

## When to Use MDA vs MOA vs MOA-all

| Scenario | Use |
|----------|-----|
| Need deep, focused debate between 3 specific expert perspectives | **biz-sales-mda** (this skill) |
| Need 12-agent synthesis across all business frameworks simultaneously | **biz-sales-moa** |
| Need exhaustive parallel analysis — all 12 agents at full depth | **biz-sales-moa-all** |

**Decision guide:**
- **MDA** — When you want to pick 3 agents and run 3 structured debate rounds (independent → cross-critique → rebuttal+convergence). Best for adversarial validation of a specific decision.
- **MOA** — When you want all 12 business agents to provide diverse perspectives in one pass, synthesized into a consensus. Best for broad strategic exploration.
- **MOA-all** — When you need every agent at full depth simultaneously. Highest token cost; use when exhaustive coverage matters more than speed.

**Core**: 3 rounds of structured debate with 3 user-selected agents → deep insight derivation.
**vs multi-round-debate**: 2R (independent + cross-critique) → 3R (independent + cross-critique + final rebuttal/convergence) extension.
**vs biz-sales-moa-all**: All 12 MoA parallel ≠ selected 3 deep debate.

---

## Step 0: Agent Selection — AskUserQuestion

Ask the user to select 3 agents. **Must use AskUserQuestion.**

### Agent Pool (by category)

**Business/Strategy:**
| ID | Agent | Core Perspective |
|----|-------|-----------------|
| 1 | `biz-sales` | B2B sales/customer acquisition/channels |
| 2 | `biz-strategy` | Business strategy/competitive advantage |
| 3 | `biz-gap-theory` | GAP analysis/current vs target |
| 4 | `biz-aarrr-funnel` | AARRR funnel/growth metrics |
| 5 | `biz-plg` | PLG/Aha Moment/conversion |
| 6 | `biz-growth-loop` | Self-reinforcing growth loops |
| 7 | `biz-gtm` | Market entry/ICP/channels |
| 8 | `biz-bmc` | Business Model Canvas 9 blocks |
| 9 | `biz-flywheel` | Flywheel/economies of scale/moat |
| 10 | `biz-ai-monetization` | AI monetization/pricing design |
| 11 | `biz-unconscious-purchase` | Unconscious purchase/behavioral economics |

**Technical/Analytical:**
| ID | Agent | Core Perspective |
|----|-------|-----------------|
| 12 | `dev-architect` | Software architecture/design |
| 13 | `research-scientist` | Data analysis/research execution |
| 14 | `research-analyst` | Requirements analysis/consulting |
| 15 | `review-critic` | Plan review/critique |
| 16 | `review-harsh-critic` | Harsh critique/weakness attack |
| 17 | `sec-reviewer` | Security vulnerabilities/OWASP |
| 18 | `review-quality` | Code quality/SOLID/anti-patterns |

**General Purpose:**
| ID | Agent | Core Perspective |
|----|-------|-----------------|
| 19 | `ops-planner` | Strategic planning/interviews |
| 20 | `dev-designer` | UI/UX design |
| 21 | `general-purpose` | General purpose (custom role assignable) |

### AskUserQuestion Execution

```
AskUserQuestion(
  questions=[
    {
      "question": "Please select 3 agents to participate in the 3-Round MDA.",
      "header": "Agent Selection",
      "multiSelect": true,
      "options": [
        // Dynamically select the 4 most relevant to the topic and present as options
        // e.g., business topic → biz-sales, biz-strategy, review-harsh-critic, biz-plg
        // e.g., technical topic → dev-architect, sec-reviewer, review-quality, research-scientist
      ]
    }
  ]
)
```

> **Option composition rule**: Analyze the topic and place the 4 most relevant in options. User selects 3 or specifies directly from the pool above via "Other".

---

## Step 1: Round 1 — Independent Analysis (3 parallel)

**Call all 3 simultaneously in a single response block** (sequential = serial = no debate effect)

```
Task(subagent_type="{agent_1}", run_in_background=True, description="R1 Independent Analysis",
  prompt="You are an expert in {agent_1_role}. Analyze independently without any knowledge of other agents' opinions.
Judge only from the {agent_1_role} perspective.

Topic: {topic}

Response format:
### Core Claims (3+, with specific evidence)
### Most Serious Risk/Weakness (1, explain why it's serious)
### Specific Improvement/Correction Suggestions (actionable level)")

Task(subagent_type="{agent_2}", ...)  // Same structure, agent_2_role
Task(subagent_type="{agent_3}", ...)  // Same structure, agent_3_role
```

---

## Step 2: Round 1 Results Collection + Cross-Comparison Table

Wait for all 3 Tasks to complete, then the orchestrator creates a comparison table:

```
| Item | Agent A | Agent B | Agent C |
|------|---------|---------|---------|
| Core Claims | ... | ... | ... |
| Top Risk | ... | ... | ... |
| Improvement Suggestions | ... | ... | ... |

Common flags: [mentioned by 2+ agents simultaneously]
Conflict points: [differing judgments]
```

> Show this comparison table to the user, then proceed to Round 2.

---

## Step 3: Round 2 — Cross-Critique (3 parallel)

Inject each agent with the other 2 agents' Round 1 results:

```
Task(subagent_type="{agent_1}", run_in_background=True, description="R2 Cross-Critique",
  prompt="You are an expert in {agent_1_role}.

[Your Round 1 Analysis]
{A_R1_result}

[Other Agents' Round 1 Analyses]
{agent_2_role}: {B_R1_result}
{agent_3_role}: {C_R1_result}

Instructions:
1. **1+ points of agreement** with other agents' analyses (with reasons)
2. **1+ rebuttals** — must be based on new evidence (simple repetition/emotional denial invalid)
3. **Update your R1 analysis** if corrections needed (if none, state 'maintained')
4. Commonly flagged items get elevated priority

Response format:
### Agreement (1+, with reasons)
### Rebuttal (1+, with new evidence)
### Updated Position (indicate changes from R1)")

Task(subagent_type="{agent_2}", ...)  // Inject A,C results to B
Task(subagent_type="{agent_3}", ...)  // Inject A,B results to C
```

> If Round 2 produces "agreement only" or evidence-free rebuttals → re-call that agent.

---

## Step 4: Round 3 — Final Rebuttal + Convergence (3 parallel)

Inject all Round 2 results for final position confirmation:

```
Task(subagent_type="{agent_1}", run_in_background=True, description="R3 Final Rebuttal",
  prompt="You are an expert in {agent_1_role}. This is the final round.

[Full Debate History]
--- Round 1 ---
You: {A_R1}
{agent_2_role}: {B_R1}
{agent_3_role}: {C_R1}

--- Round 2 ---
You: {A_R2}
{agent_2_role}: {B_R2}
{agent_3_role}: {C_R2}

Instructions:
1. **Final rebuttal or acceptance** of Round 2 rebuttals (with evidence)
2. **Final confirmed position** after 3 rounds of debate (change history summary)
3. One **key unresolved issue** (explain why it cannot be resolved)
4. **Final recommendation** on the topic (from your perspective)

Response format:
### Final Rebuttal/Acceptance
### Confirmed Position (R1→R2→R3 change history)
### Unresolved Issue (1)
### Final Recommendation")

Task(subagent_type="{agent_2}", ...)
Task(subagent_type="{agent_3}", ...)
```

---

## Step 5: Final Synthesis (Orchestrator)

Integrate all results from Round 1 + Round 2 + Round 3:

1. **Confirmed items** — Common conclusions maintained by 2+ agents through R3
2. **Convergence process** — Track position changes R1→R2→R3 (where convergence occurred)
3. **Tradeoffs that remained in conflict to the end** — Compare evidence strength
4. **Best conclusion + actionable recommendations**
5. **Residual uncertainty** — What could not be resolved even after 3 rounds of debate

---

## Step 6: Quality Self-Check

Before returning synthesis results:
- [ ] Were there actual position changes across all 3 rounds? (If not, debate was superficial)
- [ ] Were new arguments introduced in Round 3? (If R2 repeated, R3 was meaningless)
- [ ] Are all rebuttals based on new evidence?
- [ ] Are confirmed items + tradeoffs + residual uncertainty all included?
- [ ] Are there actionable recommendations?

If any is No → re-call synthesis agent.

---

## Output Format

```
## 3-Round MDA Results

### Topic: {topic}
### Participating Agents: {agent_1_role}, {agent_2_role}, {agent_3_role}
### Execution: R1 Independent Analysis → R2 Cross-Critique → R3 Final Rebuttal → Synthesis

---

### Confirmed Items (2+ agent consensus, maintained through R3)
- ...

### Convergence Process (position change tracking)
- [{agent_1}]: R1 "..." → R2 "..." → R3 "..." (reason for change: ...)
- [{agent_2}]: R1 → R2 maintained → R3 revised ...
- [{agent_3}]: ...

### Tradeoffs That Remained in Conflict to the End
- {agent_1} claims: ... (evidence: ...)
  vs {agent_2} claims: ... (evidence: ...)
  → Judgment: [evidence strength comparison]

### Best Conclusion + Actionable Recommendations
...

### Residual Uncertainty
...
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
# [biz-sales-mda] {Topic Summary}
**Date**: {YYYY-MM-DD}  **Skill**: biz-sales-mda

## Topic
{topic}

## Participating Agents
{agent_1_role}, {agent_2_role}, {agent_3_role}

## 3-Round Debate Summary
### Round 1: Independent Analysis
{Summary of each agent's core claims}

### Round 2: Cross-Critique
{Summary of agreements/rebuttals/position changes}

### Round 3: Final Rebuttal
{Confirmed positions + unresolved issues summary}

## Final Conclusion
{Confirmed items + convergence process + tradeoffs + actionable recommendations + residual uncertainty}
```
