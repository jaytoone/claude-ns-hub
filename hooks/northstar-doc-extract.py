#!/usr/bin/env python3
"""
northstar-doc-extract.py — PostToolUse hook (Write|Edit)

Fires when Claude writes/edits a session-status document.
Auto-detects which North Star project is active (scans ~/.claude/hub/projects/).
Extracts current metric value + summary, posts to hub API.

Generic: no hardcoded project names. Adding a new project =
  create ~/.claude/hub/projects/NewName/north-star.md
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

def _hub_api() -> str:
    """Find the hub API URL — checks Tailscale IP first, then localhost."""
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
PROJECTS_DIR = Path.home() / ".claude/hub/projects"

# Patterns that identify a session-status document
STATUS_PATTERNS = [
    r'\d{8}-.*status',           # 20260507-distillation-session-status.md
    r'session[-_]status',        # session-status.md
    r'\d{8}-.*session',          # 20260507-anything-session.md
    r'daily[-_]update',          # daily-update.md
    r'\d{8}-.*progress',         # 20260507-progress.md
    r'status[-_]snapshot',       # status-snapshot.md
]

def is_status_doc(file_path: str) -> bool:
    fname = Path(file_path).name.lower()
    return any(re.search(p, fname) for p in STATUS_PATTERNS)


def auto_detect_project(cwd: str) -> str | None:
    """Scan ~/.claude/hub/projects/ to find matching project for CWD."""
    if not PROJECTS_DIR.exists():
        return None

    cwd_parts = set(Path(cwd).parts)
    cwd_parts_lower = {p.lower() for p in cwd_parts}

    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        # Case-insensitive match by folder name
        if proj_dir.name.lower() in cwd_parts_lower:
            return proj_dir.name
        # Match by north-star.md `name:` field (case-insensitive)
        md = proj_dir / "north-star.md"
        if md.exists():
            try:
                content = md.read_text(encoding="utf-8")
                m = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
                if m and m.group(1).strip().lower() in cwd_parts_lower:
                    return proj_dir.name
            except Exception:
                pass
    return None


def extract_current_value(content: str) -> str | None:
    """Try to extract a metric value from document content."""
    patterns = [
        r'(\d+(?:\.\d+)?%)\s*(?:\(|baseline|confirmed)',   # 85% baseline confirmed
        r'current[:\s]+(\d+(?:\.\d+)?%)',                   # current: 85%
        r'(\d+)/(\d+)\s*=\s*(\d+(?:\.\d+)?%)',             # 17/20 = 85%
        r'(\d+(?:\.\d+)?%)\s+\((\d+)/(\d+)\)',             # 85% (17/20)
    ]
    for pat in patterns:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            # Return the percentage match
            return m.group(1) if m.lastindex >= 1 else None
    return None


def extract_summary(content: str, max_chars: int = 140) -> str:
    """Extract a brief summary from the first meaningful lines."""
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith('#')]
    if not lines:
        return ""
    # Try to find a table row or status line
    for line in lines[:10]:
        if '|' in line and len(line) > 20:
            continue  # skip table separator lines
        if re.search(r'(done|running|complete|training|eval|status)', line, re.I):
            return line[:max_chars]
    return lines[0][:max_chars] if lines else ""


def post_json(url: str, data: dict, timeout: int = 3) -> bool:
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception:
        return False


def main():
    try:
        raw = sys.stdin.read()
        hook_data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    # Only fire on Write or Edit tool
    tool_name = hook_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Only fire on session-status documents
    if not is_status_doc(file_path):
        sys.exit(0)

    # Detect project
    cwd = hook_data.get("cwd", os.getcwd())
    proj_id = auto_detect_project(cwd)
    if not proj_id:
        sys.exit(0)

    # Read the file content
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        sys.exit(0)

    today = datetime.now().strftime("%Y-%m-%d")

    # Extract summary for log entry
    # Use filename date + first meaningful content line
    fname_date = re.search(r'(\d{4}-\d{2}-\d{2}|\d{8})', Path(file_path).name)
    doc_date = fname_date.group(1).replace('', '-') if fname_date else today
    # Normalize 20260507 → 2026-05-07
    if len(doc_date) == 8 and '-' not in doc_date:
        doc_date = f"{doc_date[:4]}-{doc_date[4:6]}-{doc_date[6:]}"

    summary = extract_summary(content)
    log_text = f"[auto] {Path(file_path).name}: {summary}" if summary else f"[auto] {Path(file_path).name}"
    log_text = log_text[:200]

    # Post session log entry
    post_json(
        f"{HUB_API}/api/northstar/{proj_id}/session-log",
        {"date": today, "text": log_text}
    )

    # Try to update current metric value
    current = extract_current_value(content)
    if current:
        post_json(
            f"{HUB_API}/api/northstar/{proj_id}/update-current",
            {"current": current}
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
