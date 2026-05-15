#!/usr/bin/env python3
"""
Stop hook: consume `pending-execute-queue.jsonl` entries when Claude finishes
a response inside an autonomous claude-exec-{proj} tmux session.

Each Execute click APPENDS one JSON entry to the queue (never overwrites).
This hook tracks a byte offset in `.queue-offset` so it only consumes new
entries since the last fire — preventing duplicate dispatches AND ensuring
no entry is lost to file overwrites.

On consumption: prints aggregated entries to stderr and exits 2. Per Claude
Code spec, exit 2 blocks the stop AND feeds stderr as next-turn instruction.

Guards (in order, all must pass to inject):
  1. Running inside a tmux session named claude-exec-* (skips interactive sessions)
  2. cwd maps to a known project_id
  3. pending-execute-queue.jsonl has unconsumed entries (size > offset)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude/hub/projects"

DIR_TO_PROJECT = {
    "Moat": "MOAT", "CTX": "CTX", "FromScratch": "FromScratch",
    "Ameva": "Ameva", "EI": "EI", "FRWP": "FRWP",
    "HugwartsBanana": "HugwartsBanana", "AIKB": "AIKB",
    "Clone": "Clone", "FreeOS": "FreeOS",
}


def in_exec_tmux() -> bool:
    tmux_val = os.environ.get("TMUX")
    if not tmux_val:
        try:
            with open(f"/proc/{os.getppid()}/environ", "rb") as f:
                for chunk in f.read().split(b"\0"):
                    if chunk.startswith(b"TMUX="):
                        tmux_val = chunk[5:].decode("utf-8", "replace")
                        break
        except Exception:
            return False
    if not tmux_val:
        return False
    socket = tmux_val.split(",")[0]
    try:
        r = subprocess.run(
            ["tmux", "-S", socket, "display-message", "-p", "#S"],
            capture_output=True, text=True, timeout=2,
            env={**os.environ, "TMUX": tmux_val},
        )
        return r.returncode == 0 and r.stdout.strip().startswith("claude-exec-")
    except Exception:
        return False


def get_project_id(cwd: str):
    path = Path(cwd)
    dir_lower = {k.lower(): v for k, v in DIR_TO_PROJECT.items()}
    for part in path.parts[::-1]:
        if part.lower() in dir_lower:
            return dir_lower[part.lower()]
    if PROJECTS_DIR.exists():
        cwd_lower = {p.lower() for p in path.parts}
        for proj_dir in PROJECTS_DIR.iterdir():
            if proj_dir.is_dir() and proj_dir.name.lower() in cwd_lower:
                return proj_dir.name
    return None


def main():
    if not in_exec_tmux():
        return

    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    cwd = data.get("cwd", "")
    proj_id = get_project_id(cwd)
    if not proj_id:
        return

    pdir = PROJECTS_DIR / proj_id

    # Capture session_id for tmux-resume continuity
    # (spec: docs/research/20260513-tmux-claude-session-resume-design.md MVF #1)
    sid = data.get("session_id")
    if sid:
        sid_file = pdir / ".last-session-id"
        try:
            prev = sid_file.read_text().strip() if sid_file.exists() else ""
            if prev != sid:
                pdir.mkdir(parents=True, exist_ok=True)
                sid_file.write_text(sid)
        except Exception:
            pass
        # Also key by current model so switching models later resumes the right
        # thread (e.g. sonnet→gpt→sonnet returns to the original sonnet session).
        # Reads `model` and `continuity_mode` from north-star.md frontmatter.
        try:
            md = pdir / "north-star.md"
            cur_model = ""
            continuity_mode = "isolated"  # default
            if md.exists():
                txt = md.read_text(encoding="utf-8")
                if txt.startswith("---"):
                    end = txt.find("\n---", 3)
                    if end > 0:
                        for line in txt[3:end].splitlines():
                            line = line.strip()
                            if line.startswith("model:"):
                                cur_model = line.split(":", 1)[1].strip().strip("'\"")
                            elif line.startswith("continuity_mode:"):
                                continuity_mode = line.split(":", 1)[1].strip().strip("'\"")
            hist_file = pdir / ".session-history.json"
            hist = {}
            if hist_file.exists():
                try: hist = json.loads(hist_file.read_text())
                except Exception: hist = {}
            # In isolated mode: per-model history
            # In portable mode: both per-model AND shared _current key
            hist[cur_model or "_default"] = sid
            if continuity_mode == "portable":
                hist["_current"] = sid
            hist_file.write_text(json.dumps(hist, indent=2))
        except Exception:
            pass

    queue = pdir / "pending-execute-queue.jsonl"
    if not queue.exists():
        return

    offset_file = pdir / ".queue-offset"
    try:
        offset = int(offset_file.read_text().strip()) if offset_file.exists() else 0
    except Exception:
        offset = 0

    try:
        file_size = queue.stat().st_size
    except Exception:
        return

    if file_size <= offset:
        return  # nothing new

    try:
        with queue.open("r", encoding="utf-8") as f:
            f.seek(offset)
            new_data = f.read()
    except Exception:
        return

    entries = []
    for line in new_data.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue

    if not entries:
        try:
            offset_file.write_text(str(file_size))
        except Exception:
            pass
        return

    # Advance offset BEFORE printing — guarantees idempotency even if Claude crashes
    try:
        offset_file.write_text(str(file_size))
    except Exception:
        pass

    bodies = "\n\n---\n\n".join(e.get("body", "") for e in entries if e.get("body"))
    sys.stderr.write(
        "## AUTONOMOUS TASK DISPATCH "
        f"({len(entries)} queued entr{'y' if len(entries)==1 else 'ies'} via Execute button)\n"
        "Process these instructions now.\n\n"
        + bodies + "\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
