#!/usr/bin/env python3
"""
UserPromptSubmit hook: consume `pending-execute-queue.jsonl` entries when a
prompt is submitted to an autonomous provider-exec-{proj} tmux session.

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

        # M1101: MCP-first completion — use ns-hub MCP tool if available, else sentinel fallback
        import os as _os
        _tmux_session = _os.environ.get("TMUX_PANE", "") or ""
        try:
            import subprocess as _sp
            _r = _sp.run(["tmux", "display-message", "-p", "#{session_name}"],
                         capture_output=True, text=True, timeout=2)
            _tmux_session = _r.stdout.strip()
        except Exception:
            pass
        # M1174: respect hub_mcp_disabled flag — stale /tmp/hub/mcp/*.json files must not
        # override the DB setting (they survive reboots when hub_mcp_disabled was set later).
        def _hub_mcp_disabled() -> bool:
            try:
                import sqlite3 as _sq3
                _db = Path.home() / ".hub" / "ns-events.db"
                _c = _sq3.connect(str(_db))
                _row = _c.execute("SELECT value_json FROM user_settings WHERE key='hub_mcp_disabled'").fetchone()
                _c.close()
                return bool(_row and _row[0].strip().lower() in ("true", "1"))
            except Exception:
                return False
        _mcp_available = bool(
            _tmux_session
            and Path(f"/tmp/hub/mcp/{_tmux_session}.json").exists()
            and not _hub_mcp_disabled()
        )

        if _mcp_available:
            # MCP path: don't inject the body — Claude pulls via get_pending_task()
            msg = (
                f"\n[NS HUB] {len(bodies)} task(s) dispatched via Execute button.\n"
                "Call mcp__ns-hub__get_pending_task() to receive your task."
            )
        else:
            completion_instruction = (
                "\n\n---\n"
                "COMPLETION SENTINEL: after finishing each stone, output on its own line (no markdown/code-fence):\n"
                '  {"__hub__":"complete","mid":"<STONE_ID>","status":"pending_confirmation","reply":"<1-line>","star":"child|parent|none"}'
            )
            msg = (
                "\n## AUTONOMOUS TASK DISPATCH "
                f"({len(bodies)} queued entr{'y' if len(bodies)==1 else 'ies'} via Execute button)\n"
                "Execute these instructions NOW without waiting for user input:\n\n"
                + "\n\n---\n\n".join(bodies)
                + completion_instruction
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
