#!/usr/bin/env python3
"""
auto-index: Auto-index project with codebase-memory-mcp.

Triggers:
  SessionStart — if DB missing or >24h old
  PostToolUse (Bash git commit) — always re-index after commit (--force)

Modes:
  default         ACTUALLY EXECUTE reindex via `codebase-memory-mcp cli index_repository`
                  (iter 13 — previously emitted a hint which Claude often ignored,
                  causing 10+ day silent index staleness). Incremental reindex ~60ms.
  --hint-only     Emit additionalContext text (legacy behavior, for debugging).
  --force         Force reindex even if DB is fresh.
"""
import json
import os
import subprocess
import sys
import time


FORCE = "--force" in sys.argv
HINT_ONLY = "--hint-only" in sys.argv


def find_db(project_dir):
    """Find existing codebase-memory-mcp DB for this project."""
    cache_dir = os.path.expanduser("~/.cache/codebase-memory-mcp")
    if not os.path.isdir(cache_dir):
        return None
    slug = project_dir.replace("/", "-").lstrip("-")
    db_path = os.path.join(cache_dir, f"{slug}.db")
    return db_path if os.path.exists(db_path) else None


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    if not os.path.isdir(os.path.join(project_dir, ".git")):
        sys.exit(0)

    db_path = find_db(project_dir)

    if FORCE:
        reason = "post-commit reindex"
        age_hours = 0
    elif db_path is None:
        reason = "not indexed"
        age_hours = 0
    else:
        age_hours = (time.time() - os.path.getmtime(db_path)) / 3600
        if age_hours > 24:
            reason = f"stale ({age_hours:.0f}h old)"
        else:
            sys.exit(0)

    # Default: actually execute reindex (iter 13). Incremental is ~60ms;
    # full first-time index may take seconds but the hook is async.
    if not HINT_ONLY:
        cli = os.path.expanduser("~/.local/bin/codebase-memory-mcp")
        if os.path.exists(cli):
            payload = json.dumps({"repo_path": project_dir, "mode": "fast"})
            _t0 = time.perf_counter()
            try:
                r = subprocess.run(
                    [cli, "cli", "index_repository", payload],
                    capture_output=True, text=True, timeout=30,
                )
                _dur = int((time.perf_counter() - _t0) * 1000)
                # Emit brief visible confirmation in additionalContext so the user
                # can verify the reindex happened (especially after long-stale).
                status = "indexed" if r.returncode == 0 else f"failed (rc={r.returncode})"
                output = {
                    "additionalContext": (
                        f"[AUTO-INDEX] {reason} → executed: {status}"
                        + (f" (was {age_hours/24:.1f}d stale)" if age_hours > 72 else "")
                    )
                }
                json.dump(output, sys.stdout)
                # Opt-in telemetry (privacy-safe)
                try:
                    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                    from _ctx_telemetry import log_event
                    _tele_status = "indexed" if r.returncode == 0 else "failed"
                    log_event("auto_index", {"status": _tele_status, "age_hours": int(age_hours), "duration_ms": _dur})
                except Exception:
                    pass
                return
            except subprocess.TimeoutExpired:
                output = {
                    "additionalContext": (
                        f"⚠ [AUTO-INDEX] {reason} → execute timed out after 30s. "
                        f"Run manually: mcp__codebase-memory-mcp__index_repository(repo_path=\"{project_dir}\")"
                    )
                }
                json.dump(output, sys.stdout)
                try:
                    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                    from _ctx_telemetry import log_event
                    log_event("auto_index", {"status": "timeout", "age_hours": int(age_hours), "duration_ms": 30000})
                except Exception:
                    pass
                return
            except Exception as e:
                # fall through to hint-only
                pass

    # Hint-only path (legacy fallback or --hint-only flag).
    # Staleness tier: 24h silent / 3-7d ⚠ STALE / 7d+ ⚠⚠ CRITICAL.
    if age_hours > 168:
        severity = "⚠⚠ CRITICAL"
        detail = f"{age_hours/24:.1f}d stale — G2 may miss recent symbols"
    elif age_hours > 72:
        severity = "⚠ STALE"
        detail = f"{age_hours:.0f}h old"
    else:
        severity = "[AUTO-INDEX]"
        detail = reason

    output = {
        "additionalContext": (
            f"{severity} codebase-memory-mcp index: {detail} — "
            f"run: mcp__codebase-memory-mcp__index_repository(repo_path=\"{project_dir}\", mode=\"fast\")"
        )
    }
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
