# Contributing to claude-ns-hub

Thank you for your interest in contributing! claude-ns-hub is a personal AI project hub that keeps Claude Code sessions visible and manageable from any device.

## Quick start (2 minutes)

```bash
git clone https://github.com/be2jay67/claude-ns-hub  # replace with actual repo URL
cd claude-ns-hub
pip install -e ".[dev]"
hub   # starts hub at http://localhost:9001
```

That's it — no database setup, no environment variables required for basic dev.

## Who we're looking for

We're a small project and want **focused contributors**, not drive-by PRs. Ideal profile:

- **Python** (FastAPI, SQLite, asyncio) — backend is ~3 files
- **Claude Code user** — you use the tool daily, you feel the pain
- **2–5 hrs/week** available, fully remote, no compensation (pure OSS)
- Bonus: Korean reading ability (issues may be in Korean)

## Project structure

```
hub/
├── server.py          ← FastAPI server (all API + websocket logic)
├── static/
│   └── northstar.html ← Single-page UI (vanilla JS, ~15k lines)
├── hub/               ← CLI entry point
└── docs/              ← Architecture docs
```

## Good first issues

Look for issues labeled [`good first issue`](https://github.com/be2jay67/claude-ns-hub/issues?q=label%3A%22good+first+issue%22) on GitHub.

Typical beginner-friendly tasks:
- Add a missing tooltip / UI label
- Write a test for an existing endpoint
- Fix a typo in docs or add a missing doc section
- Improve error messages

## How to contribute

1. **Open an issue first** — describe what you want to fix/add. We'll align before you write code.
2. Fork → branch → implement → PR. Keep PRs small and focused (one thing per PR).
3. Run `python -m pytest` before submitting (no failing tests).
4. PR description: what changed, why, screenshots for UI changes.

## Development tips

```bash
# Hot-reload server (changes to server.py auto-restart)
uvicorn hub.server:app --reload --port 9001

# Run tests
python -m pytest

# Check types (optional but appreciated)
mypy hub/server.py --ignore-missing-imports
```

The UI (`northstar.html`) has no build step — edit and refresh browser. For major UI changes, describe the interaction flow in your issue first.

## Communication

- GitHub Issues: bug reports, feature requests, questions
- GitHub Discussions: architectural questions, "should we do X?"
- Keep it async — no Discord/Slack yet (project is small)

## Code of conduct

Be direct, be kind, be useful. No gatekeeping. We're building for Claude Code users — if you use it, your opinion matters.
