---
name: milestone
description: Track a task as a milestone in the hub North Star dashboard. Creates a milestone via API, then sets up a CronCreate to auto-confirm when complete. Use at the start of any non-trivial implementation task.
---

# /milestone

Track the current task as a North Star milestone + auto-monitor via cron.

## When to invoke

Invoke this skill at the **start** of any task that:
- Takes more than one response turn to complete
- Involves code changes, file edits, or system configuration
- Was explicitly requested by the user as a feature, fix, or build

Skip for: quick questions, single-line fixes, explanations.

## Steps

### 1. Resolve project ID

Map CWD to hub project ID:

```
CWD contains...  → project ID
Moat             → MOAT
CTX              → CTX
FromScratch      → FromScratch
HugwartsBanana   → HugwartsBanana
AIKB             → AIKB
Sales / PaintPoint → Sales
```

If CWD doesn't match any known project, check `~/.claude/hub/projects/` for a directory matching the CWD name. If still no match, skip milestone creation and proceed with the task.

### 2. Create milestone via API

```bash
curl -s -X POST http://100.119.82.4:9000/api/northstar/{proj_id}/milestones \
  -H "Content-Type: application/json" \
  -d '{"text": "{task_title}", "layer": 0}'
```

- `task_title`: concise description of the task (max 60 chars), derived from the user's request
- Parse the response JSON to get the actual `milestone_id` (e.g. `"M9"`)
- If API fails (connection refused etc.), skip silently and proceed with the task

### 3. Create CronCreate

After getting the real milestone_id from step 2:

```
CronCreate(
  cron='*/15 * * * *',
  prompt='Check if milestone {milestone_id} for project {proj_id} is complete. Read ~/.claude/hub/projects/{proj_id}/completion-log.jsonl — if an entry with milestone_id="{milestone_id}" exists, PATCH http://100.119.82.4:9000/api/northstar/{proj_id}/milestones/{milestone_id} with {"status":"pending_confirmation"}, then CronDelete this job. Otherwise do nothing.',
  recurring=True
)
```

### 4. Completion signal

When the task is fully complete this session, write to completion log:

```bash
echo '{"session_id":"SESSION_ID","milestone_id":"MILESTONE_ID","evidence":"WHAT_YOU_DID","timestamp":"TIMESTAMP"}' \
  >> ~/.claude/hub/projects/{proj_id}/completion-log.jsonl
```

Replace SESSION_ID with the current session ID (first 8 chars), MILESTONE_ID with the actual ID from step 2, and TIMESTAMP with `$(date -Iseconds)`.

### 5. needs_clarification CronCreate

If you set a milestone to `needs_clarification`, also create a CronCreate immediately:

```
CronCreate(
  cron='*/5 * * * *',
  recurring=True,
  prompt='Check if milestone {milestone_id} for {proj_id} has a clarification answer.
GET http://100.119.82.4:9000/api/northstar/{proj_id}/milestones/{milestone_id}
If clarification_answer is set and non-empty:
  PATCH status=pending (auto-promote).
  Notify user: "Clarification received for {milestone_id} — starting work."
  CronDelete this job.
Otherwise do nothing.'
)
```

### 6. Output

Briefly confirm to user:
```
[Milestone M9 created] {task_title}
Cron monitor active — auto-confirms when completion-log entry found.
```

Then immediately proceed with the actual task without further milestone discussion.
