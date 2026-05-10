#!/usr/bin/env python3
"""
test-task-worker.py — Real-time processing test for task-worker.py
Writes a task to task-queue/, waits for result, reports latency + pass/fail.

Usage: python3 ~/.claude/hub/test-task-worker.py [--timeout 60]
"""
import json
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

QUEUE_DIR = Path(os.environ.get("HUB_TASK_QUEUE", Path.home() / ".claude/hub/task-queue"))
RESULT_DIR = Path(os.environ.get("HUB_TASK_RESULTS", Path.home() / ".claude/hub/task-results"))
PID_FILE = Path("/tmp/hub-task-worker.pid")

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
INFO = "\033[34mINFO\033[0m"


def check_worker_running() -> bool:
    if not PID_FILE.exists():
        return False
    pid = int(PID_FILE.read_text().strip())
    return Path(f"/proc/{pid}").exists()


def run_test(timeout: int) -> dict:
    results = {}

    # T1: Worker liveness
    running = check_worker_running()
    results["worker_running"] = running
    print(f"[{PASS if running else FAIL}] Worker process running: {running}")
    if not running:
        print(f"       Start it: python3 ~/.claude/hub/task-worker.py &")
        return results

    # T2: Write task to queue
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:21]
    task_id = f"task-test-rt-{ts}"
    task_file = QUEUE_DIR / f"{task_id}.md"
    result_file = RESULT_DIR / f"{task_id}.json"

    task_content = (
        "Echo back exactly this JSON on a single line (no other text):\n"
        '{"echo": "task-worker-rt-ok"}\n'
    )

    write_start = time.monotonic()
    task_file.write_text(task_content)
    print(f"[{INFO}] Task written: {task_file.name}")

    # T3: Poll for result
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if result_file.exists():
            break
        time.sleep(0.5)

    elapsed = time.monotonic() - write_start

    if not result_file.exists():
        results["result_appeared"] = False
        results["latency_s"] = None
        print(f"[{FAIL}] Result not found after {timeout}s")
        return results

    results["result_appeared"] = True
    results["latency_s"] = round(elapsed, 2)
    print(f"[{PASS}] Result appeared in {elapsed:.2f}s")

    # T4: Validate result structure
    try:
        data = json.loads(result_file.read_text())
    except json.JSONDecodeError as e:
        results["result_valid_json"] = False
        print(f"[{FAIL}] Result is not valid JSON: {e}")
        return results

    results["result_valid_json"] = True
    required_keys = {"task_id", "task_file", "status", "output", "completed_at"}
    missing = required_keys - data.keys()
    results["required_keys_present"] = len(missing) == 0
    if missing:
        print(f"[{FAIL}] Missing keys in result: {missing}")
    else:
        print(f"[{PASS}] Result structure valid (keys: {sorted(data.keys())})")

    # T5: Status check
    status = data.get("status", "unknown")
    results["status"] = status
    ok = status == "done"
    print(f"[{PASS if ok else FAIL}] Result status: {status}")

    # Cleanup test artifacts
    task_file.unlink(missing_ok=True)
    result_file.unlink(missing_ok=True)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=90, help="Max wait seconds (default 90)")
    args = parser.parse_args()

    print(f"\n=== task-worker real-time processing test ===")
    print(f"Queue : {QUEUE_DIR}")
    print(f"Results: {RESULT_DIR}")
    print(f"Timeout: {args.timeout}s\n")

    results = run_test(args.timeout)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    total = passed + failed

    print(f"\n--- Summary ---")
    print(f"Passed: {passed}/{total}")
    if results.get("latency_s") is not None:
        print(f"Latency: {results['latency_s']}s")

    all_pass = failed == 0 and total > 0
    print(f"Overall: {PASS if all_pass else FAIL}\n")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
