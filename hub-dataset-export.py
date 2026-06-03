#!/usr/bin/env python3
"""M511 P2-E: HuggingFace Datasets compatible export of hub execution traces.

Exports all done stones with exec timestamps as a JSONL dataset.
Output fields match NeurIPS/ICML D&B track requirements.

Run: python3 hub-dataset-export.py [--output dataset.jsonl] [--split]
"""
import json, sys, os, hashlib, random
from pathlib import Path
from datetime import datetime, timezone

NS_EVENTS_DB = Path.home() / ".claude" / "hub" / "ns-events.db"
DEFAULT_OUTPUT = Path.home() / ".claude" / "hub" / "dataset.jsonl"


def load_all_stones():
    """Load all stones from SQLite milestones_store."""
    if not NS_EVENTS_DB.exists():
        print(f"ERROR: {NS_EVENTS_DB} not found", file=sys.stderr)
        sys.exit(1)
    import sqlite3
    conn = sqlite3.connect(str(NS_EVENTS_DB))
    rows = conn.execute(
        "SELECT proj_id, stone_id, data_json, status, done FROM milestones_store"
    ).fetchall()
    conn.close()
    stones = []
    for proj_id, stone_id, data_json, status, done in rows:
        try:
            m = json.loads(data_json)
            m["_proj_id"] = proj_id
            m.setdefault("id", stone_id)
            stones.append(m)
        except Exception:
            pass
    return stones


def duration_sec(start_str, end_str):
    """Compute wall-clock duration in seconds between two ISO timestamps."""
    if not start_str or not end_str:
        return None
    try:
        fmt = "%Y-%m-%dT%H:%M:%S"
        # Handle +09:00 timezone suffix
        start = start_str[:19]
        end = end_str[:19]
        s = datetime.strptime(start, fmt)
        e = datetime.strptime(end, fmt)
        diff = (e - s).total_seconds()
        return round(diff, 1) if diff >= 0 else None
    except Exception:
        return None


def build_record(m):
    """Build a HF Datasets compatible record from a stone dict."""
    proj_id = m.get("_proj_id") or m.get("proj_id", "")
    mid = m.get("id", "")
    text = (m.get("text") or "").strip()
    exec_start = m.get("exec_start")
    exec_end = m.get("exec_end")
    dur = duration_sec(exec_start, exec_end)
    conv = m.get("conversation") or []
    # Count human-AI turns
    conv_turns = len(conv)
    human_turns = sum(1 for c in conv if c.get("role") == "user")
    claude_turns = sum(1 for c in conv if c.get("role") == "claude")

    # Predecessor IDs from parent_id (direct dependency)
    predecessor_ids = [m["parent_id"]] if m.get("parent_id") else []

    record = {
        "id": f"{proj_id}_{mid}",
        "project_id": proj_id,
        "stone_id": mid,
        "text": text,
        "text_length": len(text),
        # Causal graph fields
        "parent_id": m.get("parent_id"),
        "predecessor_ids": predecessor_ids,
        "wave_index": m.get("wave_index"),          # parallel group (0=first wave)
        # Timing fields
        "exec_start": exec_start,
        "exec_end": exec_end,
        "duration_sec": dur,
        # Outcome fields
        "completion_status": m.get("completion_status") or ("success" if m.get("done") else None),
        "failure_reason": m.get("failure_reason"),
        "redo_count": m.get("redo_count") or 0,
        # Token & cost fields
        "total_tokens": m.get("total_tokens"),
        "input_tokens": m.get("input_tokens"),
        "output_tokens": m.get("output_tokens"),
        "cache_creation_tokens": m.get("cache_creation_tokens"),
        "cache_read_tokens": m.get("cache_read_tokens"),
        "cost_usd": m.get("cost_usd"),
        # Execution metadata
        "model_used": m.get("model_used"),
        "agent_ref": m.get("agent_ref"),
        "skill_ref": m.get("skill_ref"),
        # Conversation fields
        "conversation_turns": conv_turns,
        "human_turns": human_turns,
        "claude_turns": claude_turns,
        # Timestamps
        "user_added_at": m.get("user_added_at"),
        "queued_at": m.get("queued_at"),
        "done_at": m.get("done_at"),
        # Data quality: 'exact'=real exec timestamps, 'approximate'=derived from queued_at/done_at
        "exec_timestamp_precision": m.get("exec_timestamp_precision", "exact" if m.get("exec_start") else None),
    }
    return record


def stratified_split(records, train=0.8, val=0.1, test=0.1, seed=42):
    """Project-based stratified train/val/test split."""
    from collections import defaultdict
    rng = random.Random(seed)
    by_proj = defaultdict(list)
    for r in records:
        by_proj[r["project_id"]].append(r)

    train_set, val_set, test_set = [], [], []
    for proj, items in by_proj.items():
        rng.shuffle(items)
        n = len(items)
        n_val = max(1, int(n * val)) if n >= 3 else 0
        n_test = max(1, int(n * test)) if n >= 3 else 0
        n_train = n - n_val - n_test
        train_set += items[:n_train]
        val_set += items[n_train:n_train + n_val]
        test_set += items[n_train + n_val:]
    return train_set, val_set, test_set


def write_jsonl(records, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Written: {path} ({len(records)} records)")


def main():
    args = sys.argv[1:]
    do_split = "--split" in args
    output = DEFAULT_OUTPUT
    for i, a in enumerate(args):
        if a == "--output" and i + 1 < len(args):
            output = Path(args[i + 1])

    stones = load_all_stones()
    print(f"Loaded {len(stones)} stones from SQLite")

    # Filter: done + has exec_start (minimum viable for dataset)
    eligible = [
        m for m in stones
        if (m.get("done") or m.get("status") == "done") and m.get("exec_start")
    ]
    print(f"Eligible (done + exec_start): {len(eligible)}")

    # Also include pending_confirmation with exec times (completed but not user-confirmed)
    partial = [
        m for m in stones
        if m.get("status") == "pending_confirmation" and m.get("exec_start") and m.get("exec_end")
    ]
    print(f"Partial eligible (pending_confirmation + exec times): {len(partial)}")

    all_eligible = eligible + partial
    records = [build_record(m) for m in all_eligible]

    # Stats
    with_dag = sum(1 for r in records if r["parent_id"])
    with_wave = sum(1 for r in records if r["wave_index"] is not None)
    with_dur = sum(1 for r in records if r["duration_sec"] is not None)
    with_conv = sum(1 for r in records if r["conversation_turns"] > 0)

    print(f"\nDataset summary:")
    print(f"  Total records:         {len(records)}")
    print(f"  With parent_id (DAG):  {with_dag}")
    print(f"  With wave_index:       {with_wave}")
    print(f"  With duration:         {with_dur}")
    print(f"  With conversation:     {with_conv}")
    print(f"  Target (NeurIPS D&B):  1,000+")
    print(f"  Gap:                   {max(0, 1000 - len(records))}")

    if not records:
        print("\nWARNING: No records to export. Run hub and complete some stones first.")
        return

    if do_split:
        train, val, test = stratified_split(records)
        base = output.parent / output.stem
        write_jsonl(train, str(base) + "_train.jsonl")
        write_jsonl(val,   str(base) + "_val.jsonl")
        write_jsonl(test,  str(base) + "_test.jsonl")
    else:
        write_jsonl(records, output)

    print(f"\nDone. Export complete.")


if __name__ == "__main__":
    main()
