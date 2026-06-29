# claude-ns-hub

[![PyPI Downloads](https://img.shields.io/pypi/dm/claude-ns-hub?label=downloads%2Fmonth&color=orange)](https://pypi.org/project/claude-ns-hub/)
[![PyPI Version](https://img.shields.io/pypi/v/claude-ns-hub?color=blue)](https://pypi.org/project/claude-ns-hub/)
[![GitHub Stars](https://img.shields.io/github/stars/jaytoone/claude-ns-hub?style=flat&color=yellow)](https://github.com/jaytoone/claude-ns-hub)
[![Python](https://img.shields.io/pypi/pyversions/claude-ns-hub)](https://pypi.org/project/claude-ns-hub/)

**You lose ideas every day.**

Note apps, memo pads, anything that requires you to sit at a computer — none of them keep up with your brain.

> _"Why even geniuses lose their ideas"_ — the answer is here.

![NS Hub — Second Brain for Claude Code users](https://raw.githubusercontent.com/jaytoone/claude-ns-hub/master/assets/ns-hub-banner-v9.png)

---

## NS Hub is your Second Brain × AI execution layer

Idea surfaces → **captured as a Stone** → Claude runs it autonomously → check results from your phone.

No laptop required. No memo needed. No context lost.

| Without NS Hub | With NS Hub |
|---|---|
| Idea appears → forgotten before you act | Instant Stone creation → Claude picks it up from the queue |
| Claude runs blind — you have no visibility | Live session monitoring from your phone |
| Must open laptop to check context | Resume any session with ↻ from anywhere |
| Notes pile up, context evaporates | Stone persistence — ideas never disappear |

---

## Why this exists

When Claude Code runs autonomously, you are **blind** — you cannot tell which sessions are alive, stalled, or finished.

The deeper problem is **idea loss**. Thoughts on the go, insights during commute, 3am realizations — most of them scatter without context.

NS Hub solves both at once:

- **Second Brain**: Capture ideas instantly as Stones → preserved with full context in local SQLite
- **Agent execution hub**: Stone → Claude runs autonomously → completion notification — entire loop closes on your phone

---

## Core loop

```
Idea surfaces
    ↓
Create a Stone (5 seconds from your phone)
    ↓
Claude Code picks it up from the queue
    ↓
Running — live session monitoring from phone
    ↓
Completion notification → review results
    ↓
Next Stone dispatched automatically
```

The entire loop runs without touching a computer.

---

## Screenshots

**North Star swimlane** — all projects, all lanes, live execution indicators:

![North Star swimlane](https://raw.githubusercontent.com/jaytoone/claude-ns-hub/master/assets/northstar-swimlane.png)

**Corpus browser** — 58 skills · 54 agents · 75 docs, all searchable inline:

![Corpus browser](https://raw.githubusercontent.com/jaytoone/claude-ns-hub/master/assets/corpus-browser.png)

---

## Install (60 seconds)

```bash
pip install claude-ns-hub
hub                          # starts at http://localhost:9001
```

No config files. No environment variables. No separate daemon. Open the printed URL in your phone browser and you're done.

### Prerequisites

- Python 3.10+
- [Claude Code CLI](https://claude.ai/code) (`claude --version`)
- `tmux` (`brew install tmux` / `apt install tmux`)
- Tailscale (optional — for remote mobile access)

---

## Quick start

```bash
# 1. Start the hub
hub

# 2. Inject the NS Hub protocol into Claude Code (run once)
hub install-global
# Writes stone lifecycle protocol to ~/.claude/CLAUDE.md

# 3. Add your first project
# North Star tab → "+ node" → set repo_path

# 4. Drop a Stone and let Claude run it
# Click project card → "+ milestone" → type your task → "live"
```

---

## What you get

| Feature | What it does |
|---------|-------------|
| **Stone capture** | Drop any idea as a Stone — Claude picks it up on next idle |
| **Live exec sessions** | Real-time visibility: busy/idle state, session ID, last tool used |
| **Mobile terminal** | Type directly into the running Claude session from your phone |
| **Session resume** | ↻ resumes exact prior context — no re-explaining, no lost work |
| **Context persistence** | Stone history, evidence URLs, conversation summaries — all local SQLite, fully portable |
| **North Star swimlane** | All projects + milestones on one screen, any device |
| **Corpus browser** | Browse all local skills/agents/docs; inline search across 180+ entries |
| **Zero-config install** | `pip install claude-ns-hub && hub` — that's the entire setup |

---

## Directory structure

```
~/.hub/
├── server.py          — main FastAPI server
├── hub.db             — SQLite: projects, settings
├── northstar.db       — SQLite: stones (milestones), exec sessions
├── config.yaml        — optional overrides (port, tailscale IP, etc.)
├── hooks/             — PostToolUse / Stop hooks for Claude Code
├── static/            — web UI (northstar.html, index.html)
├── corpora/           — local corpus collections (skills, agents, docs)
├── ee/                — enterprise extensions (source-available)
├── relay/             — optional Cloudflare Workers relay for remote access
└── ctx-dashboard/     — context telemetry dashboard
```

---

## Telemetry & privacy

On startup, one anonymized `hub_start` event is sent:
`ts`, `event`, `install_id=sha256(hostname)[:16]`, `version`, `os` — **no PII, no code, no Stone text**.

Opt out anytime:

```bash
curl -X POST http://localhost:9001/api/hub/consent \
  -H 'Content-Type: application/json' \
  -d '{"data_collection": false}'
```

---

## Troubleshooting

### tmux not found
```bash
sudo apt install tmux   # Ubuntu/WSL
brew install tmux        # macOS
tmux -V                  # verify
```

### Claude Code not authenticated
```bash
claude --version
npm install -g @anthropic-ai/claude-code   # if missing
claude login
```

### Hub can't find my project
```bash
hub init <PROJECT_ID> --dir /path/to/your/project
# or: North Star → "+ node" → set repo_path manually
```

### Hooks not firing
```bash
hub install-global
cat ~/.claude/settings.json | grep hub
```

---

## Data schema & portability

All data lives in local SQLite (`~/.hub/northstar.db`). No vendor lock-in.

```sql
-- milestones (Stones)
CREATE TABLE milestones (
  id TEXT PRIMARY KEY,          -- e.g. "M1301"
  project TEXT,
  text TEXT,                    -- your original idea / task
  status TEXT,                  -- queued | in_progress | pending_confirmation | done
  done INTEGER DEFAULT 0,
  exec_start TEXT,
  exec_end TEXT,
  model_used TEXT,
  evidence_url TEXT,
  append_message TEXT,          -- Claude's completion summary
  created_at TEXT DEFAULT (datetime('now'))
);
```

Export/import:
```bash
sqlite3 ~/.hub/northstar.db .dump > backup.sql
```

---

## Metrics endpoint

```bash
curl http://localhost:9001/api/metrics?proj_id=MOAT
# → stones_completed, stones_queued, total_tokens per day
```

---

**pip install claude-ns-hub** — stop losing your ideas.

---

## License

MIT. If commercial redistribution becomes an issue, we may adopt [Elastic License v2 (ELv2)](https://www.elastic.co/licensing/elastic-license) — source-available, free for personal/internal use, restricted for managed-service resale only. Community PRs and personal deployments will always remain free.
