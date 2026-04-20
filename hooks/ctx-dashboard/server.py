#!/usr/bin/env python3
"""
ctx-dashboard server — FastAPI + SSE live dashboard for CTX telemetry.

Reuses ctx-report.py's _compute_metrics() and tail-follow logic.
Serves a single HTML page at / and streams JSON snapshots via /stream (SSE).

Usage:
    python3 -m uvicorn server:app --host 127.0.0.1 --port 8787
  or simply:
    python3 ~/.claude/hooks/ctx-dashboard/server.py
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

# Import from sibling ctx-report.py
HOOK_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HOOK_DIR))
import importlib.util
_spec = importlib.util.spec_from_file_location("ctx_report", HOOK_DIR / "ctx-report.py")
_ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ctx)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).parent
STATIC = HERE / "static"
LOG = _ctx.LOG
TH = _ctx.TH

app = FastAPI(title="CTX Dashboard", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ── Tail-follow state (singleton for the server process) ──────────────
class TelemetryTail:
    def __init__(self, since: str = "7d"):
        self.cutoff = _ctx.parse_since(since)
        self.events: list = []
        self.pos: int = 0
        self.size: int = 0
        self._load_once()

    def _load_once(self):
        """Full initial read."""
        self.events = _ctx.load_events(self.cutoff)
        if LOG.exists():
            self.size = LOG.stat().st_size
            self.pos = self.size

    def refresh(self):
        """Append new events since last read. Drop events older than cutoff."""
        if not LOG.exists():
            return
        try:
            st = LOG.stat()
        except OSError:
            return
        if st.st_size < self.size:  # rotation/truncation
            self.events.clear()
            self.pos = 0
        self.size = st.st_size
        if self.pos >= st.st_size:
            return
        try:
            with LOG.open() as f:
                f.seek(self.pos)
                for line in f:
                    if not line.endswith("\n"):
                        break
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    if self.cutoff is None or r.get("ts", 0) >= self.cutoff:
                        self.events.append(r)
                self.pos = f.tell()
        except OSError:
            return
        # Drop stale (only check front)
        if self.cutoff is not None:
            while self.events and self.events[0].get("ts", 0) < self.cutoff:
                self.events.pop(0)


TAIL = TelemetryTail("7d")


# ── Per-minute activity bucket (for time-series chart) ────────────────
def _activity_buckets(events, minutes: int = 60):
    """Return list of {ts_minute, count} for last N minutes."""
    now_min = int(time.time() // 60)
    buckets = Counter()
    for e in events:
        try:
            m = int(e["ts"] // 60)
            if now_min - m < minutes:
                buckets[m] += 1
        except Exception:
            continue
    result = []
    for m in range(now_min - minutes + 1, now_min + 1):
        result.append({"ts": m * 60, "count": buckets.get(m, 0)})
    return result


# ── Latency distribution (histogram buckets) ──────────────────────────
def _latency_histogram(events):
    buckets = {"0-100ms": 0, "100-200ms": 0, "200-500ms": 0, "500ms-1s": 0, ">1s": 0}
    for e in events:
        if e.get("type") != "hook_invoked" or e.get("hook") != "bm25-memory":
            continue
        d = e.get("duration_ms", 0)
        if d < 100:
            buckets["0-100ms"] += 1
        elif d < 200:
            buckets["100-200ms"] += 1
        elif d < 500:
            buckets["200-500ms"] += 1
        elif d < 1000:
            buckets["500ms-1s"] += 1
        else:
            buckets[">1s"] += 1
    return [{"bucket": k, "count": v} for k, v in buckets.items()]


# ── Samples: invoke real hooks on recent prompts ──────────────────────
# Phase 2a: proves each function works by showing actual prompt → output
# pairs that a human can eye-check for relevance. Reuses the helpers
# from ctx-report.py. Computed on a slower background cadence (60s) than
# the main SSE snapshot (2s) to keep per-tick cost cheap.

import subprocess as _sp

_CHAT_MEMORY_HOOK = HOOK_DIR / "chat-memory.py"

def _run_chat_memory(prompt: str) -> str:
    if not _CHAT_MEMORY_HOOK.exists():
        return ""
    try:
        r = _sp.run(
            ["python3", str(_CHAT_MEMORY_HOOK)],
            input=json.dumps({"prompt": prompt, "cwd": os.getcwd()}),
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout
    except Exception:
        return ""


def _parse_cm(hook_output: str, max_entries: int = 2) -> list:
    """Parse chat-memory stdout. Returns list of {role, project, preview}."""
    # chat-memory emits a header line then JSON; find the `{` line
    json_part = ""
    for line in hook_output.split("\n"):
        if line.strip().startswith("{"):
            json_part = line
            break
    if not json_part:
        return []
    try:
        payload = json.loads(json_part)
        ctx = payload.get("hookSpecificOutput", {}).get("additionalContext", "")
    except Exception:
        return []
    # Find the [CHAT-MEMORY] block
    if "[CHAT-MEMORY]" not in ctx:
        return []
    body = ctx.split("[CHAT-MEMORY]", 1)[1]
    # First line is the header — skip it; then entries separated by \n---\n
    body = body.split("\n", 1)[1] if "\n" in body else body
    entries = body.split("\n---\n")
    out = []
    for entry in entries[:max_entries]:
        entry = entry.strip()
        if not entry.startswith("["):
            continue
        # [user@Project] text...  or  [assistant@Project] text...
        close = entry.find("]")
        if close < 0:
            continue
        tag = entry[1:close]          # "user@CTX"
        rest = entry[close + 1:].strip()
        role, _, project = tag.partition("@")
        out.append({
            "role": role.strip() or "?",
            "project": project.strip() or "?",
            "preview": rest[:120] + ("…" if len(rest) > 120 else ""),
        })
    return out


def _compute_samples(n_prompts: int = 3) -> dict:
    """Pull N recent user prompts from vault.db, invoke real hooks on each,
    return structured samples for the dashboard."""
    prompts = _ctx._recent_user_prompts(n=n_prompts)
    result = {"computed_at": time.time(), "prompts": []}
    for ts, content in prompts:
        preview = content[:120] + ("…" if len(content) > 120 else "")
        bm_out = _ctx._run_bm25_memory(content)
        cm_out = _run_chat_memory(content)
        result["prompts"].append({
            "ts": ts,
            "preview": preview,
            "cm": _parse_cm(cm_out, max_entries=2),
            "g1": _ctx._extract_block(bm_out, "[RECENT DECISIONS]")[:3],
            "g2_docs": _ctx._extract_block(bm_out, "[G2-DOCS]")[:3],
            "g2_prefetch": _ctx._extract_block(bm_out, "[G2-PREFETCH]")[:3],
        })
    return result


# Cached samples + background refresh
SAMPLE_CACHE = {"computed_at": 0, "prompts": []}
SAMPLE_REFRESH_SECONDS = 60


async def _samples_refresher():
    """Background task: recompute samples every SAMPLE_REFRESH_SECONDS."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            # Run in executor because bm25-memory + chat-memory calls are sync
            # and each takes ~200-500ms; don't block the event loop.
            data = await loop.run_in_executor(None, _compute_samples, 3)
            SAMPLE_CACHE.update(data)
        except Exception as e:
            SAMPLE_CACHE["error"] = str(e)
        await asyncio.sleep(SAMPLE_REFRESH_SECONDS)


@app.on_event("startup")
async def _on_startup():
    asyncio.create_task(_samples_refresher())


# ── Recent events tail (for the live stream panel) ────────────────────
def _recent_events(events, n: int = 50):
    tail = events[-n:] if len(events) > n else events
    out = []
    for e in reversed(tail):  # newest first
        ts = e.get("ts", 0)
        out.append({
            "ts": ts,
            "time": datetime.fromtimestamp(ts).strftime("%H:%M:%S") if ts else "",
            "type": e.get("type", "?"),
            "hook": e.get("hook", ""),
            "block": e.get("block") or e.get("to_mode") or e.get("signal") or "",
            "duration_ms": e.get("duration_ms"),
        })
    return out


# ── Build a full snapshot JSON for the dashboard ──────────────────────
def _build_snapshot():
    TAIL.refresh()
    events = TAIL.events
    if not events:
        return {
            "ts": time.time(),
            "empty": True,
            "message": f"No events in {LOG} matching --since=7d",
        }
    data = _ctx._compute_metrics(events)

    # Build health rows
    rows = []
    if data["cm_events"]:
        pct = data["cm_hybrid_pct"]
        ok = pct >= TH["cm_hybrid_pct_min"]
        rows.append({
            "name": "CM hybrid", "value": pct, "value_str": f"{int(pct*100)}%",
            "threshold": TH["cm_hybrid_pct_min"], "ok": ok,
            "msg": "daemon healthy" if ok else "daemon flaky",
        })
    if data["bm_invoked"]:
        g1_ok = data["g1_rate"] < TH["g1_fire_max_concern"]
        rows.append({
            "name": "G1 fire rate", "value": data["g1_rate"],
            "value_str": f"{int(data['g1_rate']*100)}%",
            "threshold": TH["g1_fire_max_concern"], "ok": g1_ok,
            "msg": "selective" if g1_ok else "always fires",
            "info_only": True,
        })
        n_inv = data["n_inv"]
        for block, key, msg_ok, msg_bad in (
            ("g2_docs", "g2_docs_over_concern", "selective", "over-matching"),
            ("g2_grep", "g2_grep_over_concern", "graph fresh", "graph stale"),
        ):
            c = data["block_counts"].get(block, 0)
            if c == 0:
                continue
            rate = c / n_inv
            ok = rate < TH[key]
            rows.append({
                "name": block, "value": rate,
                "value_str": f"{int(rate*100)}% ({c})",
                "threshold": TH[key], "ok": ok,
                "msg": msg_ok if ok else msg_bad,
                "info_only": block == "g2_docs",
            })
        p95 = data["p95"]
        lat_ok = p95 < TH["bm25_p95_ms_yellow"]
        rows.append({
            "name": "Latency p95", "value": min(1.0, p95 / TH["bm25_p95_ms_yellow"]),
            "value_str": f"{p95}ms",
            "threshold": TH["bm25_p95_ms_yellow"], "ok": lat_ok,
            "msg": "fast" if lat_ok else "borderline",
        })

    # Grade from health-critical flags only (info_only rows excluded)
    crit = [r for r in rows if not r.get("info_only")]
    g = sum(1 for r in crit if r["ok"])
    y = sum(1 for r in crit if not r["ok"])
    if y == 0:
        grade = {"label": "ALL GREEN", "style": "green"}
    elif y == 1:
        grade = {"label": "MOSTLY GREEN", "style": "yellow"}
    else:
        grade = {"label": "MIXED", "style": "yellow"}

    # Quality notices
    notices = [{"metric": m, "msg": msg} for m, msg in data["quality_notices"]]

    # Other signals
    other = []
    if data["cm_warnings"]:
        other.append({"label": "CM daemon-down", "count": data["cm_warnings"]})
    if data["decision_hits"]:
        other.append({"label": "decision-keyword", "count": data["decision_hits"]})
    if data["grep_signals"]:
        other.append({"label": "grep-fallback",
                      "count": sum(data["grep_signals"].values())})

    return {
        "ts": time.time(),
        "updated": datetime.now().strftime("%H:%M:%S"),
        "total_events": len(events),
        "window": "7d",
        "grade": grade,
        "rows": rows,
        "activity": _activity_buckets(events, minutes=120),
        "latency_hist": _latency_histogram(events),
        "notices": notices,
        "other": other,
        "recent": _recent_events(events, n=30),
        "samples": SAMPLE_CACHE,
        "thresholds": {
            "cm_hybrid_min": int(TH["cm_hybrid_pct_min"] * 100),
            "g2_docs_max": int(TH["g2_docs_over_concern"] * 100),
            "g2_grep_max": int(TH["g2_grep_over_concern"] * 100),
            "p95_max_ms": TH["bm25_p95_ms_yellow"],
        },
    }


# ── Routes ────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(STATIC / "index.html")


@app.get("/api/snapshot")
async def snapshot():
    return JSONResponse(_build_snapshot())


@app.post("/api/samples/refresh")
async def refresh_samples():
    """Force an immediate samples recompute (ignores the 60s cache)."""
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _compute_samples, 3)
    SAMPLE_CACHE.update(data)
    return JSONResponse({"ok": True, "computed_at": data["computed_at"]})


@app.get("/stream")
async def stream():
    async def gen():
        while True:
            try:
                snap = _build_snapshot()
                yield f"data: {json.dumps(snap)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(2.0)
    return StreamingResponse(gen(), media_type="text/event-stream")


def main():
    import uvicorn
    host = "127.0.0.1"
    port = int(os.environ.get("CTX_DASHBOARD_PORT", "8787"))
    print(f"CTX Dashboard → http://{host}:{port}", flush=True)
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
