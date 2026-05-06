#!/usr/bin/env python3
"""
Hub server — unified portal aggregating CTX, Entity Corpus, and North Star.
North Star is a first-class built-in page (multi-project manager), not an iframe.
"""
import asyncio
import json
import os
import re
import subprocess
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx

HERE = Path(__file__).parent
STATIC = HERE / "static"
NORTHSTAR_DATA = HERE / "northstar.json"        # legacy fallback
PROJECTS_DIR = HERE / "projects"                 # new: per-project markdown files

HOST = os.environ.get("HUB_HOST", "127.0.0.1")
PORT = int(os.environ.get("HUB_PORT", "9000"))


def _tailscale_interface_ip() -> str:
    """Get the IP assigned to the Tailscale interface (100.x.x.x/32)."""
    try:
        r = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, timeout=2)
        m = re.search(r"(100\.\d+\.\d+\.\d+)/32", r.stdout)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "127.0.0.1"


def _bound_ip(port: int) -> str:
    try:
        r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=2)
        for line in r.stdout.splitlines():
            if f":{port}" in line and "LISTEN" in line:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+):" + str(port), line)
                if m:
                    ip = m.group(1)
                    return "127.0.0.1" if ip == "0.0.0.0" else ip
    except Exception:
        pass
    return "127.0.0.1"


def _ctx_url() -> str:
    return f"http://{_bound_ip(8787)}:8787"


def _corpus_url() -> str:
    ip = _bound_ip(8989)
    return f"http://{ip}:8989"


SERVICES = {
    "ctx":    {"port": 8787, "label": "CTX",    "url": _ctx_url()},
    "corpus": {"port": 8989, "label": "Corpus", "url": _corpus_url()},
}

app = FastAPI(title="Hub", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC / "index.html"))


@app.get("/config")
async def config():
    ctx_url    = _ctx_url()
    corpus_url = _corpus_url()
    return JSONResponse({
        "ctx_url":            ctx_url,
        "corpus_url":         corpus_url,
        "northstar_url":      "/northstar",
        "market_signals_url": "/market-signals",
        "ctx_ip":             ctx_url.split("//")[1].split(":")[0],
    })


# ── North Star — built-in multi-project manager ───────────────────────────────

@app.get("/northstar")
async def northstar_page():
    return FileResponse(str(STATIC / "northstar.html"))


@app.get("/api/northstar")
async def northstar_get():
    if NORTHSTAR_DATA.exists():
        return JSONResponse(json.loads(NORTHSTAR_DATA.read_text()))
    return JSONResponse([])


@app.post("/api/northstar")
async def northstar_save(request: Request):
    data = await request.json()
    NORTHSTAR_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return JSONResponse({"ok": True})


@app.get("/api/ctx-pulse")
async def ctx_pulse():
    """Pull recent work focus from CTX graph — hot nodes = actual work direction."""
    ctx_url = _ctx_url()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{ctx_url}/api/graph")
            d = r.json()
        nodes = d.get("nodes", [])
        hot = sorted(nodes, key=lambda n: n.get("utility_heat_raw", 0), reverse=True)[:15]
        topics = [{"type": n.get("type","?"), "label": n.get("label",""), "heat": round(n.get("utility_heat_raw",0),2)} for n in hot]
        stats = d.get("stats", {})
        return JSONResponse({"topics": topics, "stats": stats, "ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e), "topics": []})


@app.post("/api/northstar/align")
async def northstar_align(request: Request):
    """Alignment check: does recent work direction match the north star?"""
    body = await request.json()
    project = body.get("project", {})
    topics = body.get("topics", [])

    topics_text = "\n".join(
        f"  [{t.get('type','?')}] {t.get('label','')} (heat={t.get('heat',0)})"
        for t in topics[:12]
    ) or "  (no recent activity)"

    prompt = f"""You are evaluating alignment between a project's north star goal and the developer's actual recent work.

PROJECT: {project.get('name','?')}
NORTH STAR METRIC: {project.get('metric','?')}
TARGET: {project.get('target','?')}
STATUS: {project.get('status','?')}
NOTES: {project.get('note','(none)')}

RECENT WORK ACTIVITY (from session memory, hot = frequently referenced):
{topics_text}

Evaluate:
1. Is the recent work ADVANCING the north star? (directly contributing)
2. Is it NEUTRAL? (infrastructure/maintenance that eventually helps)
3. Is it DIVERGENT? (pulling focus away from north star)

Respond in this exact JSON (no markdown):
{{"alignment": "ADVANCING|NEUTRAL|DIVERGENT", "score": 0, "summary": "one sentence", "gap": "what's missing or misaligned", "redirect": "specific action to realign work toward north star"}}

score: 0-100 (100 = perfectly aligned). Be honest and direct."""

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: subprocess.run(
            ["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt],
            capture_output=True, text=True, timeout=120
        )
    )
    if result.returncode != 0:
        return JSONResponse({"error": result.stderr[:200] or "claude CLI failed"}, status_code=500)
    raw = result.stdout.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    return JSONResponse(json.loads(raw.strip()))


@app.post("/api/northstar/eval")
async def northstar_eval(request: Request):
    body = await request.json()
    project = body.get("project", {})

    milestones_text = "\n".join(
        f"  {'[x]' if m.get('done') else '[ ]'} {m.get('text','')}"
        for m in project.get("milestones", [])
    ) or "  (none)"

    log_text = "\n".join(
        f"  {l.get('date','')} — {l.get('text','')}"
        for l in project.get("log", [])[-5:]
    ) or "  (none)"

    prompt = f"""You are a multi-expert panel evaluating a project's North Star goal.
Analyze from exactly 5 lenses. Be concise, direct, specific to this project.

PROJECT: {project.get('name','?')}
NORTH STAR METRIC: {project.get('metric','?')}
CURRENT VALUE: {project.get('current','?')}
TARGET: {project.get('target','?')}
STATUS: {project.get('status','?')}
DEADLINE: {project.get('deadline','(not set)')}
NOTES: {project.get('note','(none)')}
MILESTONES:
{milestones_text}
PROGRESS LOG:
{log_text}

Respond in this EXACT JSON (no markdown, no extra text):
{{"lenses":[{{"name":"Clarity","icon":"◈","verdict":"PASS","summary":"one sentence","detail":"2-3 sentences"}},{{"name":"Feasibility","icon":"◉","verdict":"PASS","summary":"one sentence","detail":"2-3 sentences"}},{{"name":"Moat","icon":"◎","verdict":"PASS","summary":"one sentence","detail":"2-3 sentences"}},{{"name":"Leading Indicator","icon":"◇","verdict":"PASS","summary":"one sentence","detail":"2-3 sentences"}},{{"name":"Risk","icon":"△","verdict":"PASS","summary":"one sentence","detail":"2-3 sentences"}}],"verdict":"STRONG","top_action":"specific next action"}}

verdict per lens: PASS or WARN or FAIL. overall verdict: STRONG or MODERATE or WEAK."""

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: subprocess.run(
            ["claude", "-p", "--model", "claude-haiku-4-5-20251001", prompt],
            capture_output=True, text=True, timeout=120
        )
    )

    if result.returncode != 0:
        return JSONResponse({"error": result.stderr[:200] or "claude CLI failed"}, status_code=500)

    raw = result.stdout.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    raw = raw.strip()

    parsed = json.loads(raw)
    return JSONResponse(parsed)


# ── Health checks ─────────────────────────────────────────────────────────────


# ── Market Signals — built-in page ───────────────────────────────────────────

_MARKET_SIGNALS_SCRIPT = Path.home() / "Project" / "CTX" / "scripts" / "market-signals.py"
_MARKET_SIGNALS_LOG    = Path.home() / "Project" / "CTX" / "docs" / "research" / "signal-log.jsonl"
_MS_CACHE: dict = {"data": None, "ts": 0.0}
_MS_TTL = 300  # 5 min


def _fetch_signals_sync() -> dict:
    if not _MARKET_SIGNALS_SCRIPT.exists():
        return {"error": f"script not found: {_MARKET_SIGNALS_SCRIPT}"}
    try:
        r = subprocess.run(
            ["python3", str(_MARKET_SIGNALS_SCRIPT), "--json"],
            capture_output=True, text=True, timeout=25,
        )
        return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[:200]}
    except Exception as exc:
        return {"error": str(exc)}


def _load_signal_history(n: int = 10) -> list:
    if not _MARKET_SIGNALS_LOG.exists():
        return []
    lines = []
    try:
        for line in _MARKET_SIGNALS_LOG.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return lines[-n:]


@app.get("/market-signals")
async def market_signals_page():
    return FileResponse(str(STATIC / "market-signals.html"))


@app.get("/api/market-signals")
async def market_signals_api(refresh: bool = False):
    import time
    now = time.time()
    if refresh or _MS_CACHE["data"] is None or (now - _MS_CACHE["ts"]) > _MS_TTL:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _fetch_signals_sync)
        _MS_CACHE["data"] = data
        _MS_CACHE["ts"] = now
    return JSONResponse({
        "signals":   _MS_CACHE["data"],
        "history":   _load_signal_history(),
        "cached_at": _MS_CACHE["ts"],
        "ttl":       _MS_TTL,
    })


@app.post("/api/market-signals/save")
async def market_signals_save():
    """Append current signals to signal-log.jsonl."""
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _fetch_signals_sync)
    import time, json as _json
    data["ts"] = data.get("ts") or time.time()
    try:
        with _MARKET_SIGNALS_LOG.open("a") as f:
            f.write(_json.dumps(data) + "\n")
        return JSONResponse({"ok": True})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)})


@app.get("/health/{service}")
async def health(service: str):
    if service in ("northstar", "market-signals"):
        return JSONResponse({"ok": True})
    svc = SERVICES.get(service)
    if not svc:
        return JSONResponse({"ok": False, "error": "unknown service"}, status_code=404)
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(svc["url"])
            return JSONResponse({"ok": r.status_code < 500, "status": r.status_code})
    except Exception:
        return JSONResponse({"ok": False, "status": 0})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
