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

    # Consume pending-execute-prompt.txt (one-shot, delete immediately) regardless of MCP state.
    import subprocess as _sp
    projects_dir = Path.home() / ".hub" / "projects"
    _substar_short = os.environ.get("NS_SUBSTAR_SHORT", "").strip()
    _prompt_filename = f"pending-execute-prompt-{_substar_short}.txt" if _substar_short else "pending-execute-prompt.txt"
    _legacy_prompt_content = ""
    for _pdir in projects_dir.iterdir():
        _prompt_file = _pdir / _prompt_filename
        if _prompt_file.exists():
            try:
                _legacy_prompt_content = _prompt_file.read_text(encoding="utf-8").strip()
                _prompt_file.unlink()
            except Exception:
                _legacy_prompt_content = ""
            break

    # M1174: Always use direct injection path (LLM-independent).
    # MCP path removed — hub injects stone content directly so LLM never needs to call get_pending_task.

    # Pick the stone to dispatch: queued first, then pending_replies
    _dispatch_stone = (queued or pending_replies or [None])[0]
    if _dispatch_stone:
        _stone_id = _dispatch_stone.get("id") or ""
        # Register as active stone in hub (for auto-reply + auto-complete worker)
        try:
            _body = json.dumps({"stone_id": _stone_id}).encode()
            _req = urllib.request.Request(
                f"{_hub_api()}/api/northstar/{proj_id}/active-stone",
                data=_body, method="POST",
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(_req, timeout=3)
        except Exception:
            pass

    # M1174: Direct content injection (LLM-independent, no MCP tools needed)
    total_work = len(queued) + len(pending_replies) + len(unanswered)
    lines = [f"[NS:{proj_id}] {total_work} item(s) — direct dispatch (hub-mcp not required):"]

    if pending_replies:
        lines.append("")
        lines.append(f"  ★ Q&A REPLY NEEDED ({len(pending_replies)} stone(s)):")
        lines.append("    Work on these — auto-reply will be harvested from your response when idle.")
        lines.append("")
        for m in pending_replies[:3]:
            conv = m.get("conversation") or []
            lines.append(f"    [{m.get('id','')}] {m.get('text','')[:80]}")
            # Include full recent conversation for context
            for msg_entry in conv[-4:]:
                role = msg_entry.get("role", "?")
                text = msg_entry.get("text", "")[:200]
                lines.append(f"      {role}: {text}")

    if unanswered:
        lines.append(f"  NEEDS CLARIFICATION ({len(unanswered)}):")
        for m in unanswered[:3]:
            lines.append(f"    • [{m.get('id','')}] {m.get('text','')[:80]}")
            if m.get("clarification_question"):
                lines.append(f"      Q: {m['clarification_question'][:80]}")

    if paused_awaiting_user:
        lines.append(f"  PAUSED ({len(paused_awaiting_user)} — DO NOT run):")
        for m in paused_awaiting_user[:3]:
            lines.append(f"    • [{m.get('id','')}] {m.get('text','')[:60]}")

    if queued:
        lines.append(f"  QUEUED — pick the first one and work on it:")
        for m in queued[:3]:
            lines.append(f"    [{m.get('id','')}] {m.get('text','')}")
            # Include parent context if available
            if m.get("parent_id"):
                lines.append(f"      (child of {m['parent_id']})")

    if pending:
        lines.append(f"  PENDING ({len(pending)}) — for reference:")
        for m in pending[:3]:
            lines.append(f"    • [{m.get('id','')}] {m.get('text','')[:70]}")
        if len(pending) > 3:
            lines.append(f"    ... +{len(pending)-3} more")

    lines.append("")
    lines.append("PROTOCOL (M1174 LLM-independent):")
    lines.append("  • Work on the task. When done, commit your changes with git.")
    lines.append("  • Auto-completion: hub detects idle + new git commit → transitions stone automatically.")
    lines.append("  • Auto-reply: hub harvests your last response from transcript when idle.")
    lines.append("  • You do NOT need to call reply_to_stone or report_task_complete.")

    if _legacy_prompt_content:
        lines.append("")
        lines.append("## AUTONOMOUS TASK DISPATCH (via Execute button)")
        lines.append("Execute these instructions NOW without waiting for user input:")
        lines.append("")
        lines.extend(_legacy_prompt_content.splitlines())

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


if __name__ == "__main__":
    main()
