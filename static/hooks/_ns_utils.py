"""
Shared utilities for northstar hooks (stop-inject, execute-inject, session-start).
"""
import os
import subprocess
from pathlib import Path

_HUB_DATA_DIR = Path(os.environ.get("HUB_DATA_DIR", str(Path.home() / ".hub")))
PROJECTS_DIR = Path(os.environ.get("HUB_PROJECTS_DIR", str(_HUB_DATA_DIR / "projects")))


def get_exec_tmux_session() -> str | None:
    """Return current tmux session name if it matches claude-exec-* pattern, else None."""
    sess = os.environ.get("TMUX_PANE") or os.environ.get("TMUX", "")
    if not sess:
        return None
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "#{session_name}"],
            capture_output=True, text=True, timeout=2
        )
        name = result.stdout.strip()
        if name.startswith("claude-exec-"):
            return name
    except Exception:
        pass
    return None


def exec_session_proj() -> str | None:
    """Return project ID for the current claude-exec tmux session, else None."""
    sess = get_exec_tmux_session()
    if not sess:
        return None
    # claude-exec-{PROJ_ID} or claude-exec-{PROJ_ID}-{suffix}
    parts = sess.removeprefix("claude-exec-").split("-")
    # Try longest match first against known projects
    if PROJECTS_DIR.exists():
        for i in range(len(parts), 0, -1):
            candidate = "-".join(parts[:i])
            if (PROJECTS_DIR / candidate).is_dir():
                return candidate
    # Fallback: everything after claude-exec-
    return sess.removeprefix("claude-exec-").split("-")[0] or None
