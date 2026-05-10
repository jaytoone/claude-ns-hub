#!/usr/bin/env python3
"""
milestone-watcher.py — inotify-based zero-cost milestone change detector.
Watches north-star.md files for writes → appends to notifications.log.
Claude reads notifications.log instead of polling the API every N minutes.

Usage: python3 milestone-watcher.py [--projects-dir DIR] &
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = Path(os.environ.get("HUB_PROJECTS_DIR", Path.home() / ".claude/hub/projects"))
NOTIFY_LOG = Path(os.environ.get("HUB_NOTIFY_LOG", Path.home() / ".claude/hub/notifications.log"))
TASK_QUEUE = Path(os.environ.get("HUB_TASK_QUEUE", Path.home() / ".claude/hub/task-queue"))
PID_FILE = Path(os.environ.get("HUB_WATCHER_PID", "/tmp/hub-milestone-watcher.pid"))

HUB_API = os.environ.get("HUB_API", "http://100.119.82.4:9000")


def write_notification(proj_id: str, event: str):
    entry = json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "project": proj_id,
        "event": event,
    })
    with open(NOTIFY_LOG, "a") as f:
        f.write(entry + "\n")


def dispatch_task(proj_id: str):
    """Write a task file for the worker to process via claude --print."""
    import urllib.request, yaml
    TASK_QUEUE.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(f"{HUB_API}/api/northstar/{proj_id}/milestones")
        with urllib.request.urlopen(req, timeout=3) as resp:
            ms_data = json.loads(resp.read())
        new_ms = [m for m in ms_data.get("milestones", [])
                  if m.get("status") == "pending" and not m.get("claude_ack")]
        if not new_ms:
            return
        ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:19]
        task_file = TASK_QUEUE / f"task-{proj_id}-{ts}.md"
        lines = [
            f"# Milestone Queue Task: {proj_id}",
            f"",
            f"New unacknowledged milestones detected in project {proj_id}.",
            f"For each milestone below:",
            f"1. PATCH claude_ack=now to {HUB_API}/api/northstar/{proj_id}/milestones/{{id}}",
            f"2. If text is clear (>15 chars, specific task) → also PATCH status=queued",
            f"3. If vague or question → PATCH status=needs_clarification + clarification_question",
            f"4. For the first queued milestone: implement it, write completion-log, PATCH pending_confirmation",
            f"",
            f"## New Milestones:",
        ]
        for m in new_ms[:3]:
            lines.append(f"- {m.get('id')}: \"{m.get('text', '')}\"")
        task_file.write_text("\n".join(lines))
    except Exception as e:
        write_notification(proj_id, f"task-dispatch-error: {e}")


def get_watched_paths() -> dict:
    """Return {path_str: proj_id} for all north-star.md files."""
    paths = {}
    if PROJECTS_DIR.exists():
        for proj_dir in PROJECTS_DIR.iterdir():
            md = proj_dir / "north-star.md"
            if md.exists():
                paths[str(md)] = proj_dir.name
    return paths


def run():
    import pyinotify

    PID_FILE.write_text(str(os.getpid()))

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE

    class Handler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            proj_id = get_watched_paths().get(event.pathname, "unknown")
            write_notification(proj_id, "north-star-updated")
            # Dispatch task to worker queue for autonomous processing
            dispatch_task(proj_id)

    notifier = pyinotify.Notifier(wm, Handler())

    # Watch all existing north-star.md files
    paths = get_watched_paths()
    for path in paths:
        wm.add_watch(path, mask)

    # Also watch the projects dir for new projects
    wm.add_watch(str(PROJECTS_DIR), pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO)

    print(f"[milestone-watcher] watching {len(paths)} projects → {NOTIFY_LOG}", flush=True)

    try:
        notifier.loop()
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    run()
