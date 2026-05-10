---
name: biz-autopilot
description: "Autonomous business execution skill — orchestrates 8 business agents (researcher, marketer, content-writer, GTM, sales, B2B-first-customer, ops, framework-integrator) in structured cycles to achieve a business goal. Use when: 'run the business autonomously', 'execute business cycle', 'biz-autopilot'"
trigger: manual
tags:
  - business
  - autonomous
  - multi-agent
  - gtm
  - growth
---

# BIZ-AUTOPILOT — Autonomous Business Execution Protocol

Orchestrates the full business agent team to autonomously execute a business goal:
**Research → Strategy → Content → Execute → Measure → Loop**

Architecture:
```
biz-autopilot (orchestrator)
  ├── Phase 0: Context load (GoalTree + episodes)
  ├── Phase 1: PARALLEL — biz-researcher + biz-marketer
  ├── Phase 2: SEQUENTIAL — biz-content-writer (synthesizes Phase 1)
  ├── Phase 3: PARALLEL — biz-sales + biz-b2b-first-customer (outreach planning)
  ├── Phase 4: EXECUTE — orchestrator performs deliverables (post, send, etc.)
  ├── Phase 5: biz-ops (KPI review, GoalTree update)
  └── EVAL: outer goal achieved? → YES: done / NO: loop
```

---

## PRE-CYCLE: Load Context

### Step 1 — Load GoalTree

Read `.omc/goal-tree.json`. If missing, create:
```json
{
  "root_goal": "{user's business goal}",
  "level": 0,
  "sub_goals": [
    {"id": "sg1", "goal": "Research: validate ICP and channels", "status": "PENDING"},
    {"id": "sg2", "goal": "Strategy: define GTM motion and message frames", "status": "PENDING"},
    {"id": "sg3", "goal": "Content: produce ready-to-publish posts and DMs", "status": "PENDING"},
    {"id": "sg4", "goal": "Execute: publish to all target channels", "status": "PENDING"},
    {"id": "sg5", "goal": "Measure: collect user feedback (target threshold)", "status": "PENDING"}
  ],
  "reward_spec": {
    "primary_metric": "user feedback / signups / revenue",
    "threshold": "5+ real user interactions"
  },
  "history": []
}
```

### Step 2 — Load Episodes

Read `.omc/episodes.jsonl` (last 5 entries). Inject key lessons as context constraints into Phase 1+2 agents.

Report: "Cycle N/{max}. Past lessons: [summary]. Current goal: [root_goal]"

---

## PHASE 1: Parallel Intelligence Gathering

Run researcher + marketer **simultaneously** (background):

```
Task(subagent_type="biz-researcher", run_in_background=True,
  description="Market research and ICP validation",
  prompt="
## Business Goal
{root_goal}

## Past Lessons (apply these constraints)
{episode_lessons}

## Current GoalTree State
{goal_tree_json}

## Task
Research the target market for this business. Find:
1. Where does the ICP hang out online (specific subreddits, Discord servers, communities)?
2. What exact language do they use to describe their pain?
3. Who are the top 3 direct competitors and what are their weakest points (from user reviews)?
4. What channels have the lowest CAC for this ICP?
5. What would make the ICP immediately trust and try this product?

Output structured JSON as specified in your agent definition.")

Task(subagent_type="biz-marketer", run_in_background=True,
  description="Channel strategy and message frames",
  prompt="
## Business Goal
{root_goal}

## Past Lessons (apply these constraints)
{episode_lessons}

## Current GoalTree State
{goal_tree_json}

## Task
Design the go-to-market execution plan:
1. Prioritized channel list (top 3) with specific community names/links
2. 3 ICP persona frames (different hooks per segment)
3. Draft message frame for each channel (hook + pain + CTA structure)
4. Week 1 execution sequence (specific days, channels, post types)
5. Success KPIs for week 1 (specific numbers)

Output structured JSON as specified in your agent definition.")
```

Wait for both to complete. Collect: `researcher_output`, `marketer_output`.

---

## PHASE 2: Content Production

Sequential — content-writer synthesizes Phase 1:

```
Task(subagent_type="biz-content-writer",
  description="Produce final ready-to-publish content",
  prompt="
## Business Goal
{root_goal}

## Researcher Findings
{researcher_output}

## Marketer Strategy
{marketer_output}

## Task
Synthesize the above intelligence into final, ready-to-publish content:

1. For EACH channel in the marketer's priority list, produce a complete post
   - Use verbatim ICP language from researcher findings as hooks
   - Adapt format to platform (Reddit paragraphs, Discord casual, Korean community formal)
   - Include specific stats/numbers from researcher output

2. For the TOP channel, produce 3 DM templates targeting specific user types:
   - DM to someone who recently complained about the problem
   - DM to someone who asked 'is there a tool for this?'
   - DM to someone who shared a relevant article/resource

3. Produce a Korean + English version for any content targeting both audiences

Output structured JSON with ready_to_publish: true for all items.")
```

Collect: `content_output`

---

## PHASE 3: Outreach Plan

Parallel — sales + B2B first customer agent:

```
Task(subagent_type="biz-sales",
  description="Individual outreach prioritization",
  prompt="
## Business Goal
{root_goal}

## Researcher Channels
{researcher_output.recommended_channels}

## Content Ready
{content_output.dm_templates}

## Task
Design the 1-on-1 outreach execution plan:
1. List 5-10 specific types of users to reach out to first (most likely to engage/convert)
2. Prioritize by: pain intensity + platform accessibility + conversion likelihood
3. For each: platform, search query to find them, which DM template to use, follow-up timing
4. Define: what counts as a 'converted' beta user for this goal?")

Task(subagent_type="biz-b2b-first-customer",
  description="First customer acquisition strategy",
  prompt="
## Business Goal
{root_goal}

## ICP from Research
{researcher_output.icp_hypothesis}

## Task
Design the first 10 customer acquisition plan:
1. Where to find the first 10 customers (specific places, names)
2. What to offer them (beta access, personal help, exclusive features)
3. How to qualify them (BANT/CHAMP criteria for this product)
4. Email/DM sequence for first contact → follow-up → conversion
5. What feedback to collect from them (PMF signal questions)")
```

Collect: `sales_output`, `b2b_output`

---

## PHASE 4: Execute Deliverables

Orchestrator executes directly:

### 4-1. Save all content to project files

Save `content_output` to: `outreach_ready_v{N}.md`
```markdown
# Outreach Content — Cycle {N}
**Generated**: {date}
**Business Goal**: {root_goal}

## Channel Posts
{content_output.content_pieces formatted as markdown}

## DM Templates
{content_output.dm_templates formatted as markdown}

## Outreach Targets
{sales_output formatted as markdown}
```

### 4-2. Platform execution checklist

For each item in `content_output.content_pieces` where `ready_to_publish: true`:

**Web-accessible platforms** (Reddit, public forums):
- Use Playwright (mcp__playwright-session-*) if session is logged in
- Check `browser_tabs` first for idle sessions
- If NOT logged in → mark as "MANUAL_REQUIRED" and provide exact copy to paste

**Discord/Slack**:
- Check if session is logged in via `browser_snapshot`
- If logged in → navigate to channel → post
- If NOT logged in → STOP, ask user to log in, provide copy

**Rule**: NEVER auto-proceed when login is required.

### 4-3. Record execution results

```json
{
  "executed": [{"channel": "...", "status": "posted|manual_required|failed", "url": "..."}],
  "manual_required": [{"channel": "...", "reason": "...", "copy_ready": "..."}]
}
```

---

## PHASE 5: Operations Review

Run biz-ops to assess and update GoalTree:

```
Task(subagent_type="biz-ops",
  description="KPI review and GoalTree update",
  prompt="
## Business Goal
{root_goal}

## GoalTree Current State
{goal_tree_json}

## This Cycle's Execution Results
{execution_results}

## Researcher Insights
{researcher_output}

## Task
1. Update sub-goal statuses based on what was completed this cycle
2. Identify the #1 bottleneck (discovery/activation/retention/referral?)
3. Define success criteria for the NEXT cycle
4. Recommend: continue same approach OR pivot one element?
5. Output updated goal_tree_updates array and next_iteration_focus")
```

Apply `ops_output.goal_tree_updates` to `.omc/goal-tree.json`.

---

## POST-CYCLE: Evaluate and Decide

### Outer Goal Judgment

Evaluate against `reward_spec`:

```
JUDGMENT:
Root goal: {root_goal}
Threshold: {reward_spec.threshold}
Content executed: {execution_results.executed}
Manual required: {execution_results.manual_required}
Ops assessment: {ops_output.bottleneck}

Is the outer business goal achieved? Answer: YES / NO / UNCERTAIN
```

**YES** → Save episode (outcome=success), report completion:
```
BIZ-AUTOPILOT COMPLETE
Cycles: {N}
Goal: {root_goal}
Achieved: {threshold met evidence}
Files: outreach_ready_v{N}.md
```

**NO** → Check max iterations (default: 5):
- Under budget → append history to goal-tree → restart from Phase 1
- Over budget → save episode (outcome=partial) → generate handoff

**UNCERTAIN (or manual_required items exist)** → Present to user:
```
## BIZ-AUTOPILOT: Human Action Required

Posts ready but require manual submission:
{manual_required list with exact copy}

After posting, respond:
Y → continue cycle (collect feedback)
S → stop here, generate handoff
```

---

## EPISODE SAVE (every cycle)

Save to `.omc/episodes.jsonl`:
```json
{
  "ts": "{date}",
  "session": "{session_id}",
  "outcome": "success|partial|failure",
  "task": "{root_goal}",
  "lessons": ["{key insight from this cycle}"],
  "artifacts": ["{outreach_ready_v{N}.md}", "{goal-tree.json}"]
}
```

---

## HANDOFF REPORT (on forced stop)

```
## BIZ-AUTOPILOT Handoff Report
Goal: {root_goal}
Cycles completed: {N}/5
Status: {last_outcome}

Completed:
{completed sub-goals}

Remaining:
{pending sub-goals}

Bottleneck identified:
{ops_output.bottleneck}

Manual actions needed:
{manual_required items with copy}

Recommended next steps:
1. Complete manual posts listed above
2. Collect feedback from any early responses
3. Run /biz-autopilot again after 24h to process feedback

Resume: /biz-autopilot (loads goal-tree + episodes automatically)
```

---

## Configuration

Default limits (can override in `.omc/biz-autopilot-config.json`):
```json
{
  "max_cycles": 5,
  "parallel_phase1": true,
  "parallel_phase3": true,
  "auto_post_if_logged_in": true,
  "feedback_threshold": 5
}
```

---

## Agent Team Summary

| Agent | Role | Phase |
|-------|------|-------|
| biz-researcher | Market/ICP/competitor research | 1 |
| biz-marketer | Channel strategy + message frames | 1 |
| biz-content-writer | Final copy production | 2 |
| biz-sales | Individual outreach prioritization | 3 |
| biz-b2b-first-customer | First customer acquisition | 3 |
| biz-gtm | GTM motion validation (if needed) | 1/3 |
| biz-ops | KPI tracking + GoalTree updates | 5 |
| biz-framework-integrator | Full-stack synthesis (on pivot) | escalation |
