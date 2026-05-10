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

    try:
        proc = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", "--no-session-persistence"],
            stdin=open(task_file),
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max per task
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
