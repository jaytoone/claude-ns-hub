---
name: inhale
description: Universal knowledge absorption skill. Auto-detects input type (file, URL, concept, research category) and routes to the appropriate collection method, then outputs structured actionable insights.
---

<Purpose>
General-purpose knowledge absorption. Detects what the user gives as input,
routes to the right collection method, and always outputs structured actionable insights.

Supported input types:
- File path (local file: script, config, source code, doc) → read + analyze
- URL → fetch + analyze
- Research category keyword → RSS/arXiv pipeline (HarnessOS channels)
- Free-form concept/topic → codebase search + web search + synthesis
</Purpose>

<Use_When>
- User gives any input after /inhale — file, URL, category, or concept
- User wants to deeply understand something and get actionable takeaways
- User says "absorb X", "understand X", "what can I learn from X"
</Use_When>

<Steps>

## Step 1: Interpret Input

Read the argument and determine what it most likely is — no explicit rules needed.
Use judgment based on what makes sense given the input and context:

- No argument → research channel, default category `agent_research`
- Looks like a local file (script, config, source, doc) → Route A
- Looks like a web URL → Route B
- Matches one of the HarnessOS research categories below → Route C
- Anything else (concept, keyword, function name, topic) → Route D

**HarnessOS categories** (Route C triggers):
`agent_research`, `ml_engineering`, `product_growth`, `system_design`,
`daily_digest`, `trending_tools`, `ai_safety`

When ambiguous, pick the route that best serves the user's intent.
If a filename doesn't exist on disk, treat it as a concept (Route D).

## Step 2: Route to Collection Method

### Route A — File (local file path)

Resolve the path:
- Try as absolute path first
- Try relative to cwd (from env or current working directory)
- Try common locations: `~/.claude/hooks/`, `~/.claude/skills/`, cwd

Read the file with the Read tool. For large files (>500 lines), read in sections.

Then extract structure based on file type:
- `.sh` / `.bash` — extract: purpose, flow (control paths), key variables, external calls
- `.py` — extract: functions, classes, key logic, dependencies
- `.ts` / `.tsx` / `.js` — extract: components/functions, props/params, side effects, API calls
- `.md` — extract: sections, key claims, action items
- `.json` / `.yaml` — extract: schema, key fields, relationships
- `.sql` — extract: tables touched, operations, conditions
- Unknown → extract: structure, patterns, key identifiers

### Route B — URL

Use WebFetch to retrieve the page content.
Extract: title, main content, key claims, code snippets if any.

### Route C — Research Channel (HarnessOS pipeline)

Run existing pipeline:
```bash
python3 /home/jayone/Project/Entity/scripts/harness_updater.py \
  --auto-collect \
  --category {category} \
  --top {top_n|10} \
  --sort {sort|trending}
```
Read the generated digest from `docs/research/digests/{YYYYMMDD}-{category}.md`.

### Route D — Concept / Keyword

1. Search codebase for the concept:
   ```
   Grep(pattern=concept, path=cwd, output_mode="content", head_limit=30)
   ```
2. If relevant codebase hits → analyze usage patterns in code
3. If insufficient codebase hits → WebSearch for the concept (max 3 queries)
4. Synthesize findings from both sources

## Step 3: Analyze and Structure Insights

Regardless of route, produce a structured analysis with these sections:

### For Route A (File):
```
[INHALE — {filename} | {file_type}]

## What it does
{1-3 sentence purpose summary}

## Structure
{outline of key sections/functions/steps — numbered or bulleted}

## Key Logic / Control Flow
{the most important paths, conditions, decisions}
{for scripts: draw the main decision tree}

## Dependencies & Side Effects
{external tools called, files read/written, env vars used, APIs called}

## Actionable Insights
{what can be improved, extended, or reused — concrete suggestions}

## Suggested Next Actions
1. {most important action} — {why}
2. {second action} — {why}
3. {third action} — {why}
```

### For Route B (URL):
```
[INHALE — {url} | web]

## Source
{title} — {domain} | {date if available}

## Summary
{2-4 sentence summary of main content}

## Key Claims / Findings
- {claim 1}
- {claim 2}
...

## Actionable Insights
{how this applies to current work}

## Suggested Next Actions
1. ...
2. ...
```

### For Route C (Research Channel):
(Same format as original /inhale output — grouped by reflect_type)
```
[INHALE — {category} | research channels]
{N} items collected, {M} relevant (relevance >= 3.0)

## Actionable Insights
### By Type (stuck_agent / hypothesis_validation / skill_selection / evaluation / general)
- [{title}]({url}) — rel:{score}
  > {1-line takeaway}

## Suggested Next Actions
1. ...
```

### For Route D (Concept):
```
[INHALE — "{concept}" | codebase + web]

## In This Codebase
{what exists, where, how it's used — file:line references}

## External Context
{what the concept means broadly, key resources found}

## Gap Analysis
{what's missing, inconsistent, or could be improved}

## Suggested Next Actions
1. ...
```

## Step 4: Present Output

Output the structured analysis block directly in the response.

End with:
```
Absorbed: {input_type} → {source}
Next: "deep dive [aspect]" | "inhale [related_topic]" | "apply [suggestion N]"
```

</Steps>

<Examples>

## File absorption
```
User: /inhale stop-playwright-detect.sh
→ Route A: reads ~/.claude/hooks/stop-playwright-detect.sh
→ Outputs: purpose, flow diagram, key variables, actionable improvements
```

## URL absorption
```
User: /inhale https://example.com/article
→ Route B: fetches URL, extracts key claims
→ Outputs: summary, key findings, actionable insights
```

## Research channel (original behavior)
```
User: /inhale agent_research
→ Route C: runs harness_updater.py pipeline
→ Outputs: RSS/arXiv insights grouped by reflect_type
```

## Concept absorption
```
User: /inhale has_uncommitted_targets
→ Route D: greps codebase for usages, synthesizes understanding
→ Outputs: where it's used, what it does, gaps
```

## No argument
```
User: /inhale
→ Route C: defaults to agent_research category
```

</Examples>

<Integration>
| Skill/System | How |
|---|---|
| /live | SKILL ROUTER dispatches here for any "understand X" tasks |
| omc-autopilot | Insights from Route C/D can seed experiments |
| knowledge-channels.yaml | Source registry for Route C |
| harness_updater.py | Pipeline engine for Route C |
</Integration>
