#!/usr/bin/env python3
"""Backtest CTX's utility-rate metric against historical vault.db conversations.

For each past (user_prompt, assistant_response) pair:
  1. Run bm25-memory on the prompt (with the prompt's ORIGINAL project cwd)
  2. Read what tokens got captured in last-injection.json
  3. Substring-match tokens against the REAL assistant response
  4. Record per-block hit rate

Aggregates give the actual utility distribution across real usage —
no waiting for data to accumulate.
"""
import json
import os
import random
import socket
import subprocess
import sqlite3
import time
from pathlib import Path
from collections import defaultdict

VAULT_DB = Path(os.path.expanduser("~/.local/share/claude-vault/vault.db"))
INJ_FILE = Path(os.path.expanduser("~/.claude/last-injection.json"))
BM25_HOOK = Path(os.path.expanduser("~/.claude/hooks/bm25-memory.py"))
VEC_SOCK = Path(os.path.expanduser("~/.local/share/claude-vault/vec-daemon.sock"))
SEMANTIC_THRESHOLD = 0.85   # calibrated: related >= 0.84, unrelated <= 0.78 (e5-small)

N_SAMPLES = 50           # semantic mode adds ~10× latency per pair (embed calls)
MODES = ["substring", "hybrid"]    # run T0 baseline + T0+T1 hybrid on each pair
MIN_PROMPT_LEN = 40
MAX_PROMPT_LEN = 400
MIN_RESPONSE_LEN = 200   # tiny responses aren't informative

def project_to_cwd(project: str) -> str | None:
    if not project or not project.startswith("-"):
        return None
    candidate = project.replace("-", "/")
    return candidate if os.path.isdir(candidate) else None


def sample_pairs(n: int) -> list:
    """Pick N (user_prompt, next_assistant_response, cwd) tuples, across projects.
    Uses a SQL self-join to find user→assistant adjacency within the same session."""
    c = sqlite3.connect(f"file:{VAULT_DB}?mode=ro", uri=True)
    rows = c.execute(f"""
        SELECT u.content, a.content, s.project, u.id
        FROM messages u
        JOIN messages a ON a.session_id = u.session_id AND a.id = (
            SELECT MIN(id) FROM messages WHERE session_id=u.session_id AND id>u.id AND role='assistant'
        )
        JOIN sessions s ON u.session_id = s.session_id
        WHERE u.role='user'
          AND length(u.content) BETWEEN {MIN_PROMPT_LEN} AND {MAX_PROMPT_LEN}
          AND u.content NOT LIKE '[tool_%'
          AND u.content NOT LIKE 'Caveat:%'
          AND u.content NOT LIKE '<command-%'
          AND length(a.content) >= {MIN_RESPONSE_LEN}
        ORDER BY u.id DESC LIMIT {n * 6}
    """).fetchall()
    c.close()
    # Dedup by project (keep variety) + filter to pairs with a real cwd
    out = []
    seen_projects = defaultdict(int)
    for prompt, response, project, _id in rows:
        cwd = project_to_cwd(project)
        if not cwd:
            continue
        if seen_projects[project] >= 25:  # cap per-project (larger for N=200)
            continue
        out.append((prompt, response, cwd, project))
        seen_projects[project] += 1
        if len(out) >= n:
            break
    return out


def run_bm25(prompt: str, cwd: str) -> list:
    """Invoke bm25-memory + read the resulting last-injection.json items."""
    env = {**os.environ}
    env.pop("CTX_DASHBOARD_INTERNAL", None)   # must NOT be set — we need the injection write
    env["CLAUDE_PROJECT_DIR"] = cwd
    # Clear state so we don't read a stale file
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


def _embed(text: str) -> list | None:
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
    return sum(x*y for x, y in zip(a, b))


def _chunk_response(text: str, size: int = 400, overlap: int = 80) -> list:
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


def score(items: list, response: str, mode: str = "hybrid") -> dict:
    """mode: 'substring' (T0), 'semantic' (T1-only), 'hybrid' (sub OR sem)."""
    rl = response.lower()
    by_block = defaultdict(lambda: [0, 0])
    total_ref = 0

    # Pre-embed response chunks if semantic-needed
    chunk_embs = []
    if mode in ("semantic", "hybrid"):
        for chunk in _chunk_response(response):
            e = _embed(chunk)
            if e: chunk_embs.append(e)

    for it in items:
        b = it.get("block", "?")
        by_block[b][1] += 1

        sub_hit = any(len(t) >= 4 and t.lower() in rl for t in it.get("tokens", []))
        sem_hit = False
        if mode in ("semantic", "hybrid") and chunk_embs:
            item_text = it.get("subject") or " ".join(it.get("tokens", []))
            if item_text:
                item_emb = _embed(item_text)
                if item_emb:
                    max_sim = max((_cosine(item_emb, ce) for ce in chunk_embs), default=0.0)
                    sem_hit = max_sim >= SEMANTIC_THRESHOLD

        if mode == "substring":
            hit = sub_hit
        elif mode == "semantic":
            hit = sem_hit
        else:   # hybrid
            hit = sub_hit or sem_hit

        if hit:
            by_block[b][0] += 1
            total_ref += 1

    return {
        "total_items": len(items),
        "referenced_items": total_ref,
        "by_block": {b: {"ref": r, "tot": t} for b, (r, t) in by_block.items()},
    }


def main():
    print(f"Sampling {N_SAMPLES} (user→assistant) pairs from vault.db …")
    pairs = sample_pairs(N_SAMPLES)
    print(f"Got {len(pairs)} pairs covering {len(set(p[3] for p in pairs))} projects\n")

    results_by_mode = {m: [] for m in MODES}
    project_dist = defaultdict(int)
    block_agg_by_mode = {m: defaultdict(lambda: [0, 0]) for m in MODES}
    t0 = time.time()

    for i, (prompt, response, cwd, project) in enumerate(pairs, 1):
        items = run_bm25(prompt, cwd)
        project_dist[project] += 1
        for mode in MODES:
            s = score(items, response, mode=mode)
            results_by_mode[mode].append(s)
            for b, d in s["by_block"].items():
                block_agg_by_mode[mode][b][0] += d["ref"]
                block_agg_by_mode[mode][b][1] += d["tot"]
        if i % 5 == 0 or i == len(pairs):
            elapsed = time.time() - t0
            last_sub = results_by_mode["substring"][-1]
            last_hyb = results_by_mode["hybrid"][-1]
            sub_rate = last_sub['referenced_items']/max(1,last_sub['total_items'])
            hyb_rate = last_hyb['referenced_items']/max(1,last_hyb['total_items'])
            print(f"  [{i}/{len(pairs)}] elapsed={elapsed:.1f}s — last: "
                  f"sub={sub_rate:.0%} hyb={hyb_rate:.0%}  project={project[:35]}")

    # Legacy single-mode aggregate for backward compat
    results = results_by_mode["hybrid"]
    block_agg = block_agg_by_mode["hybrid"]
    total_inj = sum(r["total_items"] for r in results)
    total_ref = sum(r["referenced_items"] for r in results)
    overall = total_ref / max(1, total_inj)
    # Per-turn rate (avg of per-turn rates, not just pooled)
    per_turn_rates = [r["referenced_items"] / max(1, r["total_items"]) for r in results if r["total_items"]]
    median = sorted(per_turn_rates)[len(per_turn_rates)//2] if per_turn_rates else 0
    p25 = sorted(per_turn_rates)[len(per_turn_rates)//4] if per_turn_rates else 0
    p75 = sorted(per_turn_rates)[3*len(per_turn_rates)//4] if per_turn_rates else 0
    above_50 = sum(1 for r in per_turn_rates if r >= 0.5) / max(1, len(per_turn_rates))
    above_70 = sum(1 for r in per_turn_rates if r >= 0.7) / max(1, len(per_turn_rates))

    print("\n" + "="*60)
    print(f"BACKTEST RESULTS — n={len(results)} turns")
    print("="*60)

    # T0 vs T1-hybrid comparison table
    print(f"\n{'mode':<14} {'overall':>10}  {'g1':>10}  {'g2_docs':>10}  {'g2_prefetch':>12}")
    print("-" * 62)
    for mode in MODES:
        res = results_by_mode[mode]
        ba = block_agg_by_mode[mode]
        inj = sum(r["total_items"] for r in res)
        ref = sum(r["referenced_items"] for r in res)
        def _rate(b):
            return f"{ba[b][0]/max(1,ba[b][1])*100:.0f}% ({ba[b][0]}/{ba[b][1]})"
        print(f"{mode:<14} {ref/max(1,inj)*100:>9.1f}%  "
              f"{_rate('g1'):>10}  {_rate('g2_docs'):>10}  {_rate('g2_prefetch'):>12}")
    print()

    print(f"POOLED overall utility:  {overall:.1%}   ({total_ref}/{total_inj} items)  [hybrid mode]")
    print(f"Per-turn median:         {median:.1%}")
    print(f"Per-turn p25 / p75:      {p25:.1%} / {p75:.1%}")
    print(f"% turns with ≥50% rate:  {above_50:.0%}")
    print(f"% turns with ≥70% rate (wow gate):  {above_70:.0%}")
    print()
    print("Per-block:")
    for b, (r, t) in sorted(block_agg.items()):
        print(f"  {b:12s}  {r}/{t}  = {r/max(1,t):.1%}")
    print()
    print("Project distribution:")
    for p, n in sorted(project_dist.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {p:45s} {n}")


if __name__ == "__main__":
    main()
