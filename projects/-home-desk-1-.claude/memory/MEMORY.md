# .claude Project Memory

## Key Decisions
- [execute-button] ▶ Execute on NS card = smart dispatcher: init milestones if none, process queued if exist — 2026-05-10
- [execute-button-location] Execute button moved to detail modal (NS section), not card bottom — 2026-05-10
- [execute-flow-desired] Execute → Claude sees all stones → creates per-stone crons → crons do jobs → UI updates — 2026-05-11 (SUPERSEDED)
- [execute-flow-redesign] Execute → Claude session → TaskCreate per queued stone → TaskUpdate as work progresses → completion-log + PATCH on done. Single session, no per-milestone crons. Crash watcher checks TaskList for incomplete tasks. Approved 2026-05-11.
- [task-watcher-hardened] task-watcher-hardened.py: exponential backoff 30s→10min for 429/529, max 8 retries, persistent task-queue.jsonl crash recovery — 2026-05-11
- [hub-ui-v2] /live without dropping todos — execute remaining spec items (hierarchical milestone tree, zellij, multi-goal tabs) — 2026-05-09
- [milestone-cron] Each queued milestone managed by Claude cron until done — polls hub API, marks pending_confirmation on completion — 2026-05-10
- [hooks-removed] Deprecated hooks removed from ~/.claude/settings.json: hub-inbox-inject.py (session-inbox flow, replaced by Execute+SessionStart), close-popup.sh (sentinel popup), subagent_tracker.py (stream-log only), utility-rate.py (CTX metric). Kept: stop-decision-capture.py (bm25-memory depends on it) — 2026-05-11
