---
name: skill-router
description: "Routing SCAFFOLD — dispatches to specialist agents/skills. NOT an agent itself. Analyzes prompt, selects best 1-3 entries from agent/skill registry, runs in parallel. Use when domain is clear but agent selection is uncertain. (Note: slash command remains /ontolo-agent for backwards compatibility)"
---

<!-- CLASSIFICATION: skill (routing scaffold) — delegates all work to agents/skills, performs no domain work itself -->

# skill-router (ontolo-agent) — Smart Multi-Agent & Skill Dispatcher

Analyzes the user prompt and routes to the **best 1–3 specialist agents or skills** in parallel. Aggregates responses. If no match, researches and dynamically creates a new agent.

**Priority**: Specialized accuracy > Multi-angle analysis > Token efficiency

---

## Agent Registry

| agent_name | brief_description | category |
|---|---|---|
| biz-aarrr-funnel | AARRR Funnel, Pirate Metrics, startup growth KPIs, Acquisition→Referral stage analysis | biz |
| biz-ai-monetization | AI SaaS monetization, usage/outcome-based pricing, COGS, API vs subscription | biz |
| biz-b2b-first-customer | B2B SaaS early customer acquisition, follow-up email, BANT/MEDDIC/CHAMP lead qualification | biz |
| biz-bmc | Business Model Canvas 9 blocks, AI SaaS business model, VC pitch design | biz |
| biz-flywheel | Flywheel growth model, Amazon Flywheel, AI data network effects, competitive moat | biz |
| biz-framework-integrator | BS Framework TOP7 synthesis: AARRR+BMC+GTM+Growth+PLG+Flywheel+AI Monetization | biz |
| biz-gap-theory | GAP Theory v3, current state vs target state gap analysis | biz |
| biz-growth-loop | Growth Loop design, viral loops, data flywheel, content loops, loop velocity | biz |
| biz-gtm | Go-To-Market strategy, ICP definition, PLG/SLG/CLG/DLG, pricing strategy, AI SaaS market entry | biz |
| biz-plg | Product-Led Growth, Freemium design, Aha Moment, PQL, Free→Paid conversion | biz |
| biz-sales | B2B sales, enterprise sales cycles, MEDDIC/MEDDPICC, objection handling, pipeline | biz |
| biz-strategy | Business strategy, Porter 5 Forces, Blue Ocean, Ansoff Matrix, competitive analysis | biz |
| biz-unconscious-purchase | Unconscious purchase induction, SPIKE model, behavioral economics, neuromarketing | biz |
| dev-architect | Strategic architecture advisory, READ-ONLY, debugging strategy, Opus | dev |
| dev-build-fixer | Build/compile error resolution, minimal changes, no architecture changes | dev |
| dev-code-simplifier | Code simplification, clarity/consistency/maintainability improvement | dev |
| dev-deep-executor | Complex goal-oriented autonomous work, Opus | dev |
| dev-designer | UI/UX designer-developer, high-quality interface implementation, Sonnet | dev |
| dev-executor | Focused task execution, implementation, bug fixes, code changes, Sonnet | dev |
| dev-git-master | Git expert, atomic commits, rebase, history management | dev |
| dev-writer | Technical documentation, README, API docs, code comments, Haiku | dev |
| ops-debugger | Error analysis, exception debugging, stack trace, root cause, test failure diagnosis | ops |
| ops-ml-training | ML training scripts, DDP safety, memory management, checkpointing, WandB, ASI project | ops |
| ops-orchestrator | Multi-agent pipeline coordination, pre-merge quality validation, parallel review | ops |
| ops-planner | Strategic planning consultant, interview workflow, Opus | ops |
| qa-expert | Comprehensive QA, Quality Gates, pre-deployment validation, TypeScript+Lint+Build+E2E | qa |
| qa-pw-generator | Playwright TypeScript test generator, spec → executable .spec.ts | qa |
| qa-pw-healer | Playwright test failure healer, diagnosis/fix, selector/timing updates | qa |
| qa-pw-planner | Playwright test planner, live app exploration, structured test plan | qa |
| qa-test-coverage | Test coverage gap analysis, missing tests, untested branches, edge cases | qa |
| qa-test-engineer | Test strategy, integration/E2E coverage, flaky test hardening, TDD workflows | qa |
| qa-tester | Interactive CLI testing, tmux session management | qa |
| test-validator | Fast regression test runner (<5min), unit tests, change impact analysis | qa |
| research-analyst | Pre-planning requirements analysis, Opus | research |
| research-deep-analyst | Deep research, hypothesis generation, multi-angle analysis, domain-adaptive | research |
| research-doc-specialist | External documentation and reference specialist | research |
| research-explore | Codebase exploration, file search, code reading, investigation (Stream 1) | research |
| research-scientist | Data analysis and research execution | research |
| review-code | Code quality review, readability, maintainability | review |
| review-critic | Work plan review and critique, Opus | review |
| review-harsh-critic | Thorough review, gap analysis, multi-perspective investigation, Opus | review |
| review-intent | Implementation-intent consistency validation, checks if request was implemented | review |
| review-quality | Logic defects, maintainability, anti-patterns, SOLID principles | review |
| review-verifier | Deliverable inspection, quality check, PASS/FAIL verdict (Stream 4) | review |
| sec-code | Code security scan, auth/authz patterns, input validation, session management | sec |
| sec-data | DB security, schema, RLS policies, sensitive data handling | sec |
| sec-infra | Infrastructure security, Vercel/Supabase/Railway, env vars, API key management | sec |
| sec-reviewer | Security vulnerability scanner, OWASP Top 10, web app/API server | sec |
| korean-criminal-law-specialist | Korean criminal procedure, evidence law, Supreme Court precedents | specialist |

---

## Skill Registry

Skills are invoked via `Skill("skill-name")` directly (not via Task). omc-* skills excluded — handled by Claude Code autonomously.

| skill_name | brief_description | category |
|---|---|---|
| update-config | Configure Claude Code settings.json, hooks, permissions, env vars | config |
| keybindings-help | Customize keyboard shortcuts, ~/.claude/keybindings.json | config |
| commit | Git Commit Command | git |
| simplify | Review changed code for reuse, quality, efficiency, fix issues | dev |
| loop | Run a prompt/command on recurring interval | util |
| schedule | Create/manage scheduled remote agents on cron schedule | util |
| claude-api | Build apps with Claude API or Anthropic SDK | dev |
| code-index | Codebase semantic indexing with FAISS + sentence-transformers | dev |
| intent-clarifier | Intent Clarification — 5 Whys + JTBD + Golden Circle frameworks | analysis |
| expert-research | Lean Research Protocol — web-grounded multi-perspective analysis | research |
| expert-research-v2 | Fixed 3-Agent Research Pipeline — Deep Analyst + Devil's Advocate + Fact Finder | research |
| expert-questions | Expert Perspective Question Templates — Architect/QA/Security/Performance views | research |
| marl-5stage | MARL 5-Stage Pipeline — S1 Hypothesis→S2 Solver→S3 Auditor→S4 Verifier→S5 Refiner | quality |
| biz-synthesis | Multi-angle business analysis — biz-sales + biz-strategy + biz-gap-theory parallel | biz |
| bs-framework-synthesis | BS Framework dynamic orchestration — 7 frameworks auto-selected | biz |
| biz-sales-mda | 3-Round Multi-agent Debate — structured debate to derive insights | biz |
| biz-sales-moa | BIZ/SALES MOA — 12 business/sales agents, integrated synthesis | biz |
| biz-sales-moa-all | Full parallel analysis with all 12 business/sales agents | biz |
| codebase-memory-exploring | Codebase knowledge graph exploration — search_graph + get_architecture | code |
| codebase-memory-tracing | Call chain and dependency tracing — trace_call_path | code |
| codebase-memory-reference | Codebase-memory-mcp reference guide — MCP tools, graph queries, Cypher | code |
| codebase-memory-quality | Code quality analysis — dead code, complexity, refactor candidates | code |
| frontend-design | Create distinctive, production-grade frontend interfaces | dev |
| feature-dev | Guided feature development with codebase understanding | dev |
| superpowers:brainstorming | Explore user intent and requirements before implementation | dev |
| superpowers:writing-plans | Multi-step implementation plan from spec/requirements | dev |
| superpowers:executing-plans | Execute implementation plan with review checkpoints | dev |
| superpowers:subagent-driven-development | Execute plans with independent tasks in current session | dev |
| superpowers:dispatching-parallel-agents | 2+ independent tasks worked on without sequential dependencies | dev |
| superpowers:systematic-debugging | Debug any bug, test failure, or unexpected behavior | dev |
| superpowers:test-driven-development | TDD — write tests before implementation | dev |
| superpowers:requesting-code-review | Verify work meets requirements after feature completion | dev |
| superpowers:receiving-code-review | Process code review feedback with technical rigor | dev |
| superpowers:verification-before-completion | Verify before claiming work complete — evidence before assertions | dev |
| superpowers:finishing-a-development-branch | Complete development work — merge, PR, or cleanup options | dev |
| superpowers:using-git-worktrees | Isolated git worktrees for feature work | dev |
| superpowers:writing-skills | Create or edit Claude Code skills | dev |
| ralph-loop:ralph-loop | Start Ralph Loop in current session | util |
| ralph-loop:cancel-ralph | Cancel active Ralph Loop | util |
| ralph-loop:help | Explain Ralph Loop plugin and commands | util |

---

## Step 1: LLM Router — Select Optimal Agents/Skills

Analyze the Compact Registries above + user prompt to select the **best 1–3 entries**.

### Entry Count Decision

| Case | Count | Example |
|------|-------|---------|
| Single domain, clear specialty | 1 | "Git rebase" → dev-git-master |
| 2 domains or multi-angle needed | 2 | "Conversion rate" → biz-plg + biz-aarrr-funnel |
| Complex strategic question, 3 angles | 3 | "Business model redesign" → biz-strategy + biz-bmc + biz-gtm |

**Rule**: Never force multiple entries. 1 is enough for single-domain requests.

### Router System Prompt

```
You are an expert multi-agent dispatcher for a Claude Code multi-agent system.

Select the OPTIMAL 1-3 agents or skills for the user's request.
Each entry has a "type": "agent" (dispatched via Task) or "skill" (invoked via Skill tool directly).
Choose multiple entries only when they cover genuinely different angles (no overlapping capabilities).
Output ONLY valid JSON — no other text, no markdown fences, no explanation outside JSON.

## Agent Registry
{agent_registry_table}

## Skill Registry
{skill_registry_table}

## User Request
{user_prompt}

## Output
{
  "entries": [
    {
      "name": "<exact name from registry>",
      "type": "agent" | "skill",
      "confidence": <float 0.0-1.0>,
      "role": "<specific angle this entry covers — 1 sentence>"
    }
  ],
  "max_confidence": <highest confidence>,
  "reason": "<2-3 sentences: WHY these entries and their complementary angles>"
}
```

### Branch

- `max_confidence >= 0.65` → **Step 2A** (parallel dispatch)
- `max_confidence < 0.65` → **Step 2B** (dynamic agent creation)

---

## Step 2A: Parallel Dispatch + Aggregation

### 2A-1. Web Grounding Detection (orchestrator performs directly)

Match keywords (case-insensitive): `statistics`, `latest`, `current version`, `how many`, `benchmark`, `release date`, `recent`

- Exclude if referencing internal/local context (e.g., "in my current code")
- If detected: run WebSearch 1–2 times → inject as `## [WEB FACTS]` block into all agent prompts

### 2A-2. Parallel Dispatch (all in single response block)

**⚠️ Key Rule**: All entries dispatched **simultaneously in a single response block**. Sequential dispatch forbidden.

**For agents** (`type: "agent"`):
```
Task(
  subagent_type="{agent_name}",
  description="ontolo-agent: {agent_name} — {role}",
  run_in_background=true,
  prompt="""
## [ONTOLO-AGENT PARALLEL DISPATCH — Agent {n}/{total}]
Agent: {agent_name}
Role: {role}
Reason: {router_reason}

## [ANTI-HALLUCINATION PROTOCOL]
1. If uncertain: "No reliable information available on X" — never fabricate
2. Statistics/dates/version numbers: state "recommend verifying with official source" if unverified
3. Base on established domain knowledge

{## [WEB FACTS] block if web grounding triggered}

## [USER REQUEST]
{original_user_prompt}

## [RESPONSE FORMAT]
Start with: > **[{agent_name}] {role}**
Provide expert answer. (Focus only on your {role} angle. Minimize overlap with other agents.)
End with: > **Confidence**: HIGH / MEDIUM / LOW
"""
)
```

**For skills** (`type: "skill"`):
```
Skill("{skill_name}", args="{user_prompt}")
```
Skills are invoked directly by the orchestrator (not via Task). If multiple skills are selected, call them sequentially since Skill() is synchronous.

**Single entry**: `run_in_background=false` (or omit), receive result immediately.

### 2A-3. Aggregation (after all parallel Tasks complete)

```markdown
## Multi-Agent Analysis

> Participants: {agent_1} ({role_1}) | {agent_2} ({role_2})

---

### [{agent_1}] {role_1}
{agent_1 key content}

---

### [{agent_2}] {role_2}
{agent_2 key content}

---

## Synthesized Insights

{Core conclusions synthesizing all agent perspectives — written by orchestrator}
{Common ground across agents + areas of differing viewpoints}
```

**Single entry**: Skip aggregation section, output response directly.

---

## Step 2B: Dynamic Agent Creation (no suitable match)

When `max_confidence < 0.65`. Complete **within the same response** (do not defer to next turn).

### 1. Domain Research

```
WebSearch("{inferred domain} expert knowledge best practices 2026")
WebSearch("{inferred domain} specialized skills frameworks")
```

Extract up to 3 key facts + 1 source URL per search. If no results, use LLM general knowledge.

### 2. Create Agent File

Write `~/.claude/agents/{domain}-specialist.md`:

```yaml
---
name: {domain}-specialist
description: {domain} specialist. Deep expertise in {specific_area}. Auto-generated by ontolo-agent.
model: claude-sonnet-4-6
---

You are a {domain} specialist with deep expertise in {specific_area}.

## Domain Knowledge
{Key facts from WebSearch (omit this section if no results)}

## Anti-Hallucination Rules
- Never fabricate domain-specific facts, statistics, or references
- When uncertain: "I'd recommend verifying this with [specific source]"
- Base responses on established {domain} principles
```

### 3. Update Registry

Add new row to Agent Registry table in this SKILL.md:
`| {domain}-specialist | {brief_description} | {category} |`

### 4. Invoke in Current Session (via general-purpose)

Task agents registered as `.md` files are only available from the **next session**. For current session, use `general-purpose` and inject the specialist system prompt:

```
Task(
  subagent_type="general-purpose",
  description="ontolo-agent: {domain}-specialist (dynamic)",
  prompt="""
You are a {domain} specialist with deep expertise in {specific_area}.

## Domain Knowledge
{Key facts from WebSearch}

## Anti-Hallucination Rules
- Never fabricate domain-specific facts, statistics, or references
- When uncertain: state "recommend verifying with official source"

---

## [ONTOLO-AGENT DISPATCH]
...{same structure as Step 2A}...
"""
)
```

---

## Step 3: Post-Response Documentation (MANDATORY)

### 3-1. Determine Save Path

| Agent Category | Save Path |
|---|---|
| `dev` | `docs/research/ontolo-{agent}-{YYYYMMDD}.md` |
| `qa` | `docs/validation/ontolo-{agent}-{YYYYMMDD}.md` |
| `biz` | `docs/misc/ontolo-{agent}-{YYYYMMDD}.md` |
| `research` | `docs/research/ontolo-{agent}-{YYYYMMDD}.md` |
| `ops` | `docs/infrastructure/ontolo-{agent}-{YYYYMMDD}.md` |
| `review` / `sec` | `docs/misc/ontolo-{agent}-{YYYYMMDD}.md` |

Multiple agents: use highest-confidence agent for path. Filename: `ontolo-{agent1}+{agent2}-{YYYYMMDD}.md`

### 3-2. Document Content

```markdown
# ontolo-agent: {agents} — {YYYY-MM-DD}

**Request**: {one-line summary of user's original request}
**Selected**: {agent1} (confidence: {score1}) | {agent2} (confidence: {score2})
**Reason**: {router_reason}

## Key Answer Summary
{3–5 bullet points from synthesized insights}

## Applied Results / Changed Files
{list of changed files or "none"}

## Follow-up Tasks
{record if any, otherwise omit}
```

### 3-3. Update DOC_INDEX.md

Add one row to top of `docs/DOC_INDEX.md`:
```
| docs/{path}/ontolo-{agents}-{YYYYMMDD}.md | ontolo-agent {agents} synthesized analysis | {date} |
```

### 3-4. Dynamic Agent Creation — Additional Record

If Step 2B created a new agent, append to document:
```markdown
## Generated Agent
- File: ~/.claude/agents/{domain}-specialist.md
- Registry: Added to ontolo-agent SKILL.md Agent Registry
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Router outputs non-JSON text | Enforce "ONLY valid JSON — no other text" |
| Force 3 agents for every request | Single domain → 1 entry is enough, avoid duplicate angles |
| Sequential instead of parallel dispatch | All Tasks in **single response block** simultaneously |
| Web grounding triggered by internal context | Verify keyword refers to external world facts, not local code |
| Dynamic agent deferred to next turn | Step 2B must complete **within the same response** |
| Registry not updated after dynamic creation | Always add row to Agent Registry after creating new agent |
| Step 3 documentation skipped | **Always** save to docs/ + update DOC_INDEX after every ontolo-agent response |
| Skills dispatched via Task instead of Skill() | `type: "skill"` entries → use `Skill("name")` directly |
