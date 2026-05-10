#!/usr/bin/env python3
"""
hub-inbox-inject.py — UserPromptSubmit hook
Reads ~/.claude/hub/session-inbox.jsonl for pending milestone run requests.
If entries exist, injects them as additionalContext into the current Claude session.
The active Claude session then processes them with full context.
"""
import json
import sys
from pathlib import Path

INBOX = Path.home() / ".claude/hub/session-inbox.jsonl"


def main():
    if not INBOX.exists():
        sys.exit(0)

    lines = [l.strip() for l in INBOX.read_text().splitlines() if l.strip()]
    if not lines:
        sys.exit(0)

    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except Exception:
            pass

    if not entries:
        sys.exit(0)

    # Clear inbox immediately (atomic: write empty)
    INBOX.write_text("")

    parts = ["[HUB MILESTONE RUN REQUEST] Process these milestones now:"]
    for e in entries:
        proj = e.get("proj_id", "?")
        mid = e.get("mid", "?")
        text = e.get("text", "")
        status = e.get("status", "pending")
        hub = e.get("hub_api", "http://100.119.82.4:9000")
        parts.append(f"\n  {proj}/{mid} [{status}]: \"{text}\"")
        parts.append(f"  → PATCH {hub}/api/northstar/{proj}/milestones/{mid}")
        parts.append(f"    claude_ack=now, then implement if clear or set needs_clarification if vague")
        parts.append(f"    On done: write to ~/.claude/hub/projects/{proj}/completion-log.jsonl")
        parts.append(f"    PATCH status=pending_confirmation")

    parts.append("\nProcess these BEFORE responding to the user's message.")
    ctx = "\n".join(parts)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx
        }
    }))


if __name__ == "__main__":
    main()
