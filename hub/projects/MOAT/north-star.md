---
category: Engineering
connections:
- CTX
- FromScratch
- HugwartsBanana
current: '60'
deadline: '2026-08-31'
id: MOAT
layer: 1
links: ''
log:
- date: '2026-05-09'
  text: '6ff2aff init: Moat project'
metric: Hub dashboard completeness score (%)
milestones:
- done: true
  id: M1
  layer: 0
  parent_id: null
  status: done
  text: All 14 E2E invariant checks passing (health × 4, tab × 4, dark mode × 4, ns_nodes,
    no_errors)
- claude_ack: 2026-05-09T22:14
  done: false
  id: M2
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-09T22:13
  status: pending
  text: Mobile-responsive — all 4 panes (NS/CTX/Corpus/Market) + detail pane on iPhone
- done: true
  id: M3
  layer: 0
  parent_id: null
  status: done
  text: Milestone system fully functional — 3-state toggle, auto-ack, confirm-delete,
    delete+confirm
- done: true
  id: M4
  layer: 0
  parent_id: null
  status: done
  text: Stop hook E2E verify — hub/verify.py 14-check runs on every session end
- claude_ack: 2026-05-09T22:33
  done: false
  id: M5
  layer: 0
  parent_id: null
  status: pending
  text: Hub stable operation — 0.0.0.0 binding persisted, auto-restart on crash, hub
    accessible from all Tailscale devices
- claude_ack: 2026-05-09T22:33
  done: false
  id: M6
  layer: 0
  parent_id: null
  status: pending
  text: iPhone file transfer channel — Tailscale → WSL2 image/file receive pipeline
    working
- claude_ack: 2026-05-09T22:33
  done: false
  id: M7
  layer: 0
  parent_id: null
  status: pending
  text: All project NS stones realistic + non-rotted — CTX/FromScratch/FRWP/AIKB/HugwartsBanana/MOAT
    all reviewed
name: Claude-Hub
note: Personal AI MOAT — hub dashboard as the operational brain. Complete the hub
  first, then leverage it for content/career.
parent: null
position_x: 1
repo_path: /home/desk-1/.claude/hub
stage: unassigned
status: on-track
target: '100'
unit: '%'
x: 485
y: 0
---

# MOAT — North Star (redefined 2026-05-09)

## Why this metric
Hub dashboard is the operational center for all projects. Completing it to production quality
creates the foundation for everything else — content creation, career tracking, milestone management.
"Completeness %" = (passed invariants / 14) × 40 + milestone_done_ratio × 40 + mobile_score × 20.

## Current State (2026-05-09)
- E2E: 14/14 passing ✓
- Milestones: 3-state system working ✓
- Stop hook: 14-check verify integrated ✓
- Mobile: partial (text-size-adjust added today)
- Stable operation: hub host fixed to 0.0.0.0 ✓

## Strategy
1. Complete mobile UX (all panes + detail pane responsive on iPhone)
2. Stable ops (auto-restart, Tailscale file transfer)
3. Review all project NS stones for accuracy
4. Then pivot to content production using hub as the tracking system

## OKRs — 2026 Q2
- K1: Hub completeness score ≥ 90% by end of Q2
- K2: All 7 project NS stones non-rotted and current
- K3: iPhone → hub workflow working (file transfer + mobile access)

## Links
- Hub: http://100.119.82.4:9000
- Verify: python3 ~/.claude/hub/verify.py
- Source: ~/.claude/hub/