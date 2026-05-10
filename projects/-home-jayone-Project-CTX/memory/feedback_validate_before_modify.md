---
name: Validate empirically before stacking code changes
description: User prefers measuring impact of each code change against benchmarks before adding more changes; no speculative multi-step rollouts
type: feedback
originSessionId: 801e3a8c-60aa-4bce-84ef-ad0be5dbeffe
---
Rule: when making performance-oriented changes (retrieval, hooks, algorithms), validate the effect of change N against the relevant benchmark BEFORE implementing change N+1.

**Why:** On 2026-04-17 during live-inf Tier 1 rollout (T1-A, T1-B, T1-C from SOTA research), user interrupted after T1-A was made and T1-C was being added — requested "validate the effect before modify the codes." User wants empirical evidence per change, not stacked edits claimed to work in theory.

**How to apply:** After any substantive change to retrieval/ranking/scoring code (e.g., `search_graph_for_prompt`, `_semantic_rerank`, BM25 layers in hooks):
1. Run the corresponding benchmark (G1: `benchmarks/eval/g1_fair_eval.py`; G2 external: `benchmarks/eval/doc_retrieval_eval_v2.py` or equivalent)
2. Report delta vs baseline (e.g., FastAPI R@5: 0.40 → X.XX)
3. If regression → revert or diagnose before next change
4. Only then proceed to the next planned change

Applies especially to live-inf multi-iter plans: treat each Tier item as its own iter-with-benchmark, not as a batch.
