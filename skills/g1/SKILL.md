---
name: g1
description: "Utility command (memory write) — appends a decision/judgment to .omc/session-decisions.md for cross-session recall. Not a scaffold or agent; a single-operation CLI command. Usage: /g1 [decision text]"
---

## Protocol

1. Parse args as the decision text (everything after `/g1`)
2. Get current datetime: `date +"%Y-%m-%d %H:%M"`
3. Determine project root: `git rev-parse --show-toplevel 2>/dev/null || pwd`
4. Append to `{project_root}/.omc/session-decisions.md`:
   ```
   > {YYYY-MM-DD HH:MM}: {decision text}
   ```
   - Create file if not exists (mkdir -p .omc first)
5. Confirm: "G1 recorded: {decision text}"

## Example
/g1 topic-dedup optimizes topic diversity, not retention (age=15 measured)

→ appends: `> 2026-04-08 13:30: topic-dedup optimizes topic diversity, not retention (age=15 measured)`
