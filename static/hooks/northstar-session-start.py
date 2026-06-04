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
    """Discover hub API URL. NS_HUB_URL env var takes priority (dev/prod branching)."""
    import subprocess, re
    if url := os.environ.get("NS_HUB_URL"):
        return url
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=2)
        for line in r.stdout.splitlines():
            if ":9001" in line and "LISTEN" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+):9001", line)
                if m:
                    return f"http://{m.group(1)}:9001"
    except Exception:
        pass
    return "http://127.0.0.1:9001"


def _get_milestones_db_or_api(proj_id: str, hub: str) -> dict | None:
    """Read milestones from SQLite direct first (~1ms), fallback to HTTP API (~50ms).
    Returns None on complete failure."""
    from pathlib import Path as _P
    db_path = _P.home() / ".hub" / "ns-events.db"
    if db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path), timeout=2)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT data_json FROM milestones_store WHERE proj_id=?", (proj_id,)
            ).fetchall()
            conn.close()
            milestones = []
            for row in rows:
                try:
                    milestones.append(json.loads(row["data_json"]))
                except Exception:
                    pass
            if milestones:
                return {"milestones": milestones}
        except Exception:
            pass
    # HTTP fallback
    try:
        req = urllib.request.Request(f"{hub}/api/northstar/{proj_id}/milestones")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


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
    projects_dir = Path.home() / ".hub" / "projects"
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
    ms_data = _get_milestones_db_or_api(proj_id, hub)
    if ms_data is None:
        sys.exit(0)

    milestones = ms_data.get("milestones", [])

    # M160: a stone whose last conversation entry is from claude is awaiting user reply.
    # Such stones must NOT be auto-run — they are paused until the user responds.
    def _awaits_user(m):
        conv = m.get("conversation") or []
        return bool(conv) and isinstance(conv, list) and (conv[-1] or {}).get("role") == "claude"

    queued = [m for m in milestones if m.get("status") == "queued" and not _awaits_user(m)]
    paused_awaiting_user = [m for m in milestones
                            if m.get("status") in ("queued", "pending") and _awaits_user(m)]
    pending = [m for m in milestones
               if not m.get("done") and (m.get("status") or "pending") == "pending" and not _awaits_user(m)]
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
            ms_data2 = _get_milestones_db_or_api(proj_id, hub) or {}
            milestones = ms_data2.get("milestones", [])
            queued = [m for m in milestones if m.get("status") == "queued" and not _awaits_user(m)]
            paused_awaiting_user = [m for m in milestones
                                    if m.get("status") in ("queued", "pending") and _awaits_user(m)]
            pending = [m for m in milestones
                       if not m.get("done") and (m.get("status") or "pending") == "pending" and not _awaits_user(m)]
        except Exception:
            pass

    if not queued and not pending and not unanswered and not pending_replies and not paused_awaiting_user:
        sys.exit(0)

    lines = [f"[NS:{proj_id}] Milestone status —"]

    # M150: REPLY PROTOCOL surfaced FIRST + made MANDATORY so Claude never silently skips a user reply.
    if pending_replies:
        lines.append("")
        lines.append(f"  ★ MANDATORY REPLY (do BEFORE anything else): {len(pending_replies)} stone(s) have a user message awaiting your comment.")
        lines.append("    For each stone listed below you MUST append a claude reply via append_message.")
        lines.append("    This is NON-OPTIONAL — even a one-line acknowledgement counts.")
        lines.append("    If the message is a command → do the work, then reply confirming what you did.")
        lines.append("    If the message is a question → reply with the answer in the same turn.")
        lines.append("    Skipping = the user re-asks; do not skip.")
        lines.append("")
        lines.append(f"  CONVERSATION REPLIES AWAITING CLAUDE ({len(pending_replies)} stones):")
        for m in pending_replies[:5]:
            conv = m.get("conversation") or []
            recent = conv[-3:] if len(conv) >= 3 else conv
            lines.append(f"    • [{m['id']}] {m.get('text','')[:50]}")
            for msg in recent:
                role = msg.get("role", "?")
                text = msg.get("text", "")[:100]
                prefix = "      user" if role == "user" else "      claude"
                lines.append(f"{prefix}: \"{text}\"")
        lines.append("")
        lines.append("  REPLY COMMAND (one curl per stone, REQUIRED — copy and adapt):")
        hub_url = os.environ.get("NS_HUB_URL", "http://127.0.0.1:9001")
        lines.append(f"    curl -s -X PATCH {hub_url}/api/northstar/{proj_id}/milestones/<MID> \\")
        lines.append(f'      -H "Content-Type: application/json" \\')
        lines.append(f"      -d '{{\"append_message\":{{\"role\":\"claude\",\"text\":\"<your reply>\"}}}}' ")
        lines.append("  ENFORCEMENT: server re-fires the trigger every 5 min until last_msg.role == 'claude'.")
        lines.append("")

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

    if paused_awaiting_user:
        lines.append("")
        lines.append(f"  PAUSED — awaiting user reply ({len(paused_awaiting_user)} stones; DO NOT run, even if queued):")
        for m in paused_awaiting_user[:5]:
            lines.append(f"    • [{m.get('id')}] {m.get('text','')[:60]}")
        lines.append("  (M160 gate: user must reply to Claude's comment before these stones may be executed.)")
        lines.append("")

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

    session_id = data.get("session_id", "")
    log_path = f"~/.hub/projects/{proj_id}/completion-log.jsonl"
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
    # M747: NS_SUBSTAR_SHORT set for per-substar sessions → look for substar-specific prompt file
    projects_dir = Path.home() / ".hub" / "projects"
    auto_dispatched = False
    _substar_short = os.environ.get("NS_SUBSTAR_SHORT", "").strip()
    _prompt_filename = f"pending-execute-prompt-{_substar_short}.txt" if _substar_short else "pending-execute-prompt.txt"
    for pdir in projects_dir.iterdir():
        prompt_file = pdir / _prompt_filename
        if not prompt_file.exists() and not _substar_short:
            # Fallback: scan for substar prompt files in case NS_SUBSTAR_SHORT wasn't inherited
            pass
        if prompt_file.exists():
            try:
                prompt_content = prompt_file.read_text(encoding="utf-8").strip()
                # Delete immediately — one-shot, prevents stale injection into future sessions
                prompt_file.unlink()
            except Exception:
                prompt_content = ""
            if prompt_content:
                lines.append("")
                lines.append("## AUTONOMOUS TASK DISPATCH (via Execute button)")
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
