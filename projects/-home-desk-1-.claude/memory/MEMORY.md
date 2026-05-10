# .claude Project Memory

## Key Decisions
- [execute-button] ▶ Execute on NS card = smart dispatcher: init milestones if none, process queued if exist — 2026-05-10
- [execute-button-location] Execute button moved to detail modal (NS section), not card bottom — 2026-05-10
- [execute-flow-desired] Execute → Claude sees all stones → creates per-stone crons → crons do jobs → UI updates — 2026-05-11
- [hub-ui-v2] /live without dropping todos — execute remaining spec items (hierarchical milestone tree, zellij, multi-goal tabs) — 2026-05-09
- [milestone-cron] Each queued milestone managed by Claude cron until done — polls hub API, marks pending_confirmation on completion — 2026-05-10
