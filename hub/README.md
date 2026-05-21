# claude-ns-hub

**The personal AI project hub that runs while you work.** North Star milestone tracking · live Claude exec sessions · entity corpus browser · mobile-ready terminal.

> One command. Your whole AI workflow, visible from any device.

![Hub Dashboard — North Star swimlane with live exec sessions](https://i.imgur.com/798spzC.png)

## Why you need this

While Claude Code runs your tasks autonomously, **you're flying blind** — no idea what it just did, which session is live, or whether it's stuck. claude-ns-hub fixes that:

- **See everything live**: exec sessions, session IDs, idle/busy state — on your phone while you're away
- **Queue work without interrupting Claude**: tap a stone, queue it, it runs on next idle
- **Resume any session**: ↻ button resumes exact conversation context, never lose work
- **One install, zero config**: auto-discovers projects, spawns entity corpus, exposes to Tailscale

The engineers shipping the most with Claude Code are the ones who can monitor, queue, and intervene — without context-switching.

## Install

```bash
pip install claude-ns-hub
```

## Quick start

```bash
claude-ns-hub
# Hub starts at http://<tailscale-ip>:9000
# North Star · CTX · Corpus · Market — all tabs, live
```

## What you get

| Feature | What it does |
|---------|-------------|
| **North Star swimlane** | Visualize all projects + milestones on one screen |
| **Live exec sessions** | See `claude-exec-MOAT` running, its session ID, busy/idle state |
| **Mobile terminal** | `⌨_` button attaches browser terminal to the running Claude session — type from your phone |
| **Session resume** | ↻ rows resume exact prior conversation; ✦ starts fresh — your choice per stone |
| **Entity corpus browser** | Browse all local skills/agents/corpora; inline search |
| **Drag-and-drop comments** | Drop files into stone comments; upload auto-appended as links |
| **PyPI installable** | `pip install claude-ns-hub && claude-ns-hub` — done |

## Metrics endpoint

```bash
curl http://localhost:9000/api/metrics?proj_id=MOAT
# → stones_completed, stones_queued, total_tokens per day
```

## Configuration

```bash
# Disable entity corpus auto-spawn
ENTITY_CORPUS_DISABLED=1 claude-ns-hub

# Custom entity corpus path
ENTITY_CORPUS_SERVER=~/my-corpus/server.py claude-ns-hub
```

## Screenshots

**North Star swimlane** — all projects, badge counts, live exec indicator at a glance:

![North Star swimlane](https://i.imgur.com/TG233OE.png)

**Skill / Agent badge picker** — assign `/expert-research` or any agent to a stone directly from the milestone row:

![Skill badge picker](https://i.imgur.com/v8VRaAz.png)

---

**pip install claude-ns-hub** — because you should know what Claude is doing right now.
