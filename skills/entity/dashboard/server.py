#!/usr/bin/env python3
"""
entity-corpus-dash server — FastAPI web dashboard for corpus-registry.yaml

Usage:
    python3 ~/.claude/skills/entity/dashboard/server.py
  or via launch script:
    entity-corpus
"""
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

REGISTRY = Path.home() / ".claude/skills/entity/corpus-registry.yaml"
CORPORA_DIR = Path.home() / ".claude/skills/entity/corpora"
MISS_LOG = Path.home() / ".omc/corpus-miss-log.json"
HERE = Path(__file__).parent
STATIC = HERE / "static"

HOST = os.environ.get("ENTITY_DASH_HOST", "127.0.0.1")
PORT = int(os.environ.get("ENTITY_DASH_PORT", "8989"))

app = FastAPI(title="Entity Corpus Dashboard", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ── Registry parser ───────────────────────────────────────────────────────────

def _extract_field(block: str, key: str):
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", block, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _extract_docs(block: str) -> dict:
    m = re.search(r"^docs:\n((?:  .+\n?)+)", block, re.MULTILINE)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        item = re.match(r"\s+(\w+):\s*(.+)$", line)
        if item:
            v = item.group(2).strip().strip('"').strip("'")
            v = re.sub(r"\s+#\s+.*$", "", v).strip()
            result[item.group(1)] = v
    return result


def _extract_taxonomy(block: str) -> dict:
    m = re.search(r"^taxonomy_groups:\n((?:  \w+: \[.+\]\n?)+)", block, re.MULTILINE)
    if not m:
        return {}
    tg = {}
    for line in m.group(1).splitlines():
        gm = re.match(r"\s+(\w+): \[(.+)\]", line)
        if gm:
            tg[gm.group(1)] = [x.strip() for x in gm.group(2).split(",")]
    return tg


def _extract_triggers(block: str) -> list:
    m = re.search(r"^trigger:\n((?:  - .+\n?)+)", block, re.MULTILINE)
    if not m:
        return []
    return [x.strip().strip('"').strip("'") for x in re.findall(r"^\s+- (.+)$", m.group(1), re.MULTILINE)]


def _extract_core_theory(block: str) -> str:
    ct = re.search(r"^core_theory:\s*\|\n((?:  .+\n?)+)", block, re.MULTILINE)
    if ct:
        lines = [l[2:] if l.startswith("  ") else l for l in ct.group(1).splitlines()]
        return "\n".join(lines)
    return ""


def _extract_related(block: str) -> list:
    m = re.search(r"^related_domains:\n((?:  - .+\n?)+)", block, re.MULTILINE)
    if not m:
        # Try inline form: related_domains: [a, b, c]
        m2 = re.search(r"^related_domains:\s*\[(.+)\]$", block, re.MULTILINE)
        if m2:
            return [x.strip() for x in m2.group(1).split(",")]
        return []
    return [x.strip().strip('"').strip("'") for x in re.findall(r"^\s+- (.+)$", m.group(1), re.MULTILINE)]


def count_actual_files(corpus_root: str, registered_files: set) -> int:
    root = Path(os.path.expanduser(corpus_root))
    if not root.is_dir():
        return 0
    if registered_files:
        return len([f for f in root.iterdir() if f.name in registered_files])
    return len(list(root.glob("*.md")))


def last_modified_ts(corpus_root: str, registered_files: set) -> float:
    root = Path(os.path.expanduser(corpus_root))
    if not root.is_dir():
        return 0.0
    try:
        files = [root / f for f in registered_files if (root / f).exists()]
        if not files:
            files = list(root.glob("*.md"))
        if not files:
            return 0.0
        return max(f.stat().st_mtime for f in files)
    except Exception:
        return 0.0


def load_registry() -> list:
    if not REGISTRY.exists():
        return []
    raw = REGISTRY.read_text(encoding="utf-8")
    blocks = [b.strip() for b in raw.split("---") if b.strip()]
    corpora = []
    for block in blocks:
        name = _extract_field(block, "name")
        if not name:
            continue
        docs = _extract_docs(block)
        tg = _extract_taxonomy(block)
        registered_files = set(docs.values())
        corpus_root = _extract_field(block, "corpus_root") or ""
        n_files = count_actual_files(corpus_root, registered_files)
        mtime = last_modified_ts(corpus_root, registered_files)
        root_exists = Path(os.path.expanduser(corpus_root)).is_dir() if corpus_root else False

        now_ts = datetime.now().timestamp()
        days_old = round((now_ts - mtime) / 86400, 1) if mtime else None
        if days_old is None:       staleness = "unknown"
        elif days_old < 7:         staleness = "fresh"
        elif days_old < 30:        staleness = "aging"
        else:                      staleness = "stale"

        corpora.append({
            "name": name,
            "status": _extract_field(block, "status") or "unknown",
            "primary_domain": _extract_field(block, "primary_domain") or "?",
            "related_domains": _extract_related(block),
            "layer": _extract_field(block, "layer") or "?",
            "domain": _extract_field(block, "domain") or "",
            "corpus_root": corpus_root,
            "root_exists": root_exists,
            "docs": docs,
            "doc_count": len(docs),
            "file_count": n_files,
            "file_match": n_files == len(docs) if docs else None,
            "taxonomy_groups": tg,
            "triggers": _extract_triggers(block),
            "core_theory": _extract_core_theory(block),
            "last_modified": mtime,
            "last_modified_str": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M") if mtime else "—",
            "days_old": days_old,
            "staleness": staleness,
        })
    return corpora


def load_miss_log() -> dict:
    if not MISS_LOG.exists():
        return {}
    try:
        return json.loads(MISS_LOG.read_text())
    except Exception:
        return {}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse(str(STATIC / "index.html"))


@app.get("/api/corpora")
async def api_corpora():
    corpora = load_registry()
    miss_log = load_miss_log()

    total_docs = sum(c["doc_count"] for c in corpora)
    stable = sum(1 for c in corpora if c["status"] == "stable")
    draft = sum(1 for c in corpora if c["status"] == "draft")

    return JSONResponse({
        "corpora": corpora,
        "miss_log": miss_log,
        "summary": {
            "total": len(corpora),
            "stable": stable,
            "draft": draft,
            "total_docs": total_docs,
            "registry_path": str(REGISTRY),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    })


@app.get("/api/corpus/{name}")
async def api_corpus_detail(name: str):
    corpora = load_registry()
    match = next((c for c in corpora if c["name"] == name), None)
    if not match:
        return JSONResponse({"error": f"Corpus '{name}' not found"}, status_code=404)

    # Add actual file listing
    root = Path(os.path.expanduser(match["corpus_root"]))
    file_listing = []
    if root.is_dir():
        for f in sorted(root.iterdir()):
            if f.name in set(match["docs"].values()):
                file_listing.append({"name": f.name, "size": f.stat().st_size})

    match["file_listing"] = file_listing
    return JSONResponse(match)


@app.get("/stream")
async def stream(request: Request):
    """SSE stream — pushes corpus snapshot every 5 seconds."""
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            corpora = load_registry()
            miss_log = load_miss_log()
            total_docs = sum(c["doc_count"] for c in corpora)
            stable = sum(1 for c in corpora if c["status"] == "stable")
            data = json.dumps({
                "corpora": corpora,
                "miss_log": miss_log,
                "summary": {
                    "total": len(corpora),
                    "stable": stable,
                    "draft": len(corpora) - stable,
                    "total_docs": total_docs,
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
