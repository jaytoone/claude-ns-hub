#!/usr/bin/env python3
"""Merge v2 judge verdicts with original (v1) dataset, compute rate + CI.

Produces:
  - merged_rate = Y / (Y+N) on union dataset  (U excluded from denominator)
  - Wilson 95% CI
  - Agreement between r1 + r2 on v2
  - Per-block rate + CI on v2
  - Comparison vs v1 (169 items, 3 reviewers)
"""
import json
import math
import statistics as stats
from pathlib import Path

BASE = Path(__file__).parent / "calibration"


def wilson(p: float, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def load_verdicts(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {v["idx"]: v["verdict"] for v in data}


def rate_of(verdicts: dict) -> tuple:
    y = sum(1 for v in verdicts.values() if v == "Y")
    n = sum(1 for v in verdicts.values() if v == "N")
    u = sum(1 for v in verdicts.values() if v == "U")
    denom = y + n
    if denom == 0:
        return (0.0, 0.0, 0.0, y, n, u)
    p = y / denom
    lo, hi = wilson(p, denom)
    return (p, lo, hi, y, n, u)


def main():
    items = json.loads((BASE / "t2_items_v2.json").read_text())
    block_of = {it_idx: item["block"] for it_idx, item in enumerate(items)}

    # Load both v2 reviewers
    r1 = load_verdicts(BASE / "t2_verdicts_v2_r1.json")
    r2 = load_verdicts(BASE / "t2_verdicts_v2_r2.json")

    present_r1 = len(r1)
    present_r2 = len(r2)
    print(f"Reviewer coverage:  r1={present_r1}/{len(items)}  r2={present_r2}/{len(items)}\n")

    # Per-reviewer rates
    for label, v in [("r1", r1), ("r2", r2)]:
        if not v:
            continue
        p, lo, hi, y, n, u = rate_of(v)
        print(f"{label}: Y={y} N={n} U={u}  rate={p:.1%}  95% CI [{lo:.1%}, {hi:.1%}]  "
              f"±{(hi-lo)*50:.1f}pp")

    # Agreement (on shared idx)
    shared = set(r1.keys()) & set(r2.keys())
    if shared:
        same = sum(1 for i in shared if r1[i] == r2[i])
        agree = same / len(shared)
        print(f"\nAgreement on {len(shared)} shared items: {agree:.1%}")

    # Majority vote (Y if both reviewers say Y; require both for positive)
    # Use "either Y" as a generous merge, "both Y" as strict
    if shared:
        strict_y = sum(1 for i in shared if r1[i] == "Y" and r2[i] == "Y")
        strict_n = sum(1 for i in shared if r1[i] == "N" and r2[i] == "N")
        mixed = len(shared) - strict_y - strict_n
        strict_p = strict_y / (strict_y + strict_n) if (strict_y + strict_n) else 0
        strict_lo, strict_hi = wilson(strict_p, strict_y + strict_n)
        print(f"\n2-reviewer strict agree (both Y or both N):")
        print(f"  strict-Y={strict_y}  strict-N={strict_n}  mixed/U={mixed}")
        print(f"  rate (strict): {strict_p:.1%}  95% CI [{strict_lo:.1%}, {strict_hi:.1%}]")

    # Per-block on majority verdict
    if shared:
        print("\nPer-block (strict both-agree only):")
        for block in sorted({it["block"] for it in items}):
            block_idxs = [i for i, it in enumerate(items) if it["block"] == block]
            y = sum(1 for i in block_idxs if i in shared and r1[i] == "Y" and r2[i] == "Y")
            n = sum(1 for i in block_idxs if i in shared and r1[i] == "N" and r2[i] == "N")
            denom = y + n
            if denom == 0:
                continue
            p = y / denom
            lo, hi = wilson(p, denom)
            print(f"  {block:12s}  Y={y:3d}  N={n:3d}  rate={p:.1%}  "
                  f"95% CI [{lo:.1%}, {hi:.1%}]  ±{(hi-lo)*50:.1f}pp")

    # Union with v1 dataset (169 items, 3-reviewer majority)
    v1_verdicts = [load_verdicts(BASE / f"t2_verdicts_{k}.json") for k in (1, 2, 3)]
    v1_n = len(v1_verdicts[0]) if v1_verdicts else 0
    if v1_n:
        # Majority Y/N/U from 3 reviewers (tie → U)
        v1_merged = {}
        for i in range(v1_n):
            votes = [v.get(i) for v in v1_verdicts if v]
            y = votes.count("Y"); n_ = votes.count("N"); u = votes.count("U")
            if y > n_ and y > u: v1_merged[i] = "Y"
            elif n_ > y and n_ > u: v1_merged[i] = "N"
            else: v1_merged[i] = "U"
        p, lo, hi, y, n, u = rate_of(v1_merged)
        print(f"\nv1 (169 items, 3-reviewer majority): Y={y} N={n} U={u}  "
              f"rate={p:.1%}  95% CI [{lo:.1%}, {hi:.1%}]")

        # Union: use r1 verdicts on v2, v1 majority on v1 — combined into one pool
        if r1:
            # v1 + v2-r1 (single reviewer union)
            combined_y = y + sum(1 for v in r1.values() if v == "Y")
            combined_n = n + sum(1 for v in r1.values() if v == "N")
            combined_denom = combined_y + combined_n
            cp = combined_y / combined_denom if combined_denom else 0
            clo, chi = wilson(cp, combined_denom)
            print(f"\nUnion (v1 majority + v2 r1): Y={combined_y} N={combined_n}  "
                  f"n={combined_denom}  rate={cp:.1%}  95% CI [{clo:.1%}, {chi:.1%}]  "
                  f"±{(chi-clo)*50:.1f}pp")


if __name__ == "__main__":
    main()
