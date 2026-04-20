#!/usr/bin/env python3
"""
utility-rate.py — Stop hook that measures CTX injection utility (P1).

After each assistant turn, reads:
  1. The items bm25-memory injected into the turn (~/.claude/last-injection.json)
  2. The latest assistant message from vault.db

Substring-matches each item's distinctive tokens against the assistant's
response. Emits a `utility_measured` telemetry event with:
  - total_items: how many distinct items were injected
  - referenced_items: how many had at least one token substring-match in the response
  - by_block: per-block breakdown (g1 / g2_docs / g2_prefetch)

This is the R3 signal (outcome) described in the WTP analysis — it tells
us whether injected context was actually USED by the assistant, not just
surfaced. Dashboard presents this as "Utility rate" per block.

Privacy: no content logged; only counts + block names.
"""
import json
import os
import sqlite3
import sys
import time
from datetime import date, datetime
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LAST_INJECT = HOME / ".claude" / "last-injection.json"
VAULT_DB = HOME / ".local" / "share" / "claude-vault" / "vault.db"
WOW_STATE = HOME / ".claude" / ".ctx-wow-fired"
WOW_EVENT_FILE = HOME / ".claude" / ".ctx-wow-event.json"   # latest qualifying event (for dashboard banner)

# Wow-trigger gates
WOW_UTILITY_MIN = 0.70      # utility_rate ≥ 70%
WOW_AGE_MIN_DAYS = 14       # at least one referenced item ≥ 14 days old


def _log_event(event_type: str, payload: dict):
    try:
        sys.path.insert(0, str(HOME / ".claude" / "hooks"))
        from _ctx_telemetry import log_event
        log_event(event_type, payload)
    except Exception:
        pass


def _latest_assistant_content() -> str:
    """Return text of the most recent assistant turn from vault.db (last 5 min)."""
    if not VAULT_DB.exists():
        return ""
    try:
        c = sqlite3.connect(f"file:{VAULT_DB}?mode=ro", uri=True, timeout=2.0)
        cutoff = time.time() - 300
        # vault.db stores `timestamp` as ISO string; fallback to id-ordered
        row = c.execute(
            "SELECT content, timestamp FROM messages "
            "WHERE role='assistant' "
            "ORDER BY id DESC LIMIT 1"
        ).fetchone()
        c.close()
        if not row:
            return ""
        return row[0] or ""
    except Exception:
        return ""


def main():
    if not LAST_INJECT.exists():
        return
    try:
        inj = json.loads(LAST_INJECT.read_text())
    except Exception:
        return
    items = inj.get("items", [])
    if not items:
        return

    # Age guard: injection older than 10 min → probably stale, skip
    if time.time() - inj.get("ts", 0) > 600:
        return

    response = _latest_assistant_content()
    if not response:
        return
    # Case-insensitive substring match on distinctive tokens
    response_l = response.lower()

    by_block = {}
    total = 0
    referenced = 0
    max_referenced_age = 0    # oldest decision date among referenced items (for wow trigger)
    for it in items:
        block = it.get("block", "?")
        tokens = it.get("tokens", [])
        by_block.setdefault(block, {"total": 0, "referenced": 0})
        by_block[block]["total"] += 1
        total += 1
        # Item is "referenced" if ANY of its distinctive tokens appears in the response
        hit = any(
            len(t) >= 4 and t.lower() in response_l
            for t in tokens
        )
        if hit:
            referenced += 1
            by_block[block]["referenced"] += 1
            # Track oldest referenced decision date
            date_str = it.get("date")
            if date_str:
                try:
                    age_days = (date.today() - datetime.fromisoformat(date_str).date()).days
                    if age_days > max_referenced_age:
                        max_referenced_age = age_days
                except Exception:
                    pass

    _log_event("utility_measured", {
        "total_items": total,
        "referenced_items": referenced,
        "by_block": by_block,
        "response_len": len(response),
    })

    # ── Wow-trigger: specific-old-recall + high-utility, fired once ever ──
    if total > 0:
        rate = referenced / total
        if (not WOW_STATE.exists()
                and rate >= WOW_UTILITY_MIN
                and max_referenced_age >= WOW_AGE_MIN_DAYS):
            # Terminal toast (stderr is visible in most shells)
            age_d = max_referenced_age
            msg_lines = [
                "",
                "  ╔══════════════════════════════════════════════════╗",
                f"  ║  ● CTX recalled a decision from {age_d:3d} days ago   ║",
                f"  ║    Claude actually used it ({int(rate*100)}% of injections).  ║",
                "  ║  → see the graph:  ctx                           ║",
                "  ╚══════════════════════════════════════════════════╝",
                "",
            ]
            print("\n".join(msg_lines), file=sys.stderr)

            wow = {
                "fired_at": time.time(),
                "age_days": age_d,
                "utility_rate": rate,
            }
            try:
                WOW_STATE.write_text(json.dumps(wow))
                WOW_EVENT_FILE.write_text(json.dumps(wow))
            except Exception:
                pass
            _log_event("wow_fired", {
                "total_items": total,
                "referenced_items": referenced,
                "response_len": len(response),
            })
        # Always keep WOW_EVENT_FILE fresh for dashboard banner (latest qualifying event)
        elif rate >= WOW_UTILITY_MIN and max_referenced_age >= WOW_AGE_MIN_DAYS:
            try:
                WOW_EVENT_FILE.write_text(json.dumps({
                    "fired_at": time.time(),
                    "age_days": max_referenced_age,
                    "utility_rate": rate,
                }))
            except Exception:
                pass

    # Consume the injection file so we don't double-count it on a second Stop
    try:
        LAST_INJECT.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
