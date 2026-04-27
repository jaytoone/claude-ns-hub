# CTX Utility Calibration — T1/T2 with 95% CI (updated 2026-04-21 v3)

## Headline numbers

| Dataset | Method | N (items) | Rate | 95% CI (Wilson) | ± |
|---|---|:---:|:---:|:---:|:---:|
| **v2** (60 pairs, 2 reviewers, 2026-04-21) | T1 hybrid | 579 | **43.5%** | [39.5%, 47.6%] | ±4.0pp |
| **v2** (strict 2-reviewer agree) | T2 LLM-judge | 551 (28 mixed excluded) | **6.5%** | [4.8%, 8.9%] | ±2.1pp |
| v2 reviewer #1 | T2 LLM-judge | 579 | 9.3% | [7.2%, 12.0%] | ±2.4pp |
| v2 reviewer #2 | T2 LLM-judge | 579 | 7.8% | [5.9%, 10.3%] | ±2.2pp |
| v2 reviewer agreement | — | 579 | **95.2%** | — | — |
| v1 (20 pairs, 3 reviewers, 2026-04) | T1 hybrid | 169 | 59.8% | — | — |
| v1 pooled (3 reviewers × 56 items) | T2 LLM-judge | 169 | 32.5% | [25.9%, 39.9%] | ±7.0pp |
| **Aggregated** (v1 majority + v2 r1, all items) | T2 LLM-judge | 635 | **10.1%** | [8.0%, 12.7%] | ±2.3pp |

N=200 backtest full hybrid rate: **48.9% ±2.6pp** (1471 items — per §headline in prior v2 report).

## Critical finding: v2 rate is much lower than v1

**v1 reported 32.5%; v2 reports 6.5–9.3%.** Gap is ~25pp. Candidate explanations:

1. **Sampling bias in v1** — v1's 20 pairs were manually selected from recent vault.db activity. v2 used deterministic sequential sampling (pairs 21–80 from the same query). v2 likely reflects the underlying distribution more honestly.
2. **Response-type distribution** — of v2's 60 pairs, 40 are prose, 18 mixed prose+tool_use, 2 pure tool-heavy. Both judges flagged that tool_use pairs make textual reference nearly impossible; pure-prose pairs also scored lower than v1.
3. **Judge stringency shift** — v2 judges were given explicit "don't anchor to 32.5%" guidance, which may have tightened scoring.
4. **Harder topics** — v2 pairs include more CTX/infrastructure debugging, which surfaces g2_prefetch items (code symbols) that rarely appear in prose responses.

## Per-block (v2, strict 2-reviewer agreement)

| Block | n | Rate | 95% CI | ± |
|-------|:---:|:---:|:---:|:---:|
| g1 (decisions) | 207 | 7.2% | [4.4%, 11.6%] | ±3.6pp |
| g2_docs | 260 | 6.9% | [4.4%, 10.7%] | ±3.1pp |
| g2_prefetch | 84 | 3.6% | [1.2%, 10.0%] | ±4.4pp |

## What this means for the utility claim

The **9.3% upper-bound single-reviewer rate** (not the 32.5% from v1) is the defensible public number.

Even charitably, the aggregated union (v1 majority + v2 r1, N=635) lands at **10.1% ±2.3pp**. The prior 32.5% figure cannot be defended without caveating the 20-pair selection bias.

**Revised public claim**:

> CTX surfaced context that Claude's response textually referenced in **~10%** of injected items
> (95% CI [8.0%, 12.7%], N=635 items, 2 reviewer batches, 2026-04).
> Substring+semantic T1 upper bound: 48.9% (N=1471). The gap (10% vs 49%) is
> calibrator stringency + tool_use responses where CTX may still have influenced
> tool choice but cannot be verified textually.

## Honest limitations (unchanged)

1. **Single user** — all N=635 sessions are the founder's. Generalization unmeasured.
2. **Textual-reference blind spot** — ~33% of v2 pairs (18/60) are mixed prose+tool_use. When the assistant takes a tool action informed by CTX but doesn't cite it in prose, T2 scores N. Real "value delivered" likely exceeds textual reference rate, but the gap is unquantified.
3. **Sampling discrepancy** — v1→v2 rate drop from 32.5% to 9.3% suggests the earlier figure was overfit to a hand-picked sample. This is exactly the sort of finding that honest validation surfaces.
4. **Majority-vote on v1 yields Y=10/56** — the 32.5% in prior reports is **pooled across 3 reviewers × partially-overlapping subsets**, not a strict majority. A proper 3-of-3 majority on v1 gives 17.9% ([10%, 29.8%]).

## What should happen next (iter 3+)

1. **Tool-use-aware utility metric** — extend `utility-rate.py` to score tool_use parameter matches (e.g., did the assistant's `Read(X)` target match a CTX-surfaced file?). This closes the "textual blind spot."
2. **Multi-user cohort** — still P0. Fixed textual bias doesn't fix generalization.
3. **Stratify by response type** before aggregating — report prose / mixed / tool-heavy rates separately. Current pooled aggregate hides structural differences.

---

*Data files*:
- `t2_items.json` (v1, 169 items from 20 pairs)
- `t2_verdicts_{1,2,3}.json` (v1, 3 reviewers)
- `t2_items_v2.json` (v2, 579 items from 60 disjoint pairs)
- `t2_verdicts_v2_r{1,2}.json` (v2, 2 reviewers)
- `t2_judge_input_v2.json` (compact bundle used by reviewers)
- Export script: `t2_export.py` — samples pairs 21..80
- Analysis script: `t2_analyze.py` — Wilson CI + agreement + per-block
