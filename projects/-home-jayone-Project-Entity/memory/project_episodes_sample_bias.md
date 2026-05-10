---
name: .omc/episodes.jsonl is biased toward successes
description: Historical live-inf episodes only preserve final-run summaries, not per-iteration failures. Cannot test Mirage failure-category hypotheses without per-iteration failure logging infrastructure.
type: project
originSessionId: 9d7d186b-227d-481d-a1b6-874de9a0cd8d
---
Discovered 2026-04-17 while running Mirage classifier on 5 existing episodes. 2/5 classified (both perception/Output Parser); 3/5 unclassifiable (pure success summaries with no failure vocabulary).

**Why**: The live-inf pipeline writes to `episodes.jsonl` only at the end of a converged run via `omc-episode-memory (save)`. The `key_errors` field captures terminal errors of the final iteration, not per-iteration failures along the convergence path. Any hypothesis that depends on *per-iteration* failure distribution (like the Long-Horizon Mirage plateau-asymmetry test) is untestable from this data source.

**How to apply**:
- Do not propose experiments that depend on per-iteration failure classification against `.omc/episodes.jsonl` unless the sample is first enriched.
- Enrichment path: instrument live-inf to emit `.omc/iter-failures.jsonl` (one row per failed iteration with phase, error, score_delta, context_size).
- When an artifact cites `.omc/episodes.jsonl` as its data source, check whether it needs per-iteration granularity — if yes, flag as blocked on the enrichment work.
- Classifier exists at `scripts/mirage_classifier.py` — ready to use when richer data is available (n≥25 needed for chi-square power).
