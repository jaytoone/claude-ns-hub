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


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

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

    if not queued and not pending:
        sys.exit(0)

    lines = [f"[NS:{proj_id}] Milestone status —"]

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
    log_path = f"~/.claude/hub/projects/{proj_id}/completion-log.jsonl"
    lines.append("")
    lines.append("COMPLETION PROTOCOL (mandatory):")
    lines.append(f"  When you complete a milestone this session, write to {log_path}:")
    lines.append(f'  echo \'{{"session_id":"{session_id[:8]}","milestone_id":"MX","evidence":"what you did","timestamp":"$(date -Iseconds)"}}\' >> {log_path}')
    lines.append("  The Stop hook reads this file to mark milestones as pending_confirmation.")
    lines.append("  User confirms within 24h → done. No log entry = Jaccard fallback only.")

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
