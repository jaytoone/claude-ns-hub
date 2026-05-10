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

        elif etype in ("execute_work", "execute_all"):
            stones = e.get("stones", [])
            parts.append(f"\n[EXECUTE ALL] {proj}: {len(stones)} actionable stones detected.")
            parts.append(f"  For EACH stone below, create a CronCreate(cron='*/1 * * * *', recurring=False) that:")
            parts.append(f"  1. Checks if the stone is done (reads completion-log)")
            parts.append(f"  2. If not done: ack it + implement it + write completion-log + PATCH pending_confirmation")
            parts.append(f"  3. CronDelete itself after completing")
            parts.append(f"  4. Uses hub_api: {hub}")
            parts.append(f"")
            parts.append(f"  Stones to process:")
            for s in stones:
                mid = s.get("id", "?")
                text = s.get("text", "")[:50]
                status = s.get("status", "pending")
                acked = "acked" if s.get("claude_ack") else "unacked"
                parts.append(f"    {mid} [{status}/{acked}]: \"{text}\"")
            parts.append(f"")
            parts.append(f"  Create ONE CronCreate per stone NOW. Each cron runs independently.")
            parts.append(f"  Cron prompt template for each stone MID:")
            parts.append(f"    'Check {proj}/MID: if not done → PATCH ack + implement + write ~/.claude/hub/projects/{proj}/completion-log.jsonl + PATCH pending_confirmation {hub}/api/northstar/{proj}/milestones/MID, then CronDelete this job.'")

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
