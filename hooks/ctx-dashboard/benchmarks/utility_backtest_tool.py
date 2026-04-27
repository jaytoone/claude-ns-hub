#!/usr/bin/env python3
"""Tool-use-aware backtest — closes the blind spot that made v2 T2 judge
rates collapse to ~10%.

Key difference from utility_backtest.py: samples pairs directly from
Claude Code transcript .jsonl files (not vault.db). Transcripts preserve
the full assistant message including tool_use blocks with their input
parameters (file paths, commands, patterns, etc.) — vault.db stores only
the final text content so it cannot support tool-aware scoring.

For each user→assistant pair:
  1. Run bm25-memory on the prompt (with correct project cwd)
  2. Score each injected item against:
     a. response text (substring + semantic) — existing behavior
     b. tool_use parameters (substring only) — NEW
  3. Report rate on each stream and their union

Output: text-only rate vs text+tool rate. The delta = blind-spot size.
"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from collections import defaultdict

HOME = Path(os.path.expanduser("~"))
PROJECTS_DIR = HOME / ".claude" / "projects"
INJ_FILE = HOME / ".claude" / "last-injection.json"
BM25_HOOK = HOME / ".claude" / "hooks" / "bm25-memory.py"
VEC_SOCK = HOME / ".local" / "share" / "claude-vault" / "vec-daemon.sock"
SEMANTIC_THRESHOLD = 0.85

N_SAMPLES = 60
PER_PROJECT_CAP = 10
MIN_PROMPT_LEN = 40
MAX_PROMPT_LEN = 400
MIN_RESPONSE_LEN = 100    # lower than text-only backtest — tool-heavy turns have short text

_TOOL_USE_STRING_KEYS = {
    "file_path", "notebook_path", "command", "pattern", "path",
    "description", "prompt", "query", "url", "old_string", "new_string",
    "subagent_type",
}


def _project_dir_to_cwd(project_name: str) -> str | None:
    """Reverse the '/' → '-' encoding Claude Code uses for project dir names."""
    if not project_name.startswith("-"):
        return None
    cwd = project_name.replace("-", "/")
    return cwd if os.path.isdir(cwd) else None


def _extract_tool_params(content) -> str:
    """Flatten tool_use block inputs into a single searchable string."""
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for c in content:
        if not (isinstance(c, dict) and c.get("type") == "tool_use"):
            continue
        name = c.get("name", "")
        if name:
            parts.append(name)
        inp = c.get("input", {}) or {}
        for k, v in inp.items():
            if k not in _TOOL_USE_STRING_KEYS:
                continue
            if isinstance(v, str):
                parts.append(v[:800])
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        parts.append(item[:400])
    return "\n".join(parts)[:4000]


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            t = c.get("text", "")
            if t and t.strip():
                parts.append(t)
    return "\n".join(parts)


def sample_pairs_from_transcripts(n: int) -> list:
    """Walk recent project transcripts, pick user→assistant adjacent pairs.
    Returns (prompt, response_text, tool_params, cwd, project_name)."""
    # Get all transcript files across projects, newest first by mtime
    transcripts: list = []
    if not PROJECTS_DIR.exists():
        return []
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        cwd = _project_dir_to_cwd(proj_dir.name)
        if not cwd:
            continue
        for f in proj_dir.glob("*.jsonl"):
            transcripts.append((f, proj_dir.name, cwd))
    transcripts.sort(key=lambda t: t[0].stat().st_mtime, reverse=True)

    out: list = []
    per_project = defaultdict(int)
    for tpath, pname, cwd in transcripts:
        if len(out) >= n:
            break
        if per_project[pname] >= PER_PROJECT_CAP:
            continue
        try:
            pairs = _extract_pairs(tpath)
        except Exception:
            continue
        for prompt, response_text, tool_params in pairs:
            if len(prompt) < MIN_PROMPT_LEN or len(prompt) > MAX_PROMPT_LEN:
                continue
            # Skip command/system messages
            if prompt.startswith("[tool_") or prompt.startswith("Caveat:") or prompt.startswith("<command-"):
                continue
            # Require EITHER meaningful response text OR tool-params (don't skip
            # tool-heavy turns — that's the whole point)
            if len(response_text) < MIN_RESPONSE_LEN and len(tool_params) < 40:
                continue
            out.append((prompt, response_text, tool_params, cwd, pname))
            per_project[pname] += 1
            if per_project[pname] >= PER_PROJECT_CAP or len(out) >= n:
                break
    return out


def _extract_pairs(transcript_path: Path) -> list:
    """Walk a .jsonl and return list of (prompt, response_text, tool_params)
    for each user→assistant adjacency."""
    last_user_text: str | None = None
    current_resp_text: list[str] = []
    current_resp_tools: list[str] = []
    emitted_for_user = False
    out: list = []
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line.strip())
            except Exception:
                continue
            t = d.get("type")
            if t == "user":
                # Finalize pending assistant response if any
                if last_user_text is not None and (current_resp_text or current_resp_tools) and not emitted_for_user:
                    out.append((last_user_text,
                                "\n".join(current_resp_text),
                                "\n".join(current_resp_tools)[:4000]))
                    emitted_for_user = True
                msg = d.get("message", {})
                content = msg.get("content", "")
                last_user_text = _extract_text(content) if isinstance(content, (list, str)) else ""
                current_resp_text = []
                current_resp_tools = []
                emitted_for_user = False
                continue
            if t != "assistant":
                continue
            msg = d.get("message", {})
            content = msg.get("content", [])
            text = _extract_text(content)
            if text:
                current_resp_text.append(text)
            tp = _extract_tool_params(content)
            if tp:
                current_resp_tools.append(tp)
    # Tail: if transcript ended without a trailing user turn
    if last_user_text is not None and (current_resp_text or current_resp_tools) and not emitted_for_user:
        out.append((last_user_text,
                    "\n".join(current_resp_text),
                    "\n".join(current_resp_tools)[:4000]))
    return out


def run_bm25(prompt: str, cwd: str) -> list:
    env = {**os.environ}
    env.pop("CTX_DASHBOARD_INTERNAL", None)
    env["CLAUDE_PROJECT_DIR"] = cwd
    try:
        INJ_FILE.unlink()
    except FileNotFoundError:
        pass
    try:
        subprocess.run(
            ["python3", str(BM25_HOOK), "--rich"],
            input=json.dumps({"prompt": prompt, "cwd": cwd}),
            capture_output=True, text=True, timeout=8, env=env, cwd=cwd,
        )
    except Exception:
        return []
    if not INJ_FILE.exists():
        return []
    try:
        return json.loads(INJ_FILE.read_text()).get("items", [])
    except Exception:
        return []


def _embed(text: str):
    if not VEC_SOCK.exists() or not text:
        return None
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(0.8)
        s.connect(str(VEC_SOCK))
        s.sendall((json.dumps({"q": text[:1000]}) + "\n").encode("utf-8"))
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk: break
            buf += chunk
        s.close()
        resp = json.loads(buf.split(b"\n", 1)[0].decode("utf-8"))
        if resp.get("ok"):
            return resp.get("emb")
    except Exception:
        pass
    return None


def _cosine(a, b):
    if not a or not b: return 0.0
    return sum(x * y for x, y in zip(a, b))


def _chunk(text, size=400, overlap=80):
    if not text: return []
    out = []
    for p in text.split("\n\n"):
        p = p.strip()
        if not p: continue
        if len(p) <= size:
            out.append(p)
        else:
            i = 0
            while i < len(p):
                out.append(p[i:i+size])
                i += size - overlap
    return out[:20]


def score_item(item: dict, response_text: str, tool_params: str, chunk_embs: list) -> dict:
    tokens = item.get("tokens", [])
    rl = response_text.lower()
    tl = tool_params.lower()

    sub_hit = any(len(t) >= 4 and t.lower() in rl for t in tokens)
    sem_hit = False
    if chunk_embs:
        item_text = item.get("subject") or " ".join(tokens)
        if item_text:
            item_emb = _embed(item_text)
            if item_emb:
                max_sim = max((_cosine(item_emb, ce) for ce in chunk_embs), default=0.0)
                sem_hit = max_sim >= SEMANTIC_THRESHOLD
    tool_hit = bool(tl) and any(len(t) >= 4 and t.lower() in tl for t in tokens)

    text_hit = sub_hit or sem_hit
    return {
        "text_hit": text_hit,
        "tool_hit": tool_hit,
        "either": text_hit or tool_hit,
        "block": item.get("block", "?"),
    }


def main():
    print(f"Sampling {N_SAMPLES} pairs from transcripts …")
    pairs = sample_pairs_from_transcripts(N_SAMPLES)
    print(f"Got {len(pairs)} pairs covering {len(set(p[4] for p in pairs))} projects\n")

    total = 0
    text_hits = 0
    tool_hits = 0
    either_hits = 0
    block_stats = defaultdict(lambda: {"total": 0, "text": 0, "tool": 0, "either": 0})
    tool_only_hits = 0   # items missed by text but caught by tool
    t0 = time.time()

    for i, (prompt, resp_text, tool_params, cwd, project) in enumerate(pairs, 1):
        items = run_bm25(prompt, cwd)
        chunk_embs = [e for e in (_embed(c) for c in _chunk(resp_text)) if e]

        for it in items:
            r = score_item(it, resp_text, tool_params, chunk_embs)
            total += 1
            b = r["block"]
            block_stats[b]["total"] += 1
            if r["text_hit"]:
                text_hits += 1
                block_stats[b]["text"] += 1
            if r["tool_hit"]:
                tool_hits += 1
                block_stats[b]["tool"] += 1
            if r["either"]:
                either_hits += 1
                block_stats[b]["either"] += 1
            if r["tool_hit"] and not r["text_hit"]:
                tool_only_hits += 1

        if i % 5 == 0 or i == len(pairs):
            elapsed = time.time() - t0
            print(f"  [{i}/{len(pairs)}] elapsed={elapsed:.1f}s  items_so_far={total}  "
                  f"either_rate={either_hits/max(1,total):.0%}")

    print("\n" + "="*64)
    print(f"TOOL-AWARE BACKTEST — n={len(pairs)} turns, {total} items")
    print("="*64)

    def wilson(y, n, z=1.96):
        import math
        if n == 0: return (0.0, 0.0)
        p = y/n
        denom = 1 + z*z/n
        center = (p + z*z/(2*n)) / denom
        half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
        return (max(0, center-half), min(1, center+half))

    def line(label, hits, tot):
        p = hits/max(1,tot)
        lo, hi = wilson(hits, tot)
        print(f"{label:<26} {hits:>5}/{tot:<5}  {p:>6.1%}  95% CI [{lo:.1%}, {hi:.1%}]  ±{(hi-lo)*50:.1f}pp")

    line("TEXT-only rate:", text_hits, total)
    line("TOOL-only rate:", tool_hits, total)
    line("EITHER (union):", either_hits, total)
    print(f"{'TOOL-only catches:':<26} {tool_only_hits:>5} items missed by text — "
          f"+{tool_only_hits/max(1,total)*100:.1f}pp blind-spot recovery")
    print()

    print("Per-block (either):")
    for b, d in sorted(block_stats.items()):
        if d["total"] == 0: continue
        line(f"  {b:<20}", d["either"], d["total"])


if __name__ == "__main__":
    main()
