# MOAT Project Memory

## Current State
- Hub dashboard: http://100.119.82.4:9000 (North Star → CTX → Corpus → Market)
- North Star dashboard redesigned to read-only visualization (arc gauges, milestone pipeline)
- File-backed: ~/.claude/hub/projects/*/north-star.md (YAML frontmatter + markdown body)
- Entity corpus dashboard: http://100.119.82.4:8989

## Key Decisions
- [Hub-Terminal] Terminal → zellij 전환 예정. drag-copy + 우클릭 paste 지원. 모바일 resize 가능. — 2026-05-09
- [Hub-DetailUI] Align 버튼 → Init 버튼으로 교체 (마일스톤 없을 때 pj 환경 동기화). Open terminal 제거. 멀티골 기존 UI 유지. Progress arc 수정. 마일스톤 계층 시각화. — 2026-05-09
- [NS-Automation] NIPA polling excluded from core NS sync system — optional per-project remote_poll in north-star.md only. Core = PostToolUse doc-extract + Stop git-commit. — 2026-05-07
- [NS-Automation] Generic project detection: scan ~/.claude/hub/projects/ dir at runtime, no hardcoded project names — 2026-05-07
- [Hub/NorthStar] Detail panel redesign: side drawer → centered overlay modal with goal hierarchy (NS→OKRs→Milestones) + current work state — 2026-05-07
- [Hub] North Star = read-only display only, no editing in UI — 2026-05-06
- [Hub] UI data source = markdown files (not northstar.json) — 2026-05-06
- [Hub] Alignment Pulse uses CTX /api/graph hot nodes to detect work-north-star gap — 2026-05-06
- [Hub] wsl-expose auto-runs on hub/entity-corpus launch to expose ports to LT-1/LT-3 — 2026-05-06
- [Entity] -cc flag added for explicit corpus creation with Step 1.5 Overlap Guard — 2026-05-06
- [Entity] corpus-registry.yaml YAML fixed (out_action moved from scope_gate sequence) — 2026-05-06
- [NS-Redesign] Flat table → swimlane hierarchy layout (L0=Strategic/L1=Domain/L2=Execution). parent+layer+position_x added to north-star.md schema. Free-form 2D canvas rejected (spatial rot). — 2026-05-08
- [NS-Milestone] Memo pane → Milestone Creator with claude_ack. Max 2 layers (L0 goal + L1 sub). Stop hook writes claude_ack timestamp on commit match. Sequence: P1(schema)→P2(UI)→P3(hook)→P4(ack indicator)→P5(swimlane). — 2026-05-08
- [NS-P5] Swimlane layout approved. User confirmed building P5 now. All projects start at layer 0; user sets parent/layer to define hierarchy. — 2026-05-08
