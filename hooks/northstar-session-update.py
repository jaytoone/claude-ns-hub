#!/usr/bin/env python3
"""
northstar-session-update.py — Stop hook
Appends a session summary to the matching North Star project's progress log.
Fires on every Claude Code session end (Stop event).

Works like CTX's git-memory.py: reads recent git commits from CWD,
maps to a North Star project, posts to the hub API.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
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

HUB_API = _hub_api()

# CWD → North Star project ID mapping
# Add entries here as you add new projects
DIR_TO_PROJECT = {
    "Moat":        "MOAT",
    "CTX":         "CTX",
    "FromScratch": "FromScratch",
    "Ameva":       "Ameva",
    "EI":          "EI",
}

def get_project_id(cwd: str) -> str | None:
    """Map current directory to a North Star project ID.
    Uses case-insensitive matching + auto-scans projects dir."""
    path = Path(cwd)
    # 1. Check hardcoded map (case-insensitive)
    dir_lower = {k.lower(): v for k, v in DIR_TO_PROJECT.items()}
    for part in path.parts[::-1]:
        if part.lower() in dir_lower:
            return dir_lower[part.lower()]
    # 2. Auto-scan ~/.claude/hub/projects/ (generic fallback)
    import re
    projects_dir = Path.home() / ".claude/hub/projects"
    if projects_dir.exists():
        cwd_lower = {p.lower() for p in path.parts}
        for proj_dir in projects_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            if proj_dir.name.lower() in cwd_lower:
                return proj_dir.name
    return None


def jaccard_similarity(a: str, b: str) -> float:
    """Token overlap between two strings (Jaccard on word sets)."""
    ta = set(re.sub(r'[^\w\s]', ' ', a.lower()).split())
    tb = set(re.sub(r'[^\w\s]', ' ', b.lower()).split())
    # Filter very short tokens
    ta = {t for t in ta if len(t) > 2}
    tb = {t for t in tb if len(t) > 2}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# Commit prefixes/words that strongly signal task completion
_DONE_SIGNALS = {
    'feat', 'fix', 'done', 'complete', 'completed', 'finish', 'finished',
    'ship', 'shipped', 'implement', 'implemented', 'add', 'added',
    'close', 'closed', 'resolve', 'resolved', 'pass', 'passed',
    'success', '✓', 'achieve', 'achieve', 'deploy', 'deployed',
}


def _commit_implies_done(commit_text: str) -> bool:
    """Return True if the commit message implies a task was completed."""
    tokens = set(re.sub(r'[^\w✓]', ' ', commit_text.lower()).split())
    return bool(tokens & _DONE_SIGNALS)


def try_ack_milestones(proj_id: str, commits: list[str]) -> int:
    """Check milestones against commit text.
    - claude_ack written when match >= 0.55
    - done=True also set when match >= 0.65 AND commit implies completion
    """
    import urllib.request
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
    acked = 0
    try:
        req = urllib.request.Request(f"{HUB_API}/api/northstar/{proj_id}/milestones")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        # Process all undone milestones (acked or not — re-check for auto-done)
        milestones = [m for m in data.get("milestones", []) if not m.get("done")]
        if not milestones:
            return 0

        corpus = " ".join(commits)
        commits_imply_done = _commit_implies_done(corpus)

        for m in milestones:
            mid = m.get("id", "")
            text = m.get("text", "")
            if not mid or not text:
                continue
            score = jaccard_similarity(text, corpus)
            if score < 0.55:
                continue

            # Build patch payload
            patch = {}
            if not m.get("claude_ack"):
                patch["claude_ack"] = now_iso
            # Auto-mark done if strong match + commit signals completion
            if score >= 0.65 and commits_imply_done:
                patch["done"] = True

            if not patch:
                continue

            payload = json.dumps(patch).encode()
            patch_req = urllib.request.Request(
                f"{HUB_API}/api/northstar/{proj_id}/milestones/{mid}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="PATCH",
            )
            with urllib.request.urlopen(patch_req, timeout=3) as r:
                json.loads(r.read())
            acked += 1
    except Exception:
        pass
    return acked


def get_recent_commits(cwd: str, n: int = 3) -> list[str]:
    """Get the N most recent git commits in the session."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}", "--no-merges"],
            cwd=cwd, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []


def get_session_info(input_data: dict) -> dict:
    """Extract session info from Stop hook input."""
    return {
        "cwd": input_data.get("cwd", os.getcwd()),
        "session_id": input_data.get("session_id", "")[:12],
    }


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    info = get_session_info(data)
    cwd = info["cwd"]

    proj_id = get_project_id(cwd)
    if not proj_id:
        sys.exit(0)  # Not a tracked project — exit silently

    # Get recent commits as session summary
    commits = get_recent_commits(cwd, n=3)
    if not commits:
        sys.exit(0)  # No commits this session — skip

    # Build summary text
    today = datetime.now().strftime("%Y-%m-%d")
    summary = "; ".join(commits[:2])  # top 2 commits, joined
    if len(commits) > 2:
        summary += f" (+{len(commits)-2} more)"

    # Post session log entry
    try:
        import urllib.request
        payload = json.dumps({"date": today, "text": summary}).encode()
        req = urllib.request.Request(
            f"{HUB_API}/api/northstar/{proj_id}/session-log",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            json.loads(resp.read())
    except Exception:
        pass  # Hub offline or error — fail silently

    # P3: Try to acknowledge milestones mentioned in commits
    try_ack_milestones(proj_id, commits)

    # P4: Set session status pill to IDLE on session end
    try:
        payload = json.dumps({"status": "IDLE"}).encode()
        req = urllib.request.Request(
            f"{HUB_API}/api/northstar/{proj_id}/session-status",
            data=payload, headers={"Content-Type": "application/json"}, method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=2):
            pass
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
