# T2 LLM-judge Calibration (n=169 items, 20 pairs, 7 projects)

Method: for each injected item, a Claude Code subagent judged whether the
assistant's actual response used/referenced it (Y/N/U). Compared to T1 hybrid
(substring OR semantic ≥0.85). Three parallel subagents, batch 1 re-run once
with tightened prompt for consistency.

## Headline numbers

| Metric | T1 hybrid | LLM judge |
|--------|:---:|:---:|
| Positive rate | 59.8% | **32.5%** |
| Agreement | — | 60.9% |
| Precision (T1→LLM) | — | **44.6%** |
| Recall (LLM→T1) | — | **81.8%** |
| F1 | — | 0.58 |

## Per-block agreement

| Block | n | Agreement | TP | FP | FN | TN |
|-------|---|-----------|----|----|----|----|
| g1 | 72 | 54.2% | 16 | 29 | 4 | 23 |
| g2_docs | 84 | **69.0%** | 27 | 24 | 2 | 31 |
| g2_prefetch | 13 | 46.2% | 2 | 3 | 4 | 4 |

## Interpretation

- **T1 overclaims by ~1.8×**. Raw hybrid score is an upper bound.
- **Recall is strong (82%)** — T1 catches most items the LLM judge flags as used.
- **Precision is weak (45%)** — T1's Y verdicts are only right half the time.
- Calibrated utility estimate: `T1_rate × 0.54`
  - Backtest (N=200): 42.7% × 0.54 ≈ **23%** LLM-adjusted
  - Or, use LLM rate directly: ~**32%**

## Defensible public claim

> CTX-injected context was semantically referenced in **~32%** of assistant
> responses (LLM-judge validated, n=169 items across 7 projects).

## Next-tier improvements (if 32% is too low)

1. Raise semantic threshold 0.85 → 0.88 (reduces FP)
2. Require multi-token substring match (≥2 tokens hit, not 1)
3. AND-gate: require both substring AND semantic for hit (precision ↑, recall ↓)
