#!/usr/bin/env python3
"""
northstar-notify-status.py — Notification hook
When Claude sends a notification (waiting for user input), mark the
project's session status pill as WAITING in the hub dashboard.
"""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path


def _hub_api() -> str:
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


def auto_detect_project(cwd: str) -> str | None:
    PROJECTS_DIR = Path.home() / ".claude/hub/projects"
    if not PROJECTS_DIR.exists():
        return None
    cwd_lower = {p.lower() for p in Path(cwd).parts}
    for proj_dir in PROJECTS_DIR.iterdir():
        if proj_dir.name.lower() in cwd_lower:
            return proj_dir.name
    return None


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        data = {}

    cwd = data.get("cwd", os.getcwd())
    proj_id = auto_detect_project(cwd)
    if not proj_id:
        sys.exit(0)

    hub = _hub_api()
    try:
        payload = json.dumps({"status": "WAITING"}).encode()
        req = urllib.request.Request(
            f"{hub}/api/northstar/{proj_id}/session-status",
            data=payload, headers={"Content-Type": "application/json"}, method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=2):
            pass
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
