---
name: trace
description: "Show chronological agent flow trace — hooks, keywords, skills, agents, tools, and mode transitions for the current session. Use when debugging unexpected behavior or understanding how a workflow executed."
---

# Agent Flow Trace

## Use When
- Debugging unexpected behavior: "why did X skill activate?", "what triggered that hook?"
- Post-session review: understand what agents and tools were used and in what order
- Performance analysis: find bottlenecks in tool or agent execution times
- User says "trace", "show trace", "what happened?", "debug the flow"

## Do Not Use When
- You want session MEMORY (episodes) — use `omc-episode-memory` instead
- You want usage statistics across multiple sessions — use `omc-learn-about-omc`

---

[TRACE MODE ACTIVATED]

## Objective

Display the flow trace showing how hooks, keywords, skills, agents, and tools interacted during this session.

## Instructions

### Primary path (MCP tools available)

1. **Use `trace_timeline` MCP tool** to show the chronological event timeline
   - Call with no arguments to show the latest session
   - Use `filter` parameter to focus on specific event types (hooks, skills, agents, keywords, tools, modes)
   - Use `last` parameter to limit output

2. **Use `trace_summary` MCP tool** to show aggregate statistics
   - Hook fire counts, keywords detected, skills activated, mode transitions
   - Tool performance and bottlenecks

### Fallback path (MCP tools NOT installed)

When `trace_timeline` / `trace_summary` are unavailable, reconstruct from session context:

1. Scan current conversation for log lines: `[SKILL ROUTER]`, `[DISPATCH]`, `[WAVE1]`, `[DOMAIN ORACLE]`, `[CHECKPOINT]`
2. `cat .omc/live-progress.log` for score trajectory (if exists)
3. `git log --oneline | head -20` for checkpoint commits as proxy timeline
4. Scan `.omc/episodes.jsonl` for outcome sequence

Report: `[TRACE FALLBACK] trace_timeline not available — reconstructing from session logs`

## Output Format

Present the timeline first, then the summary. Highlight:
- **Mode transitions** (how execution modes changed)
- **Bottlenecks** (slow tools or agents)
- **Flow patterns** (keyword → skill → agent chains)
- **Score trajectory** (if live-progress.log exists)
