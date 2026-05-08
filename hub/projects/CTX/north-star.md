---
category: SVTool
connections: []
current: '1256'
deadline: '2026-09-30'
id: CTX
layer: 1
links: ''
log:
- date: '2026-05-06'
  text: 'step_seed_vault() cold-start fix shipped (3964d39) — git history pre-loads vault.db on install, G1 recall fires session 1'
- date: '2026-05-06'
  text: '--reseed flag + sharing trigger built (ff34059) — first G1 recall prompts team install; PyPI baseline: 39/day 633/wk'
- date: '2026-05-07'
  text: 'Hub Market tab = CTX channel manager live — GitHub ★4, HN 4pts, GeekNews 4comments, PyPI 696/wk (+10%); driller corpus created (7 entity corpora now)'
- date: '2026-05-08'
  text: 'a0027a1 feat: ship CTX dashboard in pip wheel + ctx-dashboard CLI; channel reactions + PyPI scrape fixed in market-signals.py'
metric: PyPI downloads/week
milestones:
- done: true
  text: 'Cold-start fix: vault seed on install (3964d39) — G1 recall fires session 1'
- done: true
  text: 'Sharing trigger: .omc/ctx-g1-first-fire.flag fires team install prompt (ff34059)'
- done: true
  text: 'Channel manager live in hub — GitHub/HN/GeekNews/Dev.to/PyPI tracked (9cd2371)'
- done: true
  text: 'ctx-dashboard CLI shipped in pip wheel (a0027a1)'
- done: false
  text: 'Cloud vault infra decision (Supabase vs Railway) — unblocks Pro paywall'
- done: false
  text: 'Pro paywall: team shared vault gate + $15-20/mo pricing'
- done: false
  text: 'Publish to Claude Code plugin marketplace'
- done: false
  text: 'Reach 50 active installs (beyond downloads)'
- done: false
  text: 'Sustain 3 consecutive weeks of +10% WoW PyPI growth'
name: CTX
note: 'Claude Code memory + context retrieval plugin. PyPI 696/wk (+10% WoW), HN 4pts, GitHub 4 stars. Next gate: cloud infra decision → Pro paywall.'
position_x: 1
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