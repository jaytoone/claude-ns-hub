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
import os
import subprocess
import sys
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude/hub/projects"


def exec_session_proj() -> str | None:
    """Return the project ID encoded in the current claude-exec-{proj} tmux session,
    or None if we're not in such a session. M197 fix — replaces the prior
    in_exec_tmux() bool that allowed iterating across projects."""
    tmux_val = os.environ.get("TMUX")
    if not tmux_val:
        try:
            with open(f"/proc/{os.getppid()}/environ", "rb") as f:
                for chunk in f.read().split(b"\0"):
                    if chunk.startswith(b"TMUX="):
                        tmux_val = chunk[5:].decode("utf-8", "replace")
                        break
        except Exception:
            return None
    if not tmux_val:
        return None
    socket = tmux_val.split(",")[0]
    try:
        r = subprocess.run(
            ["tmux", "-S", socket, "display-message", "-p", "#S"],
            capture_output=True, text=True, timeout=2,
            env={**os.environ, "TMUX": tmux_val},
        )
        if r.returncode != 0:
            return None
        name = r.stdout.strip()
        if not name.startswith("claude-exec-"):
            return None
        return name[len("claude-exec-"):]
    except Exception:
        return None


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

        # Prefer new queue file; fall back to legacy single-shot file for SessionStart bootstrap
        queue = pdir / "pending-execute-queue.jsonl"
        legacy = pdir / "pending-execute-prompt.txt"

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

        # Legacy fallback (one-shot init from SessionStart bootstrap path)
        legacy_body = ""
        if legacy.exists():
            try:
                legacy_body = legacy.read_text(encoding="utf-8").strip()
                legacy.unlink()
            except Exception:
                legacy_body = ""

        if not entries and not legacy_body:
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
        if legacy_body:
            bodies.append(legacy_body)

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
