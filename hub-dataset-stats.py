#!/usr/bin/env python3
"""M511 P2-D: Dataset scale validator — counts labeled stones across all hub projects.

Run: python3 hub-dataset-stats.py [--json]
"""
import json, sys, os
from pathlib import Path
from collections import defaultdict

PROJECTS_DIR = Path.home() / ".claude" / "hub" / "projects"
NS_EVENTS_DB = Path.home() / ".claude" / "hub" / "ns-events.db"

def load_stones_from_yaml():
    """Fallback: load from north-star.md YAML frontmatter files."""
    stones = []
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        proj_id = proj_dir.name
        ns_file = proj_dir / "north-star.md"
        if not ns_file.exists():
            continue
        try:
            text = ns_file.read_text(encoding="utf-8")
            if "---" not in text:
                continue
            parts = text.split("---", 2)
            if len(parts) < 2:
                continue
            import yaml
            meta = yaml.safe_load(parts[1]) or {}
            for m in meta.get("milestones", []):
                if isinstance(m, dict):
                    m["proj_id"] = proj_id
                    stones.append(m)
        except Exception:
            pass
    return stones

def load_stones_from_sqlite():
    """Primary: load from ns-events.db milestones_store."""
    if not NS_EVENTS_DB.exists():
        return None
    try:
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
                m["proj_id"] = proj_id
                m.setdefault("id", stone_id)
                stones.append(m)
            except Exception:
                pass
        return stones
    except Exception:
        return None

def analyze(stones):
    stats = {
        "total": len(stones),
        "by_status": defaultdict(int),
        "by_proj": defaultdict(int),
        "with_exec_times": 0,
        "with_parent_id": 0,
        "with_wave_index": 0,
        "with_conversation": 0,
        "with_completion_status": 0,
        "with_cost_usd": 0,
        "with_input_tokens": 0,
        "valid_for_dataset": 0,  # done + has exec_start + has parent_id or wave_index
        "done_count": 0,
    }
    for m in stones:
        status = m.get("status") or ("done" if m.get("done") else "pending")
        stats["by_status"][status] += 1
        stats["by_proj"][m.get("proj_id", "?")] += 1
        if m.get("exec_start") and m.get("exec_end"):
            stats["with_exec_times"] += 1
        if m.get("parent_id"):
            stats["with_parent_id"] += 1
        if m.get("wave_index") is not None:
            stats["with_wave_index"] += 1
        if m.get("conversation"):
            stats["with_conversation"] += 1
        if m.get("completion_status"):
            stats["with_completion_status"] += 1
        if m.get("cost_usd"):
            stats["with_cost_usd"] += 1
        if m.get("input_tokens"):
            stats["with_input_tokens"] += 1
        is_done = m.get("done") or status == "done"
        if is_done:
            stats["done_count"] += 1
        if is_done and m.get("exec_start") and (m.get("parent_id") or m.get("wave_index") is not None):
            stats["valid_for_dataset"] += 1
    return stats

def main():
    as_json = "--json" in sys.argv

    stones = load_stones_from_sqlite()
    source = "SQLite"
    if stones is None:
        stones = load_stones_from_yaml()
        source = "YAML"

    stats = analyze(stones)

    if as_json:
        print(json.dumps(stats, indent=2, default=str))
        return

    print(f"\n{'='*55}")
    print(f"  HUB DATASET STATS  (source: {source})")
    print(f"{'='*55}")
    print(f"  Total stones:          {stats['total']:>6}")
    print(f"  Done (completed):      {stats['done_count']:>6}")
    print(f"  With exec timestamps:  {stats['with_exec_times']:>6}")
    print(f"  With parent_id (DAG):  {stats['with_parent_id']:>6}")
    print(f"  With wave_index:       {stats['with_wave_index']:>6}")
    print(f"  With conversation[]:   {stats['with_conversation']:>6}")
    print(f"  With completion_status:{stats['with_completion_status']:>6}")
    print(f"  With cost_usd:         {stats['with_cost_usd']:>6}")
    print(f"  With input_tokens:     {stats['with_input_tokens']:>6}")
    print(f"")
    print(f"  *** VALID FOR DATASET: {stats['valid_for_dataset']:>5} ***")
    print(f"      (done + exec times + DAG/wave label)")
    print(f"      NeurIPS D&B target: 1,000+")
    gap = max(0, 1000 - stats['valid_for_dataset'])
    pct = min(100, stats['valid_for_dataset'] / 10)
    print(f"      Gap to target:  {gap:>5}  ({pct:.1f}% complete)")
    print(f"")
    print(f"  By project:")
    for proj, cnt in sorted(stats['by_proj'].items(), key=lambda x: -x[1])[:10]:
        print(f"    {proj:<20} {cnt:>5}")
    print(f"")
    print(f"  By status:")
    for s, cnt in sorted(stats['by_status'].items(), key=lambda x: -x[1]):
        print(f"    {s:<25} {cnt:>5}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
