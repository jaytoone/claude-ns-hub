#!/usr/bin/env python3
"""Export T2 LLM-judge input items from fresh (user_prompt, assistant_response) pairs.

Complements utility_backtest.py by producing a per-item JSON ready for external
LLM-judge consumption. Skips the first 20 pairs (already in t2_items.json) to
avoid overlap — produces new, disjoint evidence.

Output: calibration/t2_items_v2.json with schema matching existing t2_items.json.
"""
import json
import os
import sqlite3
from pathlib import Path

import utility_backtest as ub   # reuses sample_pairs(), run_bm25(), score()

SKIP_FIRST = 20     # these pair_ids are already judged in t2_items.json
N_NEW_PAIRS = 60    # new disjoint pairs (target ~300–500 items after BM25)
OUT = Path(__file__).parent / "calibration" / "t2_items_v2.json"


def sample_fresh_pairs() -> list:
    """Same SQL as utility_backtest.sample_pairs but returns pairs 21..(20+N)."""
    # We ask for more than we need so we can skip SKIP_FIRST and still fill N_NEW_PAIRS.
    pairs = ub.sample_pairs(SKIP_FIRST + N_NEW_PAIRS + 40)
    return pairs[SKIP_FIRST : SKIP_FIRST + N_NEW_PAIRS]


def main():
    print(f"Sampling {N_NEW_PAIRS} fresh pairs (skipping first {SKIP_FIRST})…")
    pairs = sample_fresh_pairs()
    print(f"Got {len(pairs)} pairs across {len(set(p[3] for p in pairs))} projects\n")

    out = []
    for i, (prompt, response, cwd, project) in enumerate(pairs, start=SKIP_FIRST + 1):
        items = ub.run_bm25(prompt, cwd)
        # Score per-item to preserve sub/sem/hybrid hit flags for later analysis
        rl = response.lower()
        chunk_embs = []
        for chunk in ub._chunk_response(response):
            e = ub._embed(chunk)
            if e: chunk_embs.append(e)
        for it in items:
            sub_hit = any(len(t) >= 4 and t.lower() in rl for t in it.get("tokens", []))
            sem_hit = False
            if chunk_embs:
                item_text = it.get("subject") or " ".join(it.get("tokens", []))
                if item_text:
                    item_emb = ub._embed(item_text)
                    if item_emb:
                        max_sim = max((ub._cosine(item_emb, ce) for ce in chunk_embs), default=0.0)
                        sem_hit = max_sim >= ub.SEMANTIC_THRESHOLD
            out.append({
                "pair_id": i,
                "project": project,
                "prompt": prompt,
                "response": response,
                "block": it.get("block", "?"),
                "tokens": it.get("tokens", []),
                "subject": it.get("subject", ""),
                "sub_hit": sub_hit,
                "sem_hit": sem_hit,
                "hybrid_hit": sub_hit or sem_hit,
            })
        if i % 5 == 0 or (i - SKIP_FIRST) == len(pairs):
            print(f"  [{i - SKIP_FIRST}/{len(pairs)}] items_so_far={len(out)}  project={project[:35]}")

    # Compact per-pair response field — LLM-judge only needs one copy per pair
    # (filesize concern; existing t2_items.json repeats response per item too,
    # so we match that schema for drop-in compatibility).
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(out)} items to {OUT}")
    blocks = {}
    for it in out:
        blocks[it["block"]] = blocks.get(it["block"], 0) + 1
    print(f"By block: {blocks}")
    hybrid_hits = sum(1 for it in out if it["hybrid_hit"])
    print(f"T1 hybrid rate: {hybrid_hits}/{len(out)} = {hybrid_hits/max(1,len(out)):.1%}")


if __name__ == "__main__":
    main()
