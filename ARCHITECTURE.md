# claude-ns-hub Architecture

## Overview

claude-ns-hub is a FastAPI-based milestone tracking and agent dispatch system for Claude Code.
It runs as a local server (HTTP + WebSocket) and provides a single-page dashboard (`northstar.html`)
for managing projects, milestones ("stones"), and AI agent execution sessions.

```
Browser (northstar.html SPA)
        │  HTTP REST + WebSocket
        ▼
FastAPI server (server.py)
   ├── SQLite (ns-events.db)   ← primary store
   ├── YAML files              ← async backup / human-readable
   ├── tmux sessions           ← Claude Code exec engine
   └── stop-hook / BM25        ← post-execution pipeline
```

---

## Core Components

### 1. FastAPI Server (`server.py`)

- Entry point: `hub` CLI → `uvicorn hub.server:app`
- Default port: **9001** (PyPI stable); dev: **9000**
- All state mutations go through REST endpoints; WebSocket (`/ws`) pushes live updates to the browser
- Background threads handle SQLite writes and YAML sync to keep hot-path latency < 10ms

Key endpoint groups:

| Prefix | Purpose |
|--------|---------|
| `/api/northstar/{proj}/milestones` | CRUD for stones |
| `/api/northstar/{proj}/execute` | Spawn / resume Claude Code agent |
| `/api/northstar/{proj}/north-stars` | Sub-goal management |
| `/api/hub/*` | Hub-level ops (restart, update-check, health) |
| `/api/events` | Event log (SQLite-backed) |
| `/api/ntfy/*` | Push notification config |

---

### 2. Data Layer

#### SQLite (`ns-events.db`)
Primary store. Two tables:

- `milestones_store` — one row per stone, JSON blob for full milestone data
- `project_meta` — per-project metadata (north stars, sub-goals)

Every `_save_project()` call does an upsert; reads go directly to SQLite (~1ms).

#### YAML backup
`~/.claude/hub/data/<proj>.yaml` (or configured `DATA_DIR`).
Written asynchronously after every SQLite upsert. Used for human inspection and disaster recovery.
Do NOT rely on YAML as the source of truth in code.

---

### 3. Stone Lifecycle

```
queued
  │  user clicks Execute → Claude Code agent spawned
  ▼
(agent working — tmux session active)
  │  agent calls PATCH status=pending_confirmation + append_message
  ▼
pending_confirmation
  │  user reviews → clicks ✓ Done or re-queues
  ▼
done
```

Additional statuses: `held` (paused), `needs_clarification` (agent asked a question),
`review` (needs human review before re-queue).

Stone fields of note:
- `conversation[]` — chat thread between user and agent (role: user | claude)
- `claude_ack` — bool: agent has acknowledged the stone
- `pending_confirm_at` — timestamp used for sort ordering
- `moscow` — MoSCoW priority tag (M/S/C/W)

---

### 4. Exec Engine

**Spawn flow:**

1. `POST /api/northstar/{proj}/execute` → `_spawn_claude()`
2. Kills existing exec sessions (`_kill_all_exec_sessions()`)
3. Creates tmux session `claude-exec-{proj}`
4. Runs `claude [--resume <session_id>] --model <model>` inside the pane
5. Injects the EXECUTE SYNC prompt listing all queued stones
6. Writes `.last-spawn-info.json` for session resume detection

**Session resume:**
Stop-hook captures the Claude Code session ID → `.last-session-id`.
Next spawn reads the file and passes `--resume <id>` so conversation context is preserved.

**Continuation:**
`stop-inject.py` runs after each agent stop. If queued stones remain,
it re-injects the dispatch prompt (exit code 2 = re-enter loop). Max 5 attempts per session.

---

### 5. Stop-Hook (`stop-hook.py` / `northstar-stop-inject.py`)

Registered in `~/.claude/settings.json` as a `PostToolUse` / `Stop` hook.

Responsibilities:
- Capture session ID to `.last-session-id`
- Detect if running inside an exec tmux session (`in_exec_tmux()`)
- If inside exec session: run stop-inject logic (re-dispatch or idle handoff)
- If interactive session: skip (user is at the keyboard)

---

### 6. BM25 Corpus (`ctx-retriever`)

Separate package (`ctx-retriever`, port **8787**) that indexes project files and milestone
history using BM25. The hub queries it for context injection when spawning agents,
giving Claude relevant past decisions without exceeding context limits.

The entity-corpus dashboard runs on port **8989** (separate service, do NOT confuse with 8787).

---

### 7. Push Notifications (ntfy)

Uses ntfy.sh public cloud. Server POSTs on PTY idle events.
Rate-limited: 10-minute cooldown per key, 50/day cap.
Topic: configurable via `/api/ntfy/topic`. Default: `hub-moat-jayone`.

---

## File Structure

```
~/.claude/hub/
├── hub/
│   ├── server.py          # FastAPI app — all routes
│   ├── static/
│   │   └── northstar.html # Single-page dashboard (vanilla JS)
│   └── __init__.py
├── hooks/
│   ├── stop-hook.py       # Claude Code Stop hook
│   └── stop-inject.py     # Re-dispatch logic after agent stop
├── data/                  # YAML backups (one file per project)
├── ns-events.db           # SQLite primary store
├── .last-session-id       # Last captured Claude Code session ID
├── .last-spawn-info.json  # Last exec spawn options (model, agent, etc.)
├── pending-execute-queue.jsonl  # Append-only queue log
├── .queue-offset          # Byte-offset cursor into the queue log
├── CONTRIBUTING.md
├── ARCHITECTURE.md        # This file
└── pyproject.toml
```

---

## Port Layout

| Port | Service | Notes |
|------|---------|-------|
| 9000 | Hub (dev / legacy) | Original default; svchost.exe conflict on Windows |
| 9001 | Hub (PyPI stable) | Current default since M584 |
| 8787 | ctx-retriever | BM25 context search |
| 8989 | entity-corpus | Entity/corpus dashboard |
| 6901 | websockify / noVNC | Browser VNC proxy for Playwright sessions |

Override with `HUB_PORT` env var.

---

## Design Principles

- **Hot-path non-blocking**: all SQLite/YAML writes in background threads
- **Crash-safe queue**: byte-offset cursor advances before stderr emit
- **Session idempotency**: kill-all-exec before every spawn prevents orphaned sessions
- **No external dependencies at runtime**: SQLite, tmux, vanilla JS SPA — no Redis, no Celery
- **English UI**: all user-visible strings in northstar.html must be in English
