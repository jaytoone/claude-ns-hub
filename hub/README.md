# northstar-hub

**Personal AI project management hub** — North Star milestone tracking, live Claude sessions, CTX context alignment, and team productivity.

## Install

```bash
pip install northstar-hub
```

## Quick start

```bash
# Start the hub (binds to Tailscale IP or localhost)
northstar-hub

# Or start with CTX integration (auto-discovers CTX at :8787)
northstar-hub --with-ctx
```

Open `http://localhost:9000` in your browser.

## Features

- **North Star** — milestone pipeline management with AI execution loop
- **CTX** — real-time context alignment showing what Claude is working on
- **Corpus** — skill/agent list with live entity-corpus dashboard
- **PTY terminal** — interactive Claude session directly in the detail card
- **Exec sessions** — autonomous Claude loops dispatched per project

## CTX integration

If you already run CTX (`ctx-server` on port 8787), northstar-hub auto-discovers it at startup and shows it in the **CTX** tab. No configuration needed.

CTX users: install northstar-hub to get project milestone management alongside your context tracking.

```bash
pip install northstar-hub ctx-server  # install both
northstar-hub --with-ctx              # starts both services
```

## Configuration

Hub data lives in `~/.claude/hub/projects/` — one YAML file per project.
