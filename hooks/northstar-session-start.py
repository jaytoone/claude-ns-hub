#!/usr/bin/env python3
"""
northstar-session-start.py — SessionStart hook
At session start: reads queued milestones for the current project and
injects them into Claude's context as additionalContext.

Claude sees queued milestones → knows what to work on → sets done via Stop hook.
State management is fully automated:
  - User: only add / delete stones
  - Claude: sets queued (this hook), sets done (Stop hook Jaccard match)
"""
import json
import os
import sys
import urllib.request
from pathlib import Path


def _hub_api() -> str:
    import subprocess, re
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=2)
        for line in r.stdout.splitlines():
            if ":9000" in line and "LISTEN" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+):9000", line)
                if m:
                    return f"http://{m.group(1)}:9000"
    except Exception:
        pass
    return "http://127.0.0.1:9000"


def get_project_id(cwd: str) -> str | None:
    DIR_TO_PROJECT = {
        "Moat": "MOAT", "CTX": "CTX", "FromScratch": "FromScratch",
        "Ameva": "Ameva", "EI": "EI", "FRWP": "FRWP",
        "HugwartsBanana": "HugwartsBanana", "AIKB": "AIKB",
        "Clone": "Clone", "FreeOS": "FreeOS",
    }
    path = Path(cwd)
    dir_lower = {k.lower(): v for k, v in DIR_TO_PROJECT.items()}
    for part in path.parts[::-1]:
        if part.lower() in dir_lower:
            return dir_lower[part.lower()]
    projects_dir = Path.home() / ".claude/hub/projects"
    if projects_dir.exists():
        cwd_lower = {p.lower() for p in path.parts}
        for proj_dir in projects_dir.iterdir():
            if proj_dir.is_dir() and proj_dir.name.lower() in cwd_lower:
                return proj_dir.name
    return None


def _ensure_watcher():
    """No-op: daemon watchers removed. server.py asyncio task handles milestone sync."""
    pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    _ensure_watcher()

    cwd = data.get("cwd", os.getcwd())
    proj_id = get_project_id(cwd)
    if not proj_id:
        sys.exit(0)

    hub = _hub_api()
    try:
        req = urllib.request.Request(f"{hub}/api/northstar/{proj_id}/milestones")
        with urllib.request.urlopen(req, timeout=3) as resp:
            ms_data = json.loads(resp.read())
    except Exception:
        sys.exit(0)

    milestones = ms_data.get("milestones", [])
    queued = [m for m in milestones if m.get("status") == "queued"]
    pending = [m for m in milestones if not m.get("done") and (m.get("status") or "pending") == "pending"]
    # Auto-queue removed: pending → queued only via Execute button click (user policy)
    needs_clarification = [m for m in milestones if m.get("status") == "needs_clarification"]
    answered = [m for m in needs_clarification if (m.get("clarification_answer") or "").strip()]
    unanswered = [m for m in needs_clarification if not (m.get("clarification_answer") or "").strip()]

    # Detect pending user replies in conversation threads (last message is from user, not claude)
    pending_replies = []
    for m in milestones:
        conv = m.get("conversation") or []
        if conv and conv[-1].get("role") == "user":
            pending_replies.append(m)

    # Auto-promote answered clarifications → pending (Claude will pick them up as new pending)
    for m in answered:
        try:
            req = urllib.request.Request(
                f"{hub}/api/northstar/{proj_id}/milestones/{m['id']}",
                data=json.dumps({"status": "pending"}).encode(),
                headers={"Content-Type": "application/json"},
                method="PATCH"
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass
    # Refresh after auto-promotion
    if answered:
        try:
            req2 = urllib.request.Request(f"{hub}/api/northstar/{proj_id}/milestones")
            with urllib.request.urlopen(req2, timeout=3) as resp:
                ms_data2 = json.loads(resp.read())
            milestones = ms_data2.get("milestones", [])
            queued = [m for m in milestones if m.get("status") == "queued"]
            pending = [m for m in milestones if not m.get("done") and (m.get("status") or "pending") == "pending"]
        except Exception:
            pass

    if not queued and not pending and not unanswered and not pending_replies:
        sys.exit(0)

    lines = [f"[NS:{proj_id}] Milestone status —"]

    if answered:
        lines.append(f"  AUTO-QUEUED from clarification ({len(answered)} promoted to pending):")
        for m in answered:
            lines.append(f"    • {m.get('text','')[:60]} → answer: \"{m.get('clarification_answer','')[:40]}\"")

    if unanswered:
        lines.append(f"  NEEDS CLARIFICATION ({len(unanswered)} waiting for user input in hub UI):")
        for m in unanswered[:3]:
            lines.append(f"    • {m.get('text','')[:60]}")
            if m.get("clarification_question"):
                lines.append(f"      Q: {m['clarification_question'][:60]}")

    if queued:
        lines.append(f"  QUEUED (work on these first):")
        for m in queued[:3]:
            lines.append(f"    • {m.get('text','')[:80]}")

    if pending:
        lines.append(f"  PENDING ({len(pending)} remaining):")
        for m in pending[:3]:
            lines.append(f"    • {m.get('text','')[:70]}")
        if len(pending) > 3:
            lines.append(f"    ... +{len(pending)-3} more")

    if pending_replies:
        lines.append(f"  CONVERSATION REPLIES AWAITING CLAUDE ({len(pending_replies)} stones):")
        for m in pending_replies[:5]:
            conv = m.get("conversation") or []
            last_user = next((msg for msg in reversed(conv) if msg.get("role") == "user"), None)
            lines.append(f"    • [{m['id']}] {m.get('text','')[:50]}")
            if last_user:
                lines.append(f"      user said: \"{last_user.get('text','')[:80]}\"")
        lines.append("")
        lines.append("  REPLY PROTOCOL: For each pending reply above:")
        lines.append("    1. Read the user's message. If it's a command → do the work first.")
        lines.append(f"    2. Append your reply with append_message (no need to send full array):")
        lines.append(f"       curl -s -X PATCH http://127.0.0.1:9000/api/northstar/{proj_id}/milestones/<MID> \\")
        lines.append(f'         -H "Content-Type: application/json" \\')
        lines.append(f"         -d '{{\"append_message\":{{\"role\":\"claude\",\"text\":\"<reply>\"}}}}' ")
        lines.append("    3. If user asked you to do something — do it, then confirm in the reply.")

    session_id = data.get("session_id", "")
    log_path = f"~/.claude/hub/projects/{proj_id}/completion-log.jsonl"
    lines.append("")
    lines.append("COMPLETION PROTOCOL (mandatory):")
    lines.append(f"  When you complete a milestone this session, write to {log_path}:")
    lines.append(f'  echo \'{{"session_id":"{session_id[:8]}","milestone_id":"MX","evidence":"what you did","timestamp":"$(date -Iseconds)"}}\' >> {log_path}')
    lines.append("  The Stop hook reads this file to mark milestones as pending_confirmation.")
    lines.append("  User confirms within 24h → done. No log entry = Jaccard fallback only.")

    # CRON PROTOCOL removed: server.py _start_milestone_watcher asyncio task handles
    # completion-log → pending_confirmation promotion every 5 min. No per-milestone crons needed.

    # BACKGROUND WATCHER removed: server.py _start_milestone_watcher asyncio task handles
    # all state transitions (ack, completion-log sync, clarification promotion) every 5 min.
    # No CronCreate needed.

    # Autonomous exec session detection: if pending-execute-prompt.txt exists,
    # this session was spawned by Execute — inject full content directly (no file read needed)
    projects_dir = Path.home() / ".claude/hub/projects"
    auto_dispatched = False
    for pdir in projects_dir.iterdir():
        prompt_file = pdir / "pending-execute-prompt.txt"
        if prompt_file.exists():
            try:
                prompt_content = prompt_file.read_text(encoding="utf-8").strip()
                # Delete immediately — one-shot, prevents stale injection into future sessions
                prompt_file.unlink()
            except Exception:
                prompt_content = ""
            if prompt_content:
                lines.append("")
                lines.append("## AUTONOMOUS TASK DISPATCH (Execute button was clicked)")
                lines.append("Execute these instructions NOW without waiting for user input:")
                lines.append("")
                lines.extend(prompt_content.splitlines())
                auto_dispatched = True
            break  # only one project at a time

    msg = "\n".join(lines)

    # Output as additionalContext for Claude
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg
        }
    }))


if __name__ == "__main__":
    main()
