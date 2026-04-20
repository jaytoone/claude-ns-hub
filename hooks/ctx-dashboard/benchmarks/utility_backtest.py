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
import subprocess
import sqlite3
import time
from pathlib import Path
from collections import defaultdict

VAULT_DB = Path(os.path.expanduser("~/.local/share/claude-vault/vault.db"))
INJ_FILE = Path(os.path.expanduser("~/.claude/last-injection.json"))
BM25_HOOK = Path(os.path.expanduser("~/.claude/hooks/bm25-memory.py"))

N_SAMPLES = 60           # balance between speed (each call ~500ms) and signal
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
        if seen_projects[project] >= 8:   # cap per-project to prevent skew
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


def score(items: list, response: str) -> dict:
    rl = response.lower()
    by_block = defaultdict(lambda: [0, 0])
    total_ref = 0
    for it in items:
        b = it.get("block", "?")
        by_block[b][1] += 1
        hit = any(len(t) >= 4 and t.lower() in rl for t in it.get("tokens", []))
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

    results = []
    project_dist = defaultdict(int)
    block_agg = defaultdict(lambda: [0, 0])
    t0 = time.time()

    for i, (prompt, response, cwd, project) in enumerate(pairs, 1):
        items = run_bm25(prompt, cwd)
        s = score(items, response)
        results.append(s)
        project_dist[project] += 1
        for b, d in s["by_block"].items():
            block_agg[b][0] += d["ref"]
            block_agg[b][1] += d["tot"]
        rate = s["referenced_items"] / max(1, s["total_items"])
        if i % 10 == 0 or i == len(pairs):
            elapsed = time.time() - t0
            print(f"  [{i}/{len(pairs)}] elapsed={elapsed:.1f}s — last: "
                  f"{s['referenced_items']}/{s['total_items']} = {rate:.0%}  "
                  f"project={project[:40]}")

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
    print(f"POOLED overall utility:  {overall:.1%}   ({total_ref}/{total_inj} items)")
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
