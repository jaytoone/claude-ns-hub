---
name: omc-episode-memory
description: Episodic memory for autonomous agent loops — save execution summaries and retrieve relevant past episodes to inject context into future runs
---

<Purpose>
omc-episode-memory implements a lightweight episodic memory system for Claude Code's autonomous agent loops. It saves execution summaries after each ralph/autopilot run and retrieves relevant past episodes to inject context into future runs — enabling agents to learn from experience without full trajectory replay.

Based on the Trace-First Flywheel pattern (arXiv:2601.01743v1) and Agent Transformer memory subsystem design (M component of A=(π_θ, M, T, V, E)).
</Purpose>

<Use_When>
- After completing a ralph, autopilot, or ultrawork run — save the episode
- Before starting a new ralph/autopilot run — load relevant past episodes for context
- User says "remember this run", "what happened last time", "use past experience"
- autopilot Phase 5 cleanup — always save before deleting state files
- After a fatal failure that triggers omc-goal-tree — save failure episode first
</Use_When>

<Do_Not_Use_When>
- One-shot conversational tasks with no iteration
- Tasks where the project has no .omc/ directory (no persistent state context)
- When user explicitly says "fresh start, ignore past runs"
</Do_Not_Use_When>

<Modes>
This skill operates in two modes specified at invocation:

**save**: Record the current execution as an episode
**load**: Retrieve relevant past episodes for the current task
</Modes>

<Steps_Save>
## SAVE Mode: Record Episode

1. **Collect execution summary** from current session context:
   ```
   - task_type: "autopilot" | "ralph" | "ultrawork" | "manual"
   - task_description: 1-2 line summary of what was attempted
   - outcome: "success" | "failure" | "partial"
   - key_errors: list of distinct error messages encountered (max 5)
   - approach_used: brief description of the solution strategy
   - phases_completed: which phases finished successfully
   - fatal_failure_type: if outcome=failure, classify as Transient/Persistent/Fatal
   - project_hints: any project-specific patterns discovered (file conventions, test setup, etc.)
   ```

2. **Three Laws Endure check** before saving:
   - If the current run caused a safety violation or corrupted state → skip save, log warning
   - If outcome=success AND all tests passed → mark episode as high_quality=true
   - Otherwise → save as-is (all episodes have value, even failures)

3. **Append to .omc/episodes.jsonl**:
   ```json
   {"id": "<uuid-v4>", "ts": "<ISO8601>", "task_type": "...", "task_desc": "...", "outcome": "...", "key_errors": [], "approach": "...", "phases_done": [], "fatal_type": null, "project_hints": [], "high_quality": false}
   ```
   - `id` field: generate UUID v4 at save time (stable deduplication key for LOAD mode)
   - One JSON object per line
   - Never overwrite existing entries — always append
   - If .omc/episodes.jsonl does not exist → create it

4. **Also save to mcp__memory__** (if available):
   - Call `mcp__memory__create_entities` with entity name `{ProjectName}-Episode-{YYYYMMDD}-{outcome}`
   - Observations: task_desc, outcome, key_errors summary
   - Only if mcp__memory__ is accessible — skip silently if not

5. **Confirm**: "Episode saved. Total episodes: N"
</Steps_Save>

<Steps_Load>
## LOAD Mode: Retrieve Relevant Episodes

1. **Identify current task** from user's description or current context:
   - Extract key terms: task type, domain, technology stack, error patterns

2. **Read .omc/episodes.jsonl** and apply compression selection:
   - If file doesn't exist → report "No past episodes found. Starting fresh."
   - Parse all JSONL entries, sorted by `ts` descending (newest first)

   **Episode UUID**: Each episode must carry a stable `id` field (UUID v4) assigned at save time.
   If an episode lacks `id`, derive one as `sha256(ts + task_desc)[:16]` for deduplication purposes.

   **Compression Selection Algorithm** (prevents context overflow):
   ```
   BUCKET A — Recency:     last 5 episodes regardless of outcome
   BUCKET B — Failures:    all episodes where outcome != "success" (max 10)
   BUCKET C — Gold:        top 3 episodes where high_quality=true

   MERGE: union(A ∪ B ∪ C), deduplicate by episode.id  ← UUID-based, not ts
   OVERFLOW GUARD: if |merged| > 10 → compress oldest entries:
     - Replace each excess entry with 1-line summary:
       "{ts} [{outcome}] {task_desc[:60]} | errors: {key_errors[0] if any}"
     - IMPORTANT: compressed [FAILURE] entries MUST preserve key_errors[] field
       even in compressed form. Format: "{ts} [FAILURE] {task_desc[:40]} | errors: {key_errors[:2]}"
     - Keep full objects only for the 10 most recent/relevant
   ```

   **Relevance scoring** (within each bucket, rank by):

   *Primary — TF-IDF cosine similarity* (preferred when episode store ≥ 5 entries):
   ```
   1. Build TF-IDF vectors from task_desc + key_errors joined as text corpus
   2. Compute cosine similarity between current_task_text and each episode vector
   3. Rank episodes by similarity score descending
   4. Use scores as primary sort key within each bucket
   ```

   *Fallback — Tag-based boost* (when episode store < 5 OR TF-IDF unavailable):
   - task_type match with current task → +2 priority
   - key_errors[] overlap with current error context → +3 priority
   - project_hints containing current project name → +1 priority

   Note: Tag-based fallback is a known approximation. Flag in output: "[relevance: tag-based]" vs "[relevance: tfidf]".

3. **Classify episodes** before formatting:
   - Tag each selected episode: `[GOLD]`, `[FAILURE]`, `[RECENT]`, or `[COMPRESSED]`
   - `[COMPRESSED]` entries → render as 1-line summaries (no full field expansion)
   - `[GOLD]` entries → render full details (approach + project_hints emphasized)
   - `[FAILURE]` entries → render key_errors + fatal_type emphasized

4. **Format context injection**:
   ```
   ## Past Episode Context ({N} episodes: {gold} gold, {fail} failures, {recent} recent)

   [GOLD | {date} | success]
   Task: {task_desc}
   Approach: {approach}  ← WHAT WORKED
   Project hints: {project_hints}

   [FAILURE | {date} | {outcome}]
   Task: {task_desc}
   Errors: {key_errors}  ← WHAT TO AVOID
   Fatal type: {fatal_type}

   [RECENT | {date} | {outcome}]
   Task: {task_desc}
   Approach: {approach}
   Errors encountered: {key_errors}

   [COMPRESSED] {ts} [{outcome}] {1-line summary}
   ...

   → Apply these lessons. Repeat [GOLD] approaches. Avoid [FAILURE] patterns.
   ```

5. **Inject into current agent context** — place this block at the top of Phase 0 or Phase 2 instructions

6. If no relevant episodes found → silently proceed (no noise for fresh starts)

7. **Overflow telemetry**: Report "Loaded {N} episodes ({compressed} compressed). Total in store: {total}."
</Steps_Load>

<Integration_With_Autopilot>
## Integration Point: autopilot Phase 5

The omc-autopilot skill's Phase 5 (Cleanup) MUST invoke omc-episode-memory save mode BEFORE deleting state files:

```
Phase 5 - Cleanup (modified):
  1. Call omc-episode-memory (save mode) → preserve execution summary
  2. THEN: Remove .omc/state/autopilot-state.json, ralph-state.json, etc.
  3. Run /oh-my-claudecode:cancel for clean exit
```

This ensures no execution data is lost before cleanup.
</Integration_With_Autopilot>

<File_Format>
## .omc/episodes.jsonl Format

Each line is a valid JSON object:
```json
{
  "ts": "2026-03-25T14:30:00Z",
  "task_type": "autopilot",
  "task_desc": "Build REST API for inventory management",
  "outcome": "success",
  "key_errors": ["ModuleNotFoundError: fastapi", "TypeError: expected str got int"],
  "approach": "Used pure Python http.server, avoided FastAPI dependency",
  "phases_done": ["expansion", "planning", "execution", "qa", "validation"],
  "fatal_type": null,
  "project_hints": ["project uses Python 3.12", "no test framework configured"],
  "high_quality": true
}
```
</File_Format>

<Three_Laws_Constraint>
## Three Laws Integration (Endure)

Before saving any episode:
- Check: did this run cause any unintended file deletions or external service calls?
- Check: did this run modify files outside the project directory?
- If yes to either → add "safety_warning": true to episode entry
- Do NOT skip saving — warnings are valuable learning signals
</Three_Laws_Constraint>
