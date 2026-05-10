---
category: SVTool
connections: []
current: '1256'
deadline: '2026-09-30'
id: CTX
layer: 2
links: ''
log:
- date: '2026-05-06'
  text: step_seed_vault() cold-start fix shipped (3964d39) — git history pre-loads
    vault.db on install, G1 recall fires session 1
- date: '2026-05-06'
  text: '--reseed flag + sharing trigger built (ff34059) — first G1 recall prompts
    team install; PyPI baseline: 39/day 633/wk'
- date: '2026-05-07'
  text: Hub Market tab = CTX channel manager live — GitHub ★4, HN 4pts, GeekNews 4comments,
    PyPI 696/wk (+10%); driller corpus created (7 entity corpora now)
- date: '2026-05-08'
  text: 'a0027a1 feat: ship CTX dashboard in pip wheel + ctx-dashboard CLI; channel
    reactions + PyPI scrape fixed in market-signals.py'
- date: '2026-05-09'
  text: '7171ae3 feat: add all channel reactions to market-signals + fix PyPI + GeekNews
    scrape; d8fd10e Add GitHub Actions workflow to publish to PyPI (+1 more)'
- date: '2026-05-09'
  text: '368f742 feat: activate Stage 2 telemetry pipeline + north-star milestones;
    7171ae3 feat: add all channel reactions to market-signals + fix PyPI + GeekNews
    scrape (+1 more)'
- date: '2026-05-09'
  text: '17eda6e feat: M2 — opt-in prompt at install + secure Turso token (env var
    override); 368f742 feat: activate Stage 2 telemetry pipeline + north-star milestones
    (+1 more)'
- date: '2026-05-09'
  text: '97385f8 chore: save live-state + goal-tree for north-star run (iter 2/5 in
    progress); 17eda6e feat: M2 — opt-in prompt at install + secure Turso token (env
    var override) (+1 more)'
- date: '2026-05-09'
  text: '11527b9 chore: live iter 2 — M1+M2+M5-GN done, north-star updated; aa3db68
    fix: add missing `import os` to telemetry.py + batch Turso inserts (+1 more)'
- date: '2026-05-09'
  text: 'b900b35 feat: set NS2 — first external user data in Turso (0 → 1 distinct_external_users);
    11527b9 chore: live iter 2 — M1+M2+M5-GN done, north-star updated (+1 more)'
- date: '2026-05-09'
  text: 'b267eab feat: ctx-telemetry send — one-step consent + upload; b900b35 feat:
    set NS2 — first external user data in Turso (0 → 1 distinct_external_users) (+1
    more)'
- date: '2026-05-09'
  text: '71ae2ef feat: auto-upload session stats on session end (opt-out model); b267eab
    feat: ctx-telemetry send — one-step consent + upload (+1 more)'
- date: '2026-05-09'
  text: 'efa88be feat: schema v1.7 — project_type_id + ctx_version + utility_by_qtype;
    71ae2ef feat: auto-upload session stats on session end (opt-out model) (+1 more)'
- date: '2026-05-09'
  text: '32c4d5c live-inf iter 1/∞: success | goal_v0: NS2 status check + north-star
    updated + GN v0.3.19 comment; efa88be feat: schema v1.7 — project_type_id + ctx_version
    + utility_by_qtype (+1 more)'
- date: '2026-05-10'
  text: '32c4d5c live-inf iter 1/∞: success | goal_v0: NS2 status check + north-star
    updated + GN v0.3.19 comment; efa88be feat: schema v1.7 — project_type_id + ctx_version
    + utility_by_qtype (+1 more)'
- date: '2026-05-10'
  text: 'b19c250 feat: /api/stats endpoint + weekly PyPI trend snapshot (1,854 total,
    912 last 7d); 32c4d5c live-inf iter 1/∞: success | goal_v0: NS2 status check +
    north-star updated + GN v0.3.19 comment (+1 more)'
- date: '2026-05-10'
  text: '7f9d5a9 fix: deterministic sort tiebreaks + build_docs_bm25 dedup (hang-in
    PR #4 + #5); b19c250 feat: /api/stats endpoint + weekly PyPI trend snapshot (1,854
    total, 912 last 7d) (+1 more)'
- date: '2026-05-10'
  text: '411b6a2 [hang-in] refactor(eval): unify 3 eval-pipeline tokenizers via monolith
    bm25-memory.tokenize (PR-3 re-author); 7c25f50 [hang-in] docs: add MAINTAINERS.md
    (per #1 — area-of-ownership split) (+1 more)'
metric: PyPI downloads/week
milestones:
- done: true
  text: 'Cold-start fix: vault seed on install (3964d39) — G1 recall fires session
    1'
- done: true
  text: 'Sharing trigger: .omc/ctx-g1-first-fire.flag fires team install prompt (ff34059)'
- done: true
  text: Channel manager live in hub — GitHub/HN/GeekNews/Dev.to/PyPI tracked (9cd2371)
- done: true
  text: ctx-dashboard CLI shipped in pip wheel (a0027a1)
- done: true
  status: done
  text: Cloud vault infra decision (Supabase vs Railway) — unblocks Pro paywall
- claude_ack: '2026-05-11T00:00:00Z'
  done: false
  id: M6
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-11T00:12
  queued_at: 2026-05-11T00:09
  status: pending_confirmation
  text: 'Pro paywall: team shared vault gate + $15-20/mo pricing'
- claude_ack: 2026-05-11T00:39
  done: false
  id: M7
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-11T00:38
  queued_at: 2026-05-11T00:09
  status: pending_confirmation
  text: Publish to Claude Code plugin marketplace
- clarification_answer: It’s done
  clarification_answered_at: 2026-05-11T00:12
  clarification_question: '"Active install" is ambiguous — what definition should
    we use? Options: (A) telemetry opt-in users in Turso (trackable), (B) users who
    ran ctx at least once after pip install, (C) distinct users active in the last
    30 days. Also: what is the current active-install count, and are there specific
    outreach/activation actions you want me to execute (e.g., follow-up DMs to existing
    PyPI downloaders, onboarding nudge in ctx CLI, referral prompt)?'
  claude_ack: 2026-05-11T00:36
  done: false
  id: M8
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-11T00:36
  status: pending_confirmation
  text: Reach 50 active installs (beyond downloads)
- clarification_question: 'M9 tracking infrastructure is live: wow-tracker.py initialized
    with streak 1/3 (633→912 downloads/wk, +44.1% WoW). Next target ≥1,004/wk by May
    18. Two more consecutive weeks needed. What growth actions should I execute? Options:
    (a) Write distribution content for new channels (Reddit r/ClaudeAI, Discord),
    (b) Plugin marketplace submission (overlaps M7), (c) Set up weekly Monday cron
    to auto-snapshot + alert if WoW <10%.'
  claude_ack: 2026-05-11T00:38
  done: false
  id: M9
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-11T00:38
  status: needs_clarification
  text: Sustain 3 consecutive weeks of +10% WoW PyPI growth
- claude_ack: 2026-05-11T00:38
  done: false
  id: M10
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-11T00:38
  status: pending_confirmation
  text: there are no code files showing on the ctx dasboard proof apne.
- claude_ack: 2026-05-10T17:41
  done: true
  done_at: 2026-05-10T17:41
  id: M11
  layer: 0
  parent_id: null
  status: done
  text: Add Naver email channel to hub manager — check reactions/issues via IMAP
  user_added_at: 2026-05-10T12:26
- claude_ack: 2026-05-10T18:17
  done: false
  id: M12
  layer: 0
  parent_id: null
  pending_confirm_at: 2026-05-10T18:17
  status: pending_confirmation
  text: 'Respond to d9ng GitHub replies on PRs #4/#5 + production hardening thread'
  user_added_at: 2026-05-10T18:10
name: CTX
note: 'Claude Code memory + context retrieval plugin. PyPI 696/wk (+10% WoW), HN 4pts,
  GitHub 4 stars. Next gate: cloud infra decision → Pro paywall.'
parent: MOAT
position_x: 3
stage: unassigned
status: on-track
target: '1000'
unit: downloads/wk
x: -585
y: 0
---

# CTX — North Star

## Why this metric
Active installs (users with CTX running, not just downloaders) directly measures product-market fit. It's the leading indicator for future monetization (cloud tier) and credibility for consulting/teaching.

## What CTX does
Gives Claude Code persistent memory across sessions — G1 (time), G2 (space), CM (chat) retrieval hooks. Saves context to a local vault.db, retrieves relevant past decisions/docs on every prompt.

## Strategy
- Distribution: Claude Code plugin marketplace (primary), HN Show HN, GeekNews, Dev.to
- Activation: `ctx-install` one-command setup + CTX dashboard showing memory health
- Retention: per-session utility rate visible to user (they see CTX working)

## OKRs — 2026 Q2

### Done
- ✓ Cold-start fix: vault seed on install (G1 fires session 1)
- ✓ Sharing trigger: team install prompt on first G1 recall
- ✓ Channel manager: live reaction metrics in hub dashboard
- ✓ ctx-dashboard CLI shipped in wheel

### In progress
- K1: Cloud vault infra decision → Pro paywall design ($15-20/mo)
- K2: 3 customer interviews ("would you pay $15/mo for team vault sync?")
- K3: Sustain PyPI +10% WoW for 3 consecutive weeks (currently at week 1)

### Upcoming
- K4: Publish to Claude Code plugin marketplace
- K5: Reach 50 active installs (tracked separately from downloads)

## Links
- Repo: /home/desk-1/Project/CTX
- Dashboard: http://100.119.82.4:8787