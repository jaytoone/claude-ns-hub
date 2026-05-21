#!/usr/bin/env python3
"""
Stop hook: inject pending-execute-queue.jsonl entries when Claude stops inside
a claude-exec-{proj} tmux session. Also captures session_id for all sessions.

Guards: tmux session name starts with "claude-exec-" → cwd maps to project →
queue has unconsumed bytes. Exit 2 blocks stop and feeds stderr as instruction.
"""
import json
import os
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _ns_utils import get_exec_tmux_session, PROJECTS_DIR


def get_project_id(cwd: str):
    """Map cwd to project_id by scanning PROJECTS_DIR at runtime — no hardcoded list."""
    if not PROJECTS_DIR.exists():
        return None
    cwd_parts = {p.lower() for p in Path(cwd).parts}
    for proj_dir in PROJECTS_DIR.iterdir():
        if proj_dir.is_dir() and proj_dir.name.lower() in cwd_parts:
            return proj_dir.name
    return None


def _read_frontmatter_fields(md_path: Path, *keys) -> dict:
    """Extract scalar fields from YAML frontmatter."""
    result = {k: "" for k in keys}
    try:
        txt = md_path.read_text(encoding="utf-8")
        if txt.startswith("---"):
            end = txt.find("\n---", 3)
            block = txt[3:end] if end > 0 else ""
            for k in keys:
                m = re.search(rf"^{k}:\s*['\"]?([^'\"\\n]+)['\"]?", block, re.MULTILINE)
                if m:
                    result[k] = m.group(1).strip()
    except Exception:
        pass
    return result


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    cwd = data.get("cwd", "")
    proj_id = get_project_id(cwd)
    if not proj_id:
        return

    pdir = PROJECTS_DIR / proj_id
    is_exec = get_exec_tmux_session() is not None

    # Capture session_id for all session types (exec + interactive)
    sid = data.get("session_id")
    if sid:
        try:
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / ".last-session-id").write_text(sid)
            fm = _read_frontmatter_fields(pdir / "north-star.md", "model", "continuity_mode")
            cur_model, continuity_mode = fm["model"], fm["continuity_mode"] or "isolated"
            hist_file = pdir / ".session-history.json"
            hist = {}
            if hist_file.exists():
                try: hist = json.loads(hist_file.read_text())
                except Exception: pass
            if is_exec:
                hist[cur_model or "_default"] = sid
                if continuity_mode == "portable":
                    hist["_current"] = sid
            else:
                hist["_interactive"] = sid
            hist_file.write_text(json.dumps(hist, indent=2))
        except Exception:
            pass

    if not is_exec:
        return

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
        return

    try:
        with queue.open("r", encoding="utf-8") as f:
            f.seek(offset)
            new_data = f.read()
    except Exception:
        return

    entries = [json.loads(l) for l in new_data.splitlines() if l.strip() and _safe_json(l)]

    try:
        offset_file.write_text(str(file_size))
    except Exception:
        pass

    if not entries:
        return

    bodies = "\n\n---\n\n".join(e.get("body", "") for e in entries if e.get("body"))
    sys.stderr.write(
        f"## AUTONOMOUS TASK DISPATCH ({len(entries)} queued entr"
        f"{'y' if len(entries)==1 else 'ies'} via Execute button)\n"
        "Process these instructions now.\n\n"
        + bodies + "\n"
    )
    sys.exit(2)


def _safe_json(line: str):
    try: return json.loads(line)
    except Exception: return None


if __name__ == "__main__":
    main()
