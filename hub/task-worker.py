#!/usr/bin/env python3
"""
task-worker.py — inotify-based autonomous Claude task worker
Watches task-queue/*.md → runs claude --print → writes task-results/

Usage: python3 ~/.claude/hub/task-worker.py &
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import pyinotify

QUEUE_DIR = Path(os.environ.get("HUB_TASK_QUEUE", Path.home() / ".claude/hub/task-queue"))
RESULT_DIR = Path(os.environ.get("HUB_TASK_RESULTS", Path.home() / ".claude/hub/task-results"))
LOCK_DIR = Path(os.environ.get("HUB_TASK_LOCKS", Path.home() / ".claude/hub/task-locks"))
LOG_FILE = Path(os.environ.get("HUB_WORKER_LOG", "/tmp/hub-task-worker.log"))
PID_FILE = Path("/tmp/hub-task-worker.pid")

# Project ID → working directory mapping for --continue context loading
PROJECT_DIRS: dict[str, Path] = {}
def _find_project_dirs():
    base = Path("/home/desk-1/Project")
    known = {"MOAT": "Moat", "CTX": "CTX", "FromScratch": "FromScratch",
             "HugwartsBanana": "VIDraft/HugwartsBanana", "AIKB": "AIKB",
             "FRWP": "FRWP", "Clone": "Clone", "EI": "EI", "FreeOS": "FreeOS"}
    for proj_id, rel in known.items():
        d = base / rel
        if d.exists():
            PROJECT_DIRS[proj_id] = d
_find_project_dirs()

for d in [QUEUE_DIR, RESULT_DIR, LOCK_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def process_task(task_file: Path):
    task_id = task_file.stem
    lock = LOCK_DIR / f"{task_id}.lock"
    result = RESULT_DIR / f"{task_id}.json"

    if lock.exists() or result.exists():
        return  # already processing or done

    lock.touch()
    log(f"Processing: {task_id}")

    # Extract proj_id from task filename (task-PROJID-...)
    parts = task_id.split("-")
    proj_id = parts[1] if len(parts) > 1 else None
    proj_dir = PROJECT_DIRS.get(proj_id) if proj_id else None
    prompt = task_file.read_text(encoding="utf-8")

    try:
        if proj_dir and proj_dir.exists():
            # Use --continue to load latest session context for this project
            cmd = ["claude", "--dangerously-skip-permissions", "--continue", "--print", prompt]
            cwd = str(proj_dir)
            log(f"Using -c context for {proj_id} in {proj_dir}")
        else:
            # Fallback: fresh headless session
            cmd = ["claude", "--print", "--dangerously-skip-permissions", "--no-session-persistence", prompt]
            cwd = None

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=cwd,
        )
        output = proc.stdout + proc.stderr
        status = "done" if proc.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        output = "Task timed out after 300s"
        status = "timeout"
    except Exception as e:
        output = str(e)
        status = "error"
    finally:
        lock.unlink(missing_ok=True)

    result.write_text(json.dumps({
        "task_id": task_id,
        "task_file": str(task_file),
        "status": status,
        "output": output,
        "completed_at": datetime.now().isoformat(),
    }, ensure_ascii=False, indent=2))
    log(f"Done: {task_id} [{status}]")


class Handler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        f = Path(event.pathname)
        if f.suffix == ".md":
            # Run in thread to avoid blocking inotify
            import threading
            threading.Thread(target=process_task, args=(f,), daemon=True).start()


def run():
    PID_FILE.write_text(str(os.getpid()))
    log(f"Task worker started (PID={os.getpid()}), watching {QUEUE_DIR}")

    # Process existing pending tasks on startup
    import threading
    for f in sorted(QUEUE_DIR.glob("*.md")):
        result = RESULT_DIR / f"{f.stem}.json"
        if not result.exists():
            threading.Thread(target=process_task, args=(f,), daemon=True).start()

    wm = pyinotify.WatchManager()
    wm.add_watch(str(QUEUE_DIR), pyinotify.IN_CLOSE_WRITE)
    notifier = pyinotify.Notifier(wm, Handler())
    try:
        notifier.loop()
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    run()
