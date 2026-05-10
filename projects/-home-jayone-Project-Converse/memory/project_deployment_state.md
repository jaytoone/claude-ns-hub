---
name: Deployment State 2026-04-04
description: Phase 0 first deployment status — DC-001 live, Reddit blocked by karma, channel changes
type: project
---

DC-001 deployed to 직장생활 마이너갤러리 (id=office) at 2026-04-04 ~03:00 UTC.
Posted as be2jay (고정닉) — future posts should use 유동닉 mode.

**Why:** DC HIT gallery is READ-ONLY (auto-collected best posts, no direct posting).
**How to apply:** All DC deployment posts target `office` gallery, not `hit`.

Channel changes from original plan:
- DC HIT → DC 직장생활갤 (office) — HIT is read-only aggregate
- Reddit r/Cooking → r/CasualConversation — r/Cooking heavily moderated
- Quora excluded — Cloudflare blocks headless collection

Reddit account: Gold_Conversation579 (karma=1, 2 months old).
- Previous r/MachineLearning post was removed by Reddit filters
- Need Reddit Script App credentials (REDDIT_CLIENT_ID/SECRET) for karma_builder.py
- karma_builder.py + karma_schedule.sh ready, awaiting creds

DC account: be2jay (로그인됨, Playwright 세션에서 사용).
- 식별코드 took1839 / 보안코드 43XNZRMLD3X7ENR saved to .env + shared.env
- Note: 보안코드 is NOT the login password (it's SMS verification code from registration)
