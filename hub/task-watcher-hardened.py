#!/usr/bin/env python3
"""
task-watcher-hardened.py — Crash-recovery task queue watcher
- Reads project task-queue.jsonl (persistent, survives crashes)
- Processes each task via claude --continue --print
- Exponential backoff on 429/529 API errors
- Resumes from last incomplete task after crash
- Writes detailed audit log

Usage: python3 ~/.claude/hub/task-watcher-hardened.py [PROJ_ID]
       (default: watches all projects)
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HUB = Path.home() / ".claude/hub"
PROJECTS_DIR = HUB / "projects"
PID_FILE = Path("/tmp/hub-task-watcher.pid")
LOG = Path("/tmp/hub-task-watcher.log")

PROJECT_DIRS = {
    "MOAT": Path("/home/desk-1/Project/Moat"),
    "CTX": Path("/home/desk-1/Project/CTX"),
    "FromScratch": Path("/home/desk-1/Project/FromScratch"),
    "HugwartsBanana": Path("/home/desk-1/Project/VIDraft/HugwartsBanana"),
    "AIKB": Path("/home/desk-1/Project/AIKB"),
    "FRWP": Path("/home/desk-1/Project/FRWP"),
    "Clone": Path("/home/desk-1/Project/Clone"),
    "EI": Path("/home/desk-1/Project/EI"),
    "FreeOS": Path("/home/desk-1/Project/FreeOS"),
}

# Backoff config
BACKOFF_INITIAL = 30   # seconds
BACKOFF_MAX = 600      # 10 minutes max
BACKOFF_MULT = 2.0
MAX_RETRIES = 8


def log(msg: str):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def get_task_queue(proj_id: str) -> list:
    queue_file = PROJECTS_DIR / proj_id / "task-queue.jsonl"
    if not queue_file.exists():
        return []
    tasks = []
    for line in queue_file.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                tasks.append(json.loads(line))
            except Exception:
                pass
    return tasks


def update_task_status(proj_id: str, task_id: str, status: str, result: str = ""):
    queue_file = PROJECTS_DIR / proj_id / "task-queue.jsonl"
    if not queue_file.exists():
        return
    tasks = get_task_queue(proj_id)
    updated = False
    for t in tasks:
        if t.get("id") == task_id:
            t["status"] = status
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            if result:
                t["result"] = result[:500]
            updated = True
    if updated:
        queue_file.write_text("\n".join(json.dumps(t, ensure_ascii=False) for t in tasks) + "\n")


def run_task(proj_id: str, task: dict) -> tuple[bool, str]:
    """Run a task with exponential backoff on API errors. Returns (success, output)."""
    task_id = task.get("id", "?")
    prompt = task.get("prompt", "")
    proj_dir = PROJECT_DIRS.get(proj_id)

    backoff = BACKOFF_INITIAL
    for attempt in range(MAX_RETRIES):
        log(f"[{proj_id}/{task_id}] attempt {attempt+1}/{MAX_RETRIES}")
        try:
            cmd = ["claude", "--dangerously-skip-permissions", "--continue", "--print", prompt]
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=300,
                cwd=str(proj_dir) if proj_dir and proj_dir.exists() else None,
            )
            output = result.stdout + result.stderr

            # Check for API rate limit / overload errors
            is_rate_limit = any(e in output for e in [
                "rate_limit", "Rate limit", "overloaded", "529", "Overloaded",
                "temporarily limiting", "API Error"
            ])

            if result.returncode == 0 and not is_rate_limit:
                log(f"[{proj_id}/{task_id}] SUCCESS after {attempt+1} attempts")
                return True, output

            if is_rate_limit:
                log(f"[{proj_id}/{task_id}] API rate limit — backing off {backoff}s (attempt {attempt+1})")
                time.sleep(backoff)
                backoff = min(backoff * BACKOFF_MULT, BACKOFF_MAX)
                continue

            # Non-rate-limit failure
            log(f"[{proj_id}/{task_id}] FAILED (exit={result.returncode}): {output[:100]}")
            return False, output

        except subprocess.TimeoutExpired:
            log(f"[{proj_id}/{task_id}] TIMEOUT — backing off {backoff}s")
            time.sleep(backoff)
            backoff = min(backoff * BACKOFF_MULT, BACKOFF_MAX)
        except Exception as e:
            log(f"[{proj_id}/{task_id}] ERROR: {e}")
            time.sleep(backoff)
            backoff = min(backoff * BACKOFF_MULT, BACKOFF_MAX)

    log(f"[{proj_id}/{task_id}] EXHAUSTED retries after {MAX_RETRIES} attempts")
    return False, "max retries exhausted"


def process_project(proj_id: str):
    tasks = get_task_queue(proj_id)
    pending = [t for t in tasks if t.get("status") in ("pending", "failed_retrying")]
    if not pending:
        return

    log(f"[{proj_id}] Processing {len(pending)} pending tasks")
    for task in pending:
        task_id = task.get("id", "?")
        update_task_status(proj_id, task_id, "running")
        success, output = run_task(proj_id, task)
        status = "done" if success else "failed"
        update_task_status(proj_id, task_id, status, output)
        log(f"[{proj_id}/{task_id}] → {status}")


def watch_all(target_proj: str = None):
    PID_FILE.write_text(str(os.getpid()))
    log(f"Task watcher started (PID={os.getpid()}), target={target_proj or 'all'}")

    while True:
        projects = [target_proj] if target_proj else [
            p.name for p in PROJECTS_DIR.iterdir()
            if p.is_dir() and (p / "task-queue.jsonl").exists()
        ]
        for proj_id in projects:
            try:
                process_project(proj_id)
            except Exception as e:
                log(f"[{proj_id}] Error: {e}")
        time.sleep(30)  # Poll every 30s


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    watch_all(target)
