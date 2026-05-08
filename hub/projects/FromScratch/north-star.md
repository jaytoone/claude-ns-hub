---
category: Research
connections:
- FRWP
current: 82%
deadline: '2026-06-30'
id: FromScratch
layer: 1
links: ''
log:
- date: '2026-05-08'
  text: 'PIVOT to GRPO: LoRA KD v5 scored ~82% on 198Q — BELOW 85% baseline. Root
    cause: self-distillation ceiling (119 traces only from questions already correct).
    Next: GRPO with OR-ensemble teacher signal on failure questions.'
- date: '2026-05-08'
  text: 'Phase 3 v5 DONE: 90% two-pass (18/20, +5pp over baseline). Root cause fixed:
    all 2384 original traces were corrupted garbage. New clean traces (119) from darwin36b
    direct inference. Phase 4 chem/bio trace gen running (33 traces so far).'
- date: '2026-05-07'
  text: Phase 3 v4 DONE (800 steps, darwin36b base, think-tags, LoRA r=32). Greedy
    checkpoint eval running on GPUs 1-5. Baseline 85% confirmed.
- date: '2026-05-07'
  text: 'darwin36b baseline reproduced at 85% (17/20) with two-pass eval. Format fix:
    think tags required. CUDA zombie fix: empty_cache+synchronize.'
- date: '2026-05-06'
  text: 'PIVOT v2: skip FFN merge, go darwin36b direct base. Phase 3 v3 failed (plain
    traces), v4 adds think tags.'
- date: '2026-05-08'
  text: 23d61fc 🎯 Isolation tests DEFINITIVE — Mamba2×GDN interaction is the real
    culprit; a50ba0c 5/5 on DS FINAL REJECT — 4-patch fix insufficient, pivot to mcore
    (+1 more)
metric: GPQA Diamond single-model score
milestones:
- done: true
  text: 'Phase 1: Clean trace gen — 119 traces (fixed corruption: all traces were
    garbage)'
- done: true
  text: 'Phase 2: darwin36b direct base — 85% two-pass (confirmed full 198Q baseline)'
- done: true
  text: 'Phase 3 v5: LoRA KD proxy 90% (18/20) — REVISED: 198Q actual ~82%, below
    baseline. LoRA self-distillation cannot exceed base ceiling.'
- done: false
  text: '[Gate 0] Save failure_indices.json from 198Q run + build 30Q fast-eval harness
    (~30 min eval vs 3h full). Pass if: eval script runs on 30Q in <45 min.'
- done: false
  text: '[Gate 0] GRPO micro-test: 5 failure Qs, 50 rollouts each on GPU 0 (~1h).
    Confirm reward signal converges. Pass if: reward > random baseline on ≥3/5 Qs.'
- done: false
  text: '[Gate 1] GRPO Phase 5a: 30 failure Qs, 200 rollouts, GPUs 0-5 (~3h). Eval
    on those 30Q only. Pass if: +3pp over darwin36b baseline on failure cluster.'
- done: false
  text: '[Gate 2] GRPO Phase 5b: Full GRPO if Gate 1 passes — scale to all ~30 failure
    Qs, 500 rollouts. Full 198Q eval. Pass if: ≥88% (vs 85% baseline).'
- done: false
  text: '[Gate 3] OR-ensemble teacher distillation: use 93.9% ensemble traces on failure
    Qs as GRPO reward seed. Target: ≥90% on 198Q.'
- done: false
  text: 'Final: ≥93% single-model GPQA Diamond (north star: 93.9%)'
name: FromScratch
note: 'PIVOT 2026-05-08: LoRA KD failed (self-distillation ceiling). New plan: GRPO
  with binary correct/incorrect reward on failure questions. Fast-validation gates:
  Gate 0 (2h) → Gate 1 (4h) → Gate 2 (full) only if signal confirmed.'
position_x: 2
status: at-risk
target: 93.9%
unit: '%'
x: 13
y: -130
---

# FromScratch — North Star

## Why this metric
GPQA Diamond is the hardest reasoning benchmark for science PhDs. The north star is matching the OR-ensemble (93.9%) with a single model — proving distillation/merging can capture ensemble-level intelligence. This is the technical moat and content foundation for MOAT.

## Current Plan (v3 — 2026-05-08 GRPO Pivot)

**Fast-Validation Gate Ladder:**
- **[Gate 0 ~2h]** failure_indices.json + 30Q fast-eval harness + GRPO micro-test (5 Qs, 50 rollouts)
- **[Gate 1 ~4h]** GRPO Phase 5a — 30 failure Qs, 200 rollouts, eval on failure cluster only
- **[Gate 2 ~6h]** GRPO Phase 5b — scale if Gate 1 passes (+3pp), full 198Q eval
- **[Gate 3]** OR-ensemble teacher traces as GRPO reward seed → target ≥90%

**Key insight from LoRA failure**: Self-distillation (rejection sampling from base model) cannot exceed the base model's ceiling. GRPO with binary correct/incorrect reward lets the model discover its own path to correct answers on questions it currently fails.

## Why v2 (LoRA KD) failed
119 traces all from questions darwin36b already answered correctly → zero signal on failure questions. 4.2 epochs = memorization, not generalization. 20Q proxy (90%) was statistically meaningless (±13pp CI). Final 198Q: ~82%, below 85% baseline.

## Why v1 failed
Simple 50/50 average of FLA+std-attn architectures → 30% (arch incompatible). Pivoted to jackrong35b direct → 45% (FLA O(T²) eval bottleneck + format collapse).

## Links
- Planner: /home/desk-1/Project/FromScratch/docs/north-star-dashboard.html
- Plan v2: /home/desk-1/Project/FromScratch/docs/20260506-distillation-plan-v2.md