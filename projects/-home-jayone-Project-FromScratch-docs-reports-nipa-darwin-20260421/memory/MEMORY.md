# Memory — nipa-darwin-20260421 session

- [/live decision — 2026-04-21 18:15 KST]: Chose Option A (Rogue-v1 + 2 parents 3-arm lm-eval) over Option B (Darwin v7 on 27B pair) and Option C (both). Reason: (1) A directly answers "did Darwin v4 actually beat its parents?" in ~20-30 min wall; (2) B requires 27B × 3 state dicts ≈ 162 GB which overflows single H200 (143 GB VRAM) — needs CPU-offload or multi-GPU sharding, ~5× slower + more complex code; (3) A has higher info/compute ratio and leaves iteration budget for follow-up evolved goals (e.g., cross-scale comparison with 7B Darwin v7 result).
