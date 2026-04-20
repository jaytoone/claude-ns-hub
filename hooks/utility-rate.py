#!/usr/bin/env python3
"""
utility-rate.py — Stop hook that measures CTX injection utility (P1).

After each assistant turn, reads:
  1. The items bm25-memory injected into the turn (~/.claude/last-injection.json)
  2. The just-emitted assistant response from Claude Code's transcript_path
     (passed in the Stop hook's stdin JSON). Authoritative source — no race
     with claude-vault-incremental. Falls back to vault.db if transcript
     not available.

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
import socket
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


# ── T1: Semantic similarity via vec-daemon ───────────────────────────
VEC_SOCK = HOME / ".local" / "share" / "claude-vault" / "vec-daemon.sock"
SEMANTIC_THRESHOLD = 0.85
# e5-small calibration (empirical, 2026-04-20):
#   related pairs:    cos ∈ [0.84, 0.90]  (item subject vs on-topic response chunk)
#   unrelated pairs:  cos ∈ [0.74, 0.78]  (shared "query:" prefix gives high baseline)
# 0.85 sits at the floor of "related", above the unrelated ceiling.


def _embed(text: str, timeout: float = 0.8) -> list | None:
    """Query vec-daemon for an embedding. Returns None on any failure."""
    if not VEC_SOCK.exists() or not text:
        return None
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(str(VEC_SOCK))
        s.sendall((json.dumps({"q": text[:1000]}) + "\n").encode("utf-8"))
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
        s.close()
        resp = json.loads(buf.split(b"\n", 1)[0].decode("utf-8"))
        if resp.get("ok"):
            return resp.get("emb")
    except Exception:
        pass
    return None


def _cosine(a: list, b: list) -> float:
    """Cosine similarity for already-normalized vectors (vec-daemon normalizes)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def _chunk_response(text: str, chunk_chars: int = 400, overlap: int = 80) -> list:
    """Split response into overlapping chunks so a long response doesn't dilute
    any single item's cosine. Chunks span paragraphs when possible."""
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p) <= chunk_chars:
            chunks.append(p)
        else:
            # Slide a window through long paragraphs
            start = 0
            while start < len(p):
                chunks.append(p[start:start + chunk_chars])
                start += chunk_chars - overlap
    return chunks[:20]   # hard cap — ceiling on vec-daemon calls per measurement


def _item_text(item: dict) -> str:
    """Reconstruct a natural-language description from an item's tokens.
    Prefer the raw subject if preserved; fall back to joining tokens."""
    if item.get("subject"):
        return item["subject"]
    tokens = item.get("tokens", [])
    return " ".join(tokens) if tokens else ""


def _log_event(event_type: str, payload: dict):
    try:
        sys.path.insert(0, str(HOME / ".claude" / "hooks"))
        from _ctx_telemetry import log_event
        log_event(event_type, payload)
    except Exception:
        pass


def _from_transcript(transcript_path: str) -> str:
    """Return concatenation of ALL assistant text blocks emitted since the
    last user message in Claude Code's transcript .jsonl.

    Why not just "the last assistant message":
      A single assistant turn in Claude Code is a sequence of alternating
      text-block / tool-use / tool-result entries. If we take only the last
      *text block*, we miss the narrative that appeared BEFORE the final
      tool call — often the part most relevant for utility scoring.
      Joining all text since the last user message captures the full
      response the user actually saw.

    This is the authoritative, race-free source — the transcript is written
    by Claude Code BEFORE any Stop hook fires, unlike vault.db which is
    populated asynchronously by claude-vault-incremental.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    chunks_since_user: list[str] = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except Exception:
                    continue
                t = d.get("type")
                if t == "user":
                    # Reset — we only care about text emitted since the
                    # most recent user turn (i.e., the current response).
                    chunks_since_user = []
                    continue
                if t != "assistant":
                    continue
                msg = d.get("message", {})
                content = msg.get("content", [])
                if isinstance(content, str):
                    if content.strip():
                        chunks_since_user.append(content)
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text = c.get("text", "")
                            if text and text.strip():
                                chunks_since_user.append(text)
    except Exception:
        pass
    return "\n".join(chunks_since_user)


def _from_vault() -> str:
    """Fallback: most recent assistant turn from vault.db.
    Note — vault.db updates on Stop via claude-vault-incremental (async),
    so this often lags the transcript by one turn. Kept as fallback only."""
    if not VAULT_DB.exists():
        return ""
    try:
        c = sqlite3.connect(f"file:{VAULT_DB}?mode=ro", uri=True, timeout=2.0)
        row = c.execute(
            "SELECT content FROM messages WHERE role='assistant' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        c.close()
        return (row[0] or "") if row else ""
    except Exception:
        return ""


def _read_stop_stdin() -> dict:
    """Stop hook receives {session_id, transcript_path, stop_hook_active} on stdin.
    Returns {} if stdin is empty (backward compat / manual invocation)."""
    try:
        if sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


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

    # Prefer Claude Code's transcript (race-free, authoritative); fall back
    # to vault.db only if transcript_path wasn't provided. This fixes the
    # "always scoring previous turn's response" bug where utility-rate and
    # claude-vault-incremental both ran async and utility-rate often read
    # vault.db BEFORE incremental finished writing the current turn.
    stop_input = _read_stop_stdin()
    response = _from_transcript(stop_input.get("transcript_path", "")) or _from_vault()
    if not response:
        return
    # Case-insensitive substring match on distinctive tokens
    response_l = response.lower()

    # ── T1: pre-compute response-chunk embeddings (one daemon call per chunk)
    # If vec-daemon is unreachable, we fall back to pure substring match per item.
    response_chunks = _chunk_response(response)
    chunk_embeddings = []
    semantic_available = False
    for chunk in response_chunks:
        emb = _embed(chunk)
        if emb:
            chunk_embeddings.append(emb)
            semantic_available = True

    by_block = {}
    total = 0
    referenced = 0
    hits_by_mode = {"substring": 0, "semantic": 0, "both": 0}
    max_referenced_age = 0    # oldest decision date among referenced items (for wow trigger)

    for it in items:
        block = it.get("block", "?")
        tokens = it.get("tokens", [])
        by_block.setdefault(block, {"total": 0, "referenced": 0})
        by_block[block]["total"] += 1
        total += 1

        # Substring check (fast, catches verbatim echoes)
        sub_hit = any(len(t) >= 4 and t.lower() in response_l for t in tokens)

        # Semantic check (catches paraphrase, synonym, cross-language)
        sem_hit = False
        if semantic_available:
            item_text = _item_text(it)
            if item_text:
                item_emb = _embed(item_text)
                if item_emb:
                    max_sim = max((_cosine(item_emb, ce) for ce in chunk_embeddings),
                                  default=0.0)
                    sem_hit = max_sim >= SEMANTIC_THRESHOLD

        hit = sub_hit or sem_hit
        if hit:
            referenced += 1
            by_block[block]["referenced"] += 1
            if sub_hit and sem_hit:
                hits_by_mode["both"] += 1
            elif sub_hit:
                hits_by_mode["substring"] += 1
            else:
                hits_by_mode["semantic"] += 1
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
        "hits_by_mode": hits_by_mode,
        "semantic_available": semantic_available,
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
