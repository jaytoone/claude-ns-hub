# CTX Project Memory

## Video Edit Plan (2026-05-07 updated)
- NEW: IMG_1655.MOV (iPhone, 1.9GB) + screen_recording_new.mp4 (LT-3, 1.4GB) — both downloaded ✅
- PIP: screen recording main track + face cam small overlay (bottom-right)
- /live autonomous loop started 2026-05-07

## NS2 Goal (2026-05-09)
- NS2: first external user data in Turso (distinct_external_users > 0)
- v0.3.16 released to PyPI ✅ (GitHub Release created, workflow queued)
- Critical path: new installs get opt-in prompt → users consent → upload → NS2 passes
- Monitor: SELECT COUNT(DISTINCT user_id) FROM ctx_session_aggregates WHERE user_id NOT LIKE 'test_%'

## Next Session Plan (2026-05-09)
- Run: `ctx-telemetry consent grant` → `ctx-telemetry upload --send` → then `/live M1부터 CTX north-star 마일스톤 순서대로 실행`
- /live will execute north-star.md M1→M2→M4 in order (M3/M5/M6 gated by data/date/karma)

## CTX Status (2026-05-09) — commit 368f742
- v0.3.16 committed — Beta status, Turso pipeline live, north-star.md created (M1-M6)
- Turso: `ctx_session_aggregates` table in frwp-jaytoone DB, _turso_insert_rows() tested ✅
- Next session: `ctx-telemetry consent grant` + `upload --send` → M1 complete, then `/live M1부터 north-star 실행`
- awesome-claude-code #1773 CLOSED (API rejected) — resubmit via web form after 2026-05-16
- HN jaytoone karma=1 (needs 1 more for link posting), GeekNews no account yet
- TURSO_WRITE_TOKEN in telemetry.py — rotate to write-only token before publishing v0.3.16 to PyPI

## CTX Status (2026-05-09 earlier)
- v0.3.15 on PyPI ✅ | v0.3.16 staged (uncommitted) — Beta status, fixed project URLs, AI classifier added
- v0.3.16 publish: commit pyproject.toml + app.js → tag v0.3.16 → push → create GitHub Release
- HF Spaces: ctx-dashboard-demo RUNNING ✅ (Be2Jay), ctx-demo to DELETE manually at HF settings
- awesome-claude-code #1773 REJECTED (API submission not allowed — must use web form template)
  - Resubmit after: 2026-05-16 via https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml
- Official plugin submission: platform.claude.com/plugins/submit (requires manual login)
- HN account jaytoone: karma=1 (needs 1 more to post links), created 38 days ago
- GeekNews: no account yet — signup at news.hada.io/signup (ID/password only, no Google SSO)

## MCP Infrastructure (2026-04-29)
- Node.js installed via nvm v24.15.0 at `~/.nvm` (was missing entirely — old user `jayone` paths fixed to `desk-1`)
- Active MCPs: playwright-session-1~4 (`@playwright/mcp`), repomix, websearch, playwright-mcp-remote
- All npx-based MCPs need `env.PATH` set to nvm bin dir (no system node)
- `playwright-mcp-remote` (SSE localhost:8831): native WSL2 service (NOT Docker)
  - Service: `~/.config/systemd/user/playwright-mcp-sse.service` (enabled, auto-starts)
  - Script: `~/.local/bin/playwright-mcp-novnc` — starts Xvfb + x11vnc + noVNC + playwright-mcp
  - noVNC viewer: `http://localhost:6901/vnc.html` (Windows clients via wsl-expose 6901)
  - wsl-expose 6901 runs automatically on SessionStart hook
- `playwright-test` (`run-test-mcp-server`): Playwright Agents (Planner/Generator/Healer) — add back if needed
- Docker NOT needed in WSL2 for playwright — native approach is simpler and works

## Telemetry DB Decision (2026-05-09)
- DB: **Turso** (new DB `ctx-telemetry`, separate from FRWP) — 5 GB free, HTTP API, write-only token for clients
- Upload endpoint: direct Turso HTTP API from telemetry.py (no server needed)
- Table: `session_aggregate` (schema v1.6) — k-anonymity enforced client-side (k≥5)
- Monetization prep also queued for this session

## User Data Flywheel — Activation Decision (2026-05-09)
- Decision: activate telemetry/data gathering pipeline — signals are strong enough (1.4k/mo PyPI, 4 stars)
- Plan: prepare telemetry opt-in → aggregate pipeline → HF dashboard shows real user data → flywheel starts
- Reference docs: `20260427-ctx-user-data-flywheel-strategy.md`, `20260427-ctx-flywheel-data-coverage.md`

## Social Accounts (2026-05-10)
- GeekNews: `nave94` / `jayone8974^^` — post live at news.hada.io/topic?id=29124 (1pt, 6 comments)
- HN: `nave94hn` / `jayone8974^^` — comment posted on #48071940, karma=1, waiting for upvote to post Show HN
- HN `jaytoone` (old): karma=1, password unknown — abandoned

## CTX Distribution Channels (2026-05-02)
Primary channels for CTX outreach (in order):
1. **LinkedIn** — founder post, dev tool audience
2. **Blog** — long-form writeup (jaytoone.dev or dev.to)
3. **GeekNews (GN)** — Korean dev community
4. **Hacker News** — Show HN post
5. **YouTube** — demo/explainer video

Previously also noted: r/ClaudeAI, r/LocalLLaMA, Claude Developer Forum (still valid, secondary)

## Vault Security (2026-05-02)
- vault.db scrubbed: 453 messages had tokens/passwords replaced with [REDACTED]
- Backup: vault.db.bak_20260502 (420MB)
- CTX + Secure projects excluded from vault read/write (chat-memory.py hardcoded exclusion)
- Excluded set: -home-desk-1-Project-CTX, -home-jayone-Project-CTX, Secure variants

## CTX Release Status (2026-05-02)
- v0.3.10 on PyPI ✅ | GitHub released ✅ | Docker validated ✅
- Install: `pip install ctx-retriever && ctx-install` OR `/plugin install ctx@jaytoone`
- Docker dashboard image: `ctx-dashboard:latest` (running on port 8787, telemetry mounted)
