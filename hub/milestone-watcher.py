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
PID_FILE = Path(os.environ.get("HUB_WATCHER_PID", "/tmp/hub-milestone-watcher.pid"))


def write_notification(proj_id: str, event: str):
    entry = json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "project": proj_id,
        "event": event,
    })
    with open(NOTIFY_LOG, "a") as f:
        f.write(entry + "\n")


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
