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

# Import from sibling ctx-report.py and bm25-memory.py
HOOK_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HOOK_DIR))
import importlib.util
_spec = importlib.util.spec_from_file_location("ctx_report", HOOK_DIR / "ctx-report.py")
_ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ctx)

_bspec = importlib.util.spec_from_file_location("bm25_memory", HOOK_DIR / "bm25-memory.py")
_bm = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(_bm)

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

# Env for dashboard-internal hook invocations — suppresses telemetry
# emission from the child process so the dashboard's own samples/graph
# refresh does not generate new "user events" that re-trigger itself.
_INTERNAL_ENV = {**os.environ, "CTX_DASHBOARD_INTERNAL": "1"}


def _run_chat_memory(prompt: str) -> str:
    if not _CHAT_MEMORY_HOOK.exists():
        return ""
    try:
        r = _sp.run(
            ["python3", str(_CHAT_MEMORY_HOOK)],
            input=json.dumps({"prompt": prompt, "cwd": os.getcwd()}),
            capture_output=True, text=True, timeout=5,
            env=_INTERNAL_ENV,
        )
        return r.stdout
    except Exception:
        return ""


# Override ctx_report._run_bm25_memory to also pass CTX_DASHBOARD_INTERNAL,
# so samples computation (which uses this helper) doesn't emit telemetry.
_original_run_bm25 = _ctx._run_bm25_memory
def _run_bm25_memory_internal(prompt: str) -> str:
    if not _ctx._BM25_HOOK.exists():
        return ""
    try:
        r = _sp.run(
            ["python3", str(_ctx._BM25_HOOK), "--rich"],
            input=json.dumps({"prompt": prompt, "cwd": os.getcwd()}),
            capture_output=True, text=True, timeout=5,
            env=_INTERNAL_ENV,
        )
        return r.stdout
    except Exception:
        return ""
_ctx._run_bm25_memory = _run_bm25_memory_internal


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


# ── Reactive refresh — when new events arrive (user just submitted a
# prompt), invalidate samples + graph caches so the next tick recomputes
# with fresh data. Samples/graph recompute is scheduled in the stream
# handler (non-blocking, runs in executor).
_LAST_EVENT_COUNT = {"n": 0}
_PENDING_REFRESH = {"samples": False, "graph": False}


def _maybe_trigger_reactive_refresh():
    """Called after TAIL.refresh(). If new events arrived, flag caches
    as needing refresh so the SSE loop can kick off the recompute."""
    n = len(TAIL.events)
    if n > _LAST_EVENT_COUNT["n"]:
        _LAST_EVENT_COUNT["n"] = n
        _PENDING_REFRESH["samples"] = True
        _PENDING_REFRESH["graph"] = True


# ── Build a full snapshot JSON for the dashboard ──────────────────────
def _build_snapshot():
    TAIL.refresh()
    _maybe_trigger_reactive_refresh()
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


# ── Knowledge Graph (Phase 3) ─────────────────────────────────────────
# Builds a network of decisions/docs/prompts with edges weighted by BM25
# similarity or temporal co-occurrence. Produces the "Apple patent graph"
# visual the user asked for — compounding knowledge made visible.

from math import log

def _project_dir() -> str:
    """Pick a project root for the graph.
    Priority:
      1. CLAUDE_PROJECT_DIR env (must be a git repo)
      2. CTX_DASHBOARD_PROJECT env
      3. ~/Project/CTX (the active CTX project)
      4. cwd
    """
    for env_key in ("CLAUDE_PROJECT_DIR", "CTX_DASHBOARD_PROJECT"):
        v = os.environ.get(env_key)
        if v and (Path(v) / ".git").exists():
            return v
    ctx_default = Path(os.path.expanduser("~/Project/CTX"))
    if (ctx_default / ".git").exists():
        return str(ctx_default)
    return os.getcwd()


GRAPH_CACHE = {"ts": 0, "data": None, "project_dir": None}
GRAPH_CACHE_SECONDS = 60


def _build_graph(project_dir: str, max_decisions: int = 120,
                 max_docs: int = 40, max_prompts: int = 15) -> dict:
    """Build nodes + edges from decisions, docs, and recent prompts.

    Node types (colored in UI):
      - decision  (teal)     — from git decision corpus
      - doc       (blue)     — from docs/research + CLAUDE.md + MEMORY.md
      - prompt    (grey)     — recent user prompts from vault.db
      - current   (green)    — the most recent prompt (highlighted)

    Edges:
      - decision ↔ decision: temporal (same day) — keeps clusters tight
      - doc ↔ doc:           shared keywords above BM25 threshold
      - prompt → decision/doc: current retrieval cone from bm25_rank on prompt
    """
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        return {"nodes": [], "edges": [], "error": "rank_bm25 not installed"}

    nodes, edges = [], []
    id_counter = [0]
    def nid():
        id_counter[0] += 1
        return f"n{id_counter[0]}"

    # 1. Decisions
    decisions = _bm.get_decision_corpus(project_dir)[:max_decisions]
    decision_nodes = []
    for d in decisions:
        nid_ = nid()
        decision_nodes.append({
            "id": nid_, "type": "decision",
            "label": d["subject"][:40],
            "full": d["subject"],
            "date": d.get("date", ""),
            "tokens": set(_bm.tokenize(d["text"])),
        })
    # 2. Docs — units from build_docs_bm25() are "filename\ncontent" strings
    bm25_docs, units = _bm.build_docs_bm25(project_dir)
    doc_nodes = []
    for unit in (units or [])[:max_docs]:
        fname, _, content = unit.partition("\n")
        nid_ = nid()
        doc_nodes.append({
            "id": nid_, "type": "doc",
            "label": fname[:40],
            "full": fname,
            "tokens": set(_bm.tokenize(content[:2000])),  # sample for speed
        })
    # 3. Recent prompts
    prompt_rows = _ctx._recent_user_prompts(n=max_prompts)
    prompt_nodes = []
    for idx, (ts, content) in enumerate(prompt_rows):
        preview = content[:60].replace("\n", " ")
        is_current = (idx == 0)
        nid_ = nid()
        prompt_nodes.append({
            "id": nid_,
            "type": "current" if is_current else "prompt",
            "label": preview[:30],
            "full": preview,
            "ts": ts,
            "tokens": set(_bm.tokenize(content, drop_stopwords=True)),
        })

    # Build node list (strip tokens before serialization)
    for n in decision_nodes + doc_nodes + prompt_nodes:
        nodes.append({k: v for k, v in n.items() if k != "tokens"})

    # ── Edges ────────────────────────────────────────────────────
    # A. decision ↔ decision (same day → temporal cluster)
    from collections import defaultdict
    by_date = defaultdict(list)
    for d in decision_nodes:
        if d["date"]:
            by_date[d["date"]].append(d["id"])
    for date, ids in by_date.items():
        for i in range(len(ids)):
            for j in range(i + 1, min(i + 4, len(ids))):  # cap 3 per node
                edges.append({
                    "from": ids[i], "to": ids[j],
                    "type": "temporal", "weight": 0.4,
                })

    # B. doc ↔ doc (shared keywords — Jaccard on token sets)
    for i in range(len(doc_nodes)):
        scored = []
        for j in range(len(doc_nodes)):
            if i == j:
                continue
            a, b = doc_nodes[i]["tokens"], doc_nodes[j]["tokens"]
            if not a or not b:
                continue
            jac = len(a & b) / max(1, len(a | b))
            if jac >= 0.08:
                scored.append((jac, j))
        scored.sort(reverse=True)
        for jac, j in scored[:2]:  # keep top-2 similar docs per doc
            if i < j:  # avoid duplicate pairs
                edges.append({
                    "from": doc_nodes[i]["id"], "to": doc_nodes[j]["id"],
                    "type": "topic", "weight": float(jac),
                })

    # C. prompt → decision/doc (current retrieval cone)
    if prompt_nodes:
        # BM25 over decisions for each prompt
        dec_tokens = [list(d["tokens"]) for d in decision_nodes]
        doc_tokens = [list(d["tokens"]) for d in doc_nodes]
        bm25_dec = BM25Okapi(dec_tokens) if dec_tokens else None
        bm25_doc = BM25Okapi(doc_tokens) if doc_tokens else None

        for p in prompt_nodes:
            q = list(p["tokens"])
            if not q:
                continue
            # Top 5 decisions
            if bm25_dec:
                dscores = bm25_dec.get_scores(q)
                for i in sorted(range(len(dscores)),
                                key=lambda i: dscores[i], reverse=True)[:5]:
                    if dscores[i] >= 0.5:
                        edges.append({
                            "from": p["id"], "to": decision_nodes[i]["id"],
                            "type": "recall-d",
                            "weight": float(dscores[i]),
                            "current": p["type"] == "current",
                        })
            # Top 5 docs
            if bm25_doc:
                dscores = bm25_doc.get_scores(q)
                for i in sorted(range(len(dscores)),
                                key=lambda i: dscores[i], reverse=True)[:5]:
                    if dscores[i] >= 1.0:
                        edges.append({
                            "from": p["id"], "to": doc_nodes[i]["id"],
                            "type": "recall-w",
                            "weight": float(dscores[i]),
                            "current": p["type"] == "current",
                        })

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "decisions": len(decision_nodes),
            "docs": len(doc_nodes),
            "prompts": len(prompt_nodes),
            "edges": len(edges),
        },
    }


def _get_graph_cached() -> dict:
    """Return cached graph or rebuild if stale."""
    now = time.time()
    project_dir = _project_dir()
    if (GRAPH_CACHE["data"] is not None
            and GRAPH_CACHE["project_dir"] == project_dir
            and now - GRAPH_CACHE["ts"] < GRAPH_CACHE_SECONDS):
        return GRAPH_CACHE["data"]
    data = _build_graph(project_dir)
    GRAPH_CACHE.update({"ts": now, "data": data, "project_dir": project_dir})
    return data


# ── Routes ────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(STATIC / "index.html")


@app.get("/api/snapshot")
async def snapshot():
    return JSONResponse(_build_snapshot())


@app.get("/api/graph")
async def graph():
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _get_graph_cached)
    return JSONResponse(data)


@app.post("/api/graph/refresh")
async def refresh_graph():
    GRAPH_CACHE["ts"] = 0   # invalidate cache
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _get_graph_cached)
    return JSONResponse({"ok": True, "stats": data.get("stats", {})})


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
        loop = asyncio.get_event_loop()
        while True:
            try:
                snap = _build_snapshot()
                yield f"data: {json.dumps(snap)}\n\n"
                # Reactive: if new events arrived this tick, kick off
                # non-blocking samples + graph recompute so the NEXT tick
                # has fresh data visible to the user.
                if _PENDING_REFRESH["samples"]:
                    _PENDING_REFRESH["samples"] = False
                    async def _refresh_samples():
                        try:
                            data = await loop.run_in_executor(None, _compute_samples, 3)
                            SAMPLE_CACHE.update(data)
                        except Exception:
                            pass
                    asyncio.create_task(_refresh_samples())
                if _PENDING_REFRESH["graph"]:
                    _PENDING_REFRESH["graph"] = False
                    GRAPH_CACHE["ts"] = 0  # invalidate so next /api/graph rebuilds
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
