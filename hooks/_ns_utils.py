"""
Shared utilities for northstar-*.py hooks.
Import: from _ns_utils import get_exec_tmux_session
"""
import os
import subprocess
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude/hub/projects"


def get_exec_tmux_session() -> str | None:
    """Return the claude-exec-* tmux session name if running inside one, else None.
    Reads TMUX env var; falls back to /proc/ppid/environ for hooks running as subprocesses."""
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
    try:
        r = subprocess.run(
            ["tmux", "-S", tmux_val.split(",")[0], "display-message", "-p", "#S"],
            capture_output=True, text=True, timeout=2,
            env={**os.environ, "TMUX": tmux_val},
        )
        if r.returncode != 0:
            return None
        name = r.stdout.strip()
        return name if name.startswith("claude-exec-") else None
    except Exception:
        return None


def exec_session_proj() -> str | None:
    """Return the project ID from the current claude-exec-{proj} session name, or None."""
    name = get_exec_tmux_session()
    if name and name.startswith("claude-exec-"):
        return name[len("claude-exec-"):]
    return None
