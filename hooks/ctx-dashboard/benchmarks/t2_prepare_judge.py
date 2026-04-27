#!/usr/bin/env python3
"""Prepare T2 judge input: dedup per-pair responses, produce compact per-pair
bundles that the LLM-judge subagent can process in a single pass.

Output schema (per pair):
{
  "pair_id": N,
  "prompt": "user prompt",
  "response": "assistant response (shared across this pair's items)",
  "items": [
    {"idx": 0, "block": "g1", "subject": "...", "tokens": [...]},
    ...
  ]
}

Global idx is assigned sequentially so verdicts merge back cleanly.
"""
import json
import sys
from pathlib import Path

SRC = Path(__file__).parent / "calibration" / "t2_items_v2.json"
OUT = Path(__file__).parent / "calibration" / "t2_judge_input_v2.json"


def main():
    items = json.loads(SRC.read_text())
    by_pair: dict = {}
    for it in items:
        pid = it["pair_id"]
        if pid not in by_pair:
            by_pair[pid] = {
                "pair_id": pid,
                "prompt": it["prompt"][:500],      # truncate long prompts
                "response": it["response"][:4000], # truncate long responses
                "items": [],
            }
        by_pair[pid]["items"].append({
            "idx": len(sum([p["items"] for p in by_pair.values()], [])) - 1,  # filled below
            "block": it["block"],
            "subject": (it.get("subject") or "")[:200],
            "tokens": it.get("tokens", [])[:8],
        })
    # Re-number idx globally
    pairs = sorted(by_pair.values(), key=lambda p: p["pair_id"])
    global_idx = 0
    for p in pairs:
        for it in p["items"]:
            it["idx"] = global_idx
            global_idx += 1

    OUT.write_text(json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")
    total_items = sum(len(p["items"]) for p in pairs)
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {len(pairs)} pairs ({total_items} items) to {OUT}")
    print(f"File size: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
