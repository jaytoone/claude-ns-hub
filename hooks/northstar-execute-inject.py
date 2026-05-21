#!/usr/bin/env python3
"""
UserPromptSubmit hook: consume `pending-execute-queue.jsonl` entries when a
prompt is submitted to an autonomous claude-exec-{proj} tmux session.

Used as a wake-path partner to Stop hook: when hub sends `tmux send-keys "go"`
to wake an idle session, this hook fires on the resulting prompt and injects
all unconsumed queue entries via additionalContext for the next model turn.

Idempotency via `.queue-offset` byte cookie (shared with Stop hook).

Skips non-exec sessions to avoid hijacking interactive Claude windows whose
cwd happens to match a hub project.
"""
import json
import sys
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).parent))
from _ns_utils import exec_session_proj, PROJECTS_DIR


def main():
    proj = exec_session_proj()
    if not proj:
        return

    if not PROJECTS_DIR.exists():
        return

    # M197 fix — only process THIS session's project queue, not every project's.
    pdir = PROJECTS_DIR / proj
    if not pdir.is_dir():
        return
    for _once in (pdir,):
        pdir = _once

        queue = pdir / "pending-execute-queue.jsonl"
        new_data = ""
        new_offset = None

        if queue.exists():
            offset_file = pdir / ".queue-offset"
            try:
                offset = int(offset_file.read_text().strip()) if offset_file.exists() else 0
            except Exception:
                offset = 0
            try:
                file_size = queue.stat().st_size
            except Exception:
                continue
            if file_size > offset:
                try:
                    with queue.open("r", encoding="utf-8") as f:
                        f.seek(offset)
                        new_data = f.read()
                    new_offset = file_size
                except Exception:
                    new_data = ""

        entries = []
        for line in new_data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

        # Legacy pending-execute-prompt.txt intentionally NOT read here.
        # northstar-session-start.py always fires before UserPromptSubmit and
        # already consumes + deletes that file. Reading it here would be a
        # race condition (double-delivery) if session-start fires concurrently.

        if not entries:
            continue

        if new_offset is not None:
            try:
                (pdir / ".queue-offset").write_text(str(new_offset))
            except Exception:
                pass

        bodies = []
        for e in entries:
            b = e.get("body", "")
            if b:
                bodies.append(b)

        msg = (
            "\n## AUTONOMOUS TASK DISPATCH "
            f"({len(bodies)} queued entr{'y' if len(bodies)==1 else 'ies'} via Execute button)\n"
            "Execute these instructions NOW without waiting for user input:\n\n"
            + "\n\n---\n\n".join(bodies)
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": msg,
            }
        }))
        break  # one project at a time


if __name__ == "__main__":
    main()
