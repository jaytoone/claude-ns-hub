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

    parts = ["[HUB INBOX] Process these requests BEFORE responding to the user:"]
    for e in entries:
        etype = e.get("type", "run")
        proj = e.get("proj_id", "?")
        hub = e.get("hub_api", "http://100.119.82.4:9000")

        if etype == "execute_init":
            parts.append(f"\n[EXECUTE INIT] {proj} has no milestones.")
            parts.append(f"  → Use /ns-stone to analyze project and create milestone roadmap")
            parts.append(f"  → Project name: {e.get('proj_name', proj)}")
            parts.append(f"  → After creating milestones, queue the first actionable one")

        elif etype == "execute_work":
            first = e.get("first_milestone")
            parts.append(f"\n[EXECUTE WORK] {proj}: {e.get('queued_count',0)} queued, {e.get('pending_count',0)} pending")
            if first:
                mid = first.get("id", "?")
                text = first.get("text", "")
                status = first.get("status", "pending")
                parts.append(f"  → First item: {mid} [{status}]: \"{text}\"")
                parts.append(f"  → PATCH claude_ack=now: {hub}/api/northstar/{proj}/milestones/{mid}")
                parts.append(f"  → Implement it, write completion-log, PATCH status=pending_confirmation")
            else:
                parts.append(f"  → No actionable items found. Check milestone states.")

        else:
            # Legacy: individual milestone run
            mid = e.get("mid", "?")
            text = e.get("text", "")
            status = e.get("status", "pending")
            parts.append(f"\n[RUN] {proj}/{mid} [{status}]: \"{text}\"")
            parts.append(f"  → PATCH {hub}/api/northstar/{proj}/milestones/{mid}")
            parts.append(f"    claude_ack=now, implement if clear or needs_clarification if vague")
            parts.append(f"    On done: write completion-log, PATCH status=pending_confirmation")
    ctx = "\n".join(parts)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx
        }
    }))


if __name__ == "__main__":
    main()
