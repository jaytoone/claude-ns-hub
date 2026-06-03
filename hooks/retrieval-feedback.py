#!/usr/bin/env python3
"""
retrieval-feedback.py — M61 PostToolUse hook

Fires after Edit / Write / MultiEdit tool calls.
Compares the edited file against CTX's last-injection.json to determine
whether the retrieval was a hit or miss, then appends the result to
.omc/retrieval_feedback.jsonl and increments ctx-feedback-stats.json.

Ground-truth signal: if Claude edits a file that CTX injected → hit,
otherwise → miss. Aggregated over time this trains personalization weights.
"""

import json
import os
import sys
import time
from pathlib import Path


def _normalize(path_str: str, project_dir: str) -> str:
    """Return a normalized, absolute path string for comparison."""
    if not path_str:
        return ""
    p = Path(path_str)
    if not p.is_absolute():
        p = Path(project_dir) / p
    try:
        return str(p.resolve())
    except Exception:
        return str(p)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    edited_file = tool_input.get("file_path", "")
    if not edited_file:
        # MultiEdit uses a different key
        edited_file = tool_input.get("path", "")
    if not edited_file:
        sys.exit(0)

    # Determine project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    session_id = data.get("session_id", "")

    # Load last-injection.json
    inj_path = Path.home() / ".claude" / "last-injection.json"
    injected_files = []
    query_preview = ""
    inj_session_id = ""
    if inj_path.exists():
        try:
            inj = json.loads(inj_path.read_text())
            injected_files = inj.get("files", [])
            query_preview = (inj.get("prompt_preview") or "")[:50]
            inj_session_id = inj.get("session_id", "")
        except Exception:
            pass

    # Normalize paths for comparison
    edited_abs = _normalize(edited_file, project_dir)

    # Check if any injected file matches the edited file
    # Match on absolute path OR basename (for doc files stored as plain names)
    edited_basename = Path(edited_file).name
    hit = False
    for inj_f in injected_files:
        inj_abs = _normalize(inj_f, project_dir)
        inj_basename = Path(inj_f).name
        if edited_abs and inj_abs and edited_abs == inj_abs:
            hit = True
            break
        # basename match only when the name is unique across all injected files
        # (avoids false positives like src/utils/index.py == tests/index.py)
        if edited_basename and inj_basename and edited_basename == inj_basename:
            basename_count = sum(1 for f in injected_files if Path(f).name == inj_basename)
            if basename_count == 1:
                hit = True
                break

    # Build feedback event
    event = {
        "ts": time.time(),
        "session_id": session_id or inj_session_id,
        "tool": tool_name,
        "edited_file": edited_file,
        "injected_files": injected_files,
        "hit": hit,
        "query_preview": query_preview,
    }

    # Append to .omc/retrieval_feedback.jsonl
    omc_dir = Path(project_dir) / ".omc"
    try:
        omc_dir.mkdir(parents=True, exist_ok=True)
        feedback_path = omc_dir / "retrieval_feedback.jsonl"
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # Increment ctx-feedback-stats.json for quick dashboard display
    stats_path = Path.home() / ".claude" / "ctx-feedback-stats.json"
    try:
        stats = {}
        if stats_path.exists():
            stats = json.loads(stats_path.read_text())
        hits = stats.get("hits", 0)
        misses = stats.get("misses", 0)
        total = stats.get("total", 0)
        if hit:
            hits += 1
        else:
            misses += 1
        total += 1
        hit_rate = round(hits / total, 3) if total > 0 else 0.0
        stats.update({
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": hit_rate,
            "last_ts": event["ts"],
            "last_edited": edited_file,
            "last_hit": hit,
        })
        stats_path.write_text(json.dumps(stats, indent=2))
    except Exception:
        pass

    # No stdout output needed — hook is informational only
    sys.exit(0)


if __name__ == "__main__":
    main()
